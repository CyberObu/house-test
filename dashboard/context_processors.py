from properties.models import Property
from accounts.models import AgentVerification, UserReport
from dashboard.models import Payment


def admin_counts(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return {}
    return {
        'admin_pending_listings_count': Property.objects.filter(approval_status='pending').count(),
        'admin_pending_verifs_count': AgentVerification.objects.filter(status='pending').count(),
        'admin_pending_payments_count': Payment.objects.filter(status='pending').count(),
        'admin_open_reports_count': UserReport.objects.filter(is_resolved=False).count(),
    }
