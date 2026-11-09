from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Conversation, Message

User = get_user_model()


@login_required
def inbox(request):
    conversations = (
        request.user.conversations
        .prefetch_related('participants', 'messages__sender')
        .select_related('property')
        .all()
    )
    enriched = [
        {
            'convo': c,
            'other': c.get_other_participant(request.user),
            'last_message': c.get_last_message(),
            'unread': c.unread_count(request.user),
        }
        for c in conversations
    ]
    return render(request, 'messaging/inbox.html', {'conversations': enriched})


@login_required
def start_conversation(request, user_id, property_id=None):
    other_user = get_object_or_404(User, pk=user_id)
    if other_user == request.user:
        return redirect('messaging:inbox')

    prop = None
    if property_id:
        from properties.models import Property
        prop = get_object_or_404(Property, pk=property_id)

    # Find existing conversation between these two users (for this property if given)
    existing = None
    qs = request.user.conversations.filter(participants=other_user)
    if prop:
        qs = qs.filter(property=prop)
    existing = qs.first()

    if existing:
        return redirect('messaging:conversation_detail', conversation_id=existing.pk)

    # Create new conversation
    convo = Conversation.objects.create(property=prop)
    convo.participants.set([request.user, other_user])
    return redirect('messaging:conversation_detail', conversation_id=convo.pk)


@login_required
def conversation_detail(request, conversation_id):
    convo = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'messages__sender'),
        pk=conversation_id,
        participants=request.user,
    )
    # Mark all messages in this conversation as read (messages not from me)
    convo.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages_qs = convo.messages.select_related('sender').order_by('created_at')
    other_user = convo.get_other_participant(request.user)

    return render(request, 'messaging/conversation.html', {
        'conversation': convo,
        'messages': messages_qs,
        'other_user': other_user,
    })


@login_required
@require_POST
def send_message(request, conversation_id):
    convo = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
    content = request.POST.get('content', '').strip()
    if content:
        msg = Message.objects.create(
            conversation=convo,
            sender=request.user,
            content=content,
        )
        convo.updated_at = timezone.now()
        convo.save(update_fields=['updated_at'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': msg.pk,
                'content': msg.content,
                'sender_id': msg.sender_id,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
                'created_at': msg.created_at.strftime('%H:%M'),
                'is_mine': True,
            })

    return redirect('messaging:conversation_detail', conversation_id=convo.pk)


@login_required
def poll_messages(request, conversation_id):
    convo = get_object_or_404(Conversation, pk=conversation_id, participants=request.user)
    after_id = int(request.GET.get('after', 0))

    new_msgs = convo.messages.filter(pk__gt=after_id).select_related('sender').order_by('created_at')
    # Mark incoming messages as read
    new_msgs.exclude(sender=request.user).update(is_read=True)

    data = []
    for msg in new_msgs:
        data.append({
            'id': msg.pk,
            'content': msg.content,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.get_full_name() or msg.sender.username,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_mine': msg.sender_id == request.user.pk,
        })
    return JsonResponse({'messages': data})
