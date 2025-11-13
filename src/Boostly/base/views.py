from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import CreditBalance, Recognition, Endorsement, Redemption
from .forms import RecognitionForm, RedemptionForm
from datetime import datetime


@login_required
def dashboard(request):
    """Main dashboard showing student's credit balance and activity"""
    try:
        balance = CreditBalance.objects.get(student=request.user)
    except CreditBalance.DoesNotExist:
        balance = CreditBalance.objects.create(student=request.user)
    
    # Get recent recognitions given
    recognitions_given = Recognition.objects.filter(from_student=request.user)[:10]
    
    # Get recent recognitions received
    recognitions_received = Recognition.objects.filter(to_student=request.user)[:10]
    
    context = {
        'balance': balance,
        'recognitions_given': recognitions_given,
        'recognitions_received': recognitions_received,
        'monthly_limit_remaining': balance.get_monthly_sending_limit(),
    }
    return render(request, 'base/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def recognize(request):
    """Create a new recognition entry"""
    if request.method == 'POST':
        form = RecognitionForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # Get form data
                to_student = form.cleaned_data.get('to_student')
                credits = form.cleaned_data.get('credits')
                message = form.cleaned_data.get('message')
                
                # Create recognition with from_student
                recognition = Recognition(
                    from_student=request.user,
                    to_student=to_student,
                    credits=credits,
                    message=message
                )
                recognition.save()
                messages.success(request, f'Recognition sent! {recognition.credits} credits transferred.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RecognitionForm(user=request.user)
    
    # Get list of students (exclude current user)
    students = User.objects.exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    context = {
        'form': form,
        'students': students,
    }
    return render(request, 'base/recognize.html', context)


@login_required
@require_http_methods(["POST"])
def endorse_recognition(request, recognition_id):
    """Endorse an existing recognition"""
    recognition = get_object_or_404(Recognition, id=recognition_id)
    
    try:
        endorsement, created = Endorsement.objects.get_or_create(
            recognition=recognition,
            endorser=request.user
        )
        if created:
            messages.success(request, 'Recognition endorsed!')
        else:
            messages.info(request, 'You have already endorsed this recognition.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('recognition_detail', recognition_id=recognition_id)


@login_required
def recognition_detail(request, recognition_id):
    """View details of a specific recognition"""
    recognition = get_object_or_404(Recognition, id=recognition_id)
    endorsements = recognition.endorsements.all()
    user_endorsed = endorsements.filter(endorser=request.user).exists()
    
    context = {
        'recognition': recognition,
        'endorsements': endorsements,
        'user_endorsed': user_endorsed,
        'endorsement_count': endorsements.count(),
    }
    return render(request, 'base/recognition_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def redeem_credits(request):
    """Redeem credits for vouchers"""
    try:
        balance = CreditBalance.objects.get(student=request.user)
    except CreditBalance.DoesNotExist:
        balance = CreditBalance.objects.create(student=request.user)
    
    if request.method == 'POST':
        form = RedemptionForm(request.POST, balance=balance)
        if form.is_valid():
            try:
                redemption = form.save(commit=False)
                redemption.student = request.user
                redemption.status = 'completed'
                redemption.save()
                messages.success(
                    request,
                    f'Success! {redemption.credits_redeemed} credits redeemed for ₹{redemption.rupees_value}'
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RedemptionForm(balance=balance)
    
    # Get redemption history
    redemptions = Redemption.objects.filter(student=request.user)
    
    context = {
        'form': form,
        'balance': balance,
        'redemptions': redemptions,
    }
    return render(request, 'base/redeem.html', context)


@login_required
def leaderboard(request):
    """Display leaderboard of top recipients"""
    from django.db.models import Count, Sum, Q
    
    # Get all users
    all_users = User.objects.filter(is_active=True).order_by('-id')
    
    leaderboard_data = []
    
    for student in all_users:
        # Count recognitions received
        recognition_count = Recognition.objects.filter(to_student=student).count()
        
        # Sum credits received
        credits_received = Recognition.objects.filter(to_student=student).aggregate(
            total=Sum('credits')
        )['total'] or 0
        
        # Count total endorsements on recognitions received by this student
        endorsement_count = Endorsement.objects.filter(
            recognition__to_student=student
        ).count()
        
        # Only include students who have some activity
        if credits_received > 0 or recognition_count > 0 or endorsement_count > 0:
            leaderboard_data.append({
                'student': student,
                'credits_received': credits_received,
                'recognition_count': recognition_count,
                'endorsement_count': endorsement_count,
            })
    
    # Sort by credits received (descending), then by student ID (ascending)
    leaderboard_data.sort(
        key=lambda x: (-x['credits_received'], x['student'].id)
    )
    
    context = {
        'leaderboard': leaderboard_data,
    }
    return render(request, 'base/leaderboard.html', context)


def home(request):
    """Home page - redirect to dashboard if logged in"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'base/home.html')
