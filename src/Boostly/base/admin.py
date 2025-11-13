from django.contrib import admin
from .models import CreditBalance, Recognition, Endorsement, Redemption


@admin.register(CreditBalance)
class CreditBalanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'available_credits', 'monthly_sent', 'total_received', 'last_reset_date')
    list_filter = ('last_reset_date',)
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('total_received', 'last_reset_date')


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ('from_student', 'to_student', 'credits', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('from_student__username', 'to_student__username', 'message')
    readonly_fields = ('created_at',)


@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('endorser', 'recognition', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('endorser__username',)
    readonly_fields = ('created_at',)


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('student', 'credits_redeemed', 'rupees_value', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__username',)
    readonly_fields = ('rupees_value', 'created_at', 'completed_at')
