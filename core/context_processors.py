from properties.models import PropertyType, PropertyInquiry, TourRequest


def site_context(request):
    ctx = {
        'site_name': 'NyumbaHub',
        'property_types': PropertyType.objects.all(),
    }
    if request.user.is_authenticated:
        ctx['inquiries_unread_count'] = PropertyInquiry.objects.filter(
            property__owner=request.user, is_read=False
        ).count()
        ctx['tours_pending_count'] = TourRequest.objects.filter(
            property__owner=request.user, status='pending'
        ).count()
        from messaging.models import Message
        ctx['messages_unread_count'] = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False,
        ).exclude(sender=request.user).count()
    return ctx
