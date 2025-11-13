from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
import calendar


class CreditBalance(models.Model):
    """
    Tracks student's monthly credit balance and sending limits.
    Credits reset every month with optional carry-forward of up to 50 credits.
    """
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credit_balance')
    available_credits = models.IntegerField(default=100)
    monthly_sent = models.IntegerField(default=0)  # Amount sent this month
    last_reset_date = models.DateField(auto_now_add=True)
    total_received = models.IntegerField(default=0)  # Total credits ever received
    
    class Meta:
        verbose_name_plural = "Credit Balances"
    
    def __str__(self):
        return f"{self.student.username} - Available: {self.available_credits}, Sent: {self.monthly_sent}"
    
    def get_monthly_sending_limit(self):
        """Returns the remaining monthly sending limit (100 per month)"""
        return max(0, 100 - self.monthly_sent)
    
    def can_send_credits(self, amount):
        """Check if student can send the specified amount"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if amount > self.available_credits:
            raise ValidationError(f"Insufficient balance. You have {self.available_credits} credits")
        if amount > self.get_monthly_sending_limit():
            raise ValidationError(f"Monthly limit exceeded. You can send {self.get_monthly_sending_limit()} more credits")
        return True


class Recognition(models.Model):
    """
    Core recognition model - one student recognizing another.
    """
    from_student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recognitions_given')
    to_student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recognitions_received')
    credits = models.IntegerField()
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_student.username} -> {self.to_student.username}: {self.credits} credits"
    
    def clean(self):
        """Validate recognition rules"""
        if self.from_student == self.to_student:
            raise ValidationError("You cannot recognize yourself")
        
        from_balance = CreditBalance.objects.get_or_create(student=self.from_student)[0]
        if self.credits > from_balance.available_credits:
            raise ValidationError(f"Insufficient balance. You have {from_balance.available_credits} credits")
        
        if self.credits > from_balance.get_monthly_sending_limit():
            raise ValidationError(f"Monthly limit exceeded. Limit: {from_balance.get_monthly_sending_limit()} credits")
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Deduct credits from sender
        from_balance = CreditBalance.objects.get_or_create(student=self.from_student)[0]
        from_balance.available_credits -= self.credits
        from_balance.monthly_sent += self.credits
        from_balance.save()
        
        # Add credits to receiver
        to_balance = CreditBalance.objects.get_or_create(student=self.to_student)[0]
        to_balance.available_credits += self.credits
        to_balance.total_received += self.credits
        to_balance.save()
        
        super().save(*args, **kwargs)


class Endorsement(models.Model):
    """
    Endorsement of a recognition entry (like/cheer).
    Each endorser can only endorse a recognition once.
    Endorsements don't affect credit balances.
    """
    recognition = models.ForeignKey(Recognition, on_delete=models.CASCADE, related_name='endorsements')
    endorser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='endorsements_given')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recognition', 'endorser']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.endorser.username} endorsed {self.recognition}"
    
    def clean(self):
        """Ensure endorser is not the original recognizer or recipient"""
        if self.endorser == self.recognition.from_student:
            raise ValidationError("You cannot endorse your own recognition")
        # Allow recipient to endorse, or remove this line if you want to prevent it


class Redemption(models.Model):
    """
    Credit redemption model - converts credits to vouchers at ₹5 per credit.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions')
    credits_redeemed = models.IntegerField()
    rupees_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.credits_redeemed} credits -> ₹{self.rupees_value}"
    
    def clean(self):
        """Validate redemption rules"""
        balance = CreditBalance.objects.get_or_create(student=self.student)[0]
        if self.credits_redeemed <= 0:
            raise ValidationError("Credits must be greater than 0")
        if self.credits_redeemed > balance.available_credits:
            raise ValidationError(f"Insufficient balance. You have {balance.available_credits} credits")
    
    def save(self, *args, **kwargs):
        self.clean()
        
        # Set rupees value (₹5 per credit)
        self.rupees_value = self.credits_redeemed * 5
        
        # Deduct credits from balance if status is completed
        if self.status == 'completed' and not self.completed_at:
            balance = CreditBalance.objects.get_or_create(student=self.student)[0]
            balance.available_credits -= self.credits_redeemed
            balance.save()
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
