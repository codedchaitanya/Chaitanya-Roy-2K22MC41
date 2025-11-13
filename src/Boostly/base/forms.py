from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Recognition, Redemption, CreditBalance


class RecognitionForm(forms.ModelForm):
    to_student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Recognize Student'
    )
    
    class Meta:
        model = Recognition
        fields = ['to_student', 'credits', 'message']
        widgets = {
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'type': 'number'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What did this student do well?'
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Exclude current user from dropdown
        if user:
            self.fields['to_student'].queryset = User.objects.exclude(
                id=user.id
            ).order_by('first_name', 'last_name')
    
    def clean(self):
        cleaned_data = super().clean()
        credits = cleaned_data.get('credits')
        to_student = cleaned_data.get('to_student')
        
        if not credits or not to_student:
            return cleaned_data
        
        # Get or create sender's balance
        balance = CreditBalance.objects.get_or_create(student=self.user)[0]
        
        # Check if sender can send this amount
        if credits > balance.available_credits:
            raise ValidationError(
                f'Insufficient balance. You have {balance.available_credits} credits available.'
            )
        
        if credits > balance.get_monthly_sending_limit():
            raise ValidationError(
                f'Monthly limit exceeded. You can send {balance.get_monthly_sending_limit()} more credits this month.'
            )
        
        if credits <= 0:
            raise ValidationError('Credits must be greater than 0.')
        
        if credits > 100:
            raise ValidationError('Cannot transfer more than 100 credits at once.')
        
        return cleaned_data


class RedemptionForm(forms.ModelForm):
    class Meta:
        model = Redemption
        fields = ['credits_redeemed']
        widgets = {
            'credits_redeemed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'type': 'number',
                'placeholder': 'Enter number of credits to redeem'
            }),
        }
    
    def __init__(self, *args, balance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.balance = balance
    
    def clean(self):
        cleaned_data = super().clean()
        credits = cleaned_data.get('credits_redeemed')
        
        if not credits:
            return cleaned_data
        
        if credits <= 0:
            raise ValidationError('Credits must be greater than 0.')
        
        if self.balance and credits > self.balance.available_credits:
            raise ValidationError(
                f'Insufficient balance. You have {self.balance.available_credits} credits available.'
            )
        
        return cleaned_data
