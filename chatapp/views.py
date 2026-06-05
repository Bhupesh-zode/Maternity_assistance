from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Max, Q

from chatapp.models import ChatMessage, SupportMessage
from chatapp.services import (
    generate_assistant_reply,
    get_predict_guidance_reply,
    get_quick_reply,
    load_tips,
)
from chatapp.utils import (
    admin_login_required,
    get_logged_in_user,
    user_login_required,
    validate_support_attachment,
)
from mainapp.models import mainModel

MAX_HISTORY = 50


def _get_history(user):
    return list(
        ChatMessage.objects.filter(user_sno=user.sno).order_by('-created_at')[:MAX_HISTORY]
    )[::-1]


@user_login_required
@require_http_methods(['GET', 'POST'])
def user_chat(request):
    user = get_logged_in_user(request)
    tips = load_tips()

    if request.method == 'POST':
        action = request.POST.get('action', 'send')

        if action == 'clear':
            ChatMessage.objects.filter(user_sno=user.sno).delete()
            messages.info(request, 'Chat history cleared.')
            return redirect('user_chat')

        user_text = (request.POST.get('message') or '').strip()
        quick_key = request.POST.get('quick', '').strip()

        if quick_key and not user_text:
            user_text = f'[Quick topic: {quick_key.replace("_", " ")}]'

        if quick_key == 'predict_help':
            assistant_text = get_predict_guidance_reply(user, request, tips)
        elif quick_key:
            assistant_text = get_quick_reply(quick_key, tips)
            if not assistant_text:
                assistant_text = generate_assistant_reply(
                    user, user_text or quick_key, _get_history(user), request
                )
        else:
            if not user_text:
                messages.warning(request, 'Please enter a message.')
                return redirect('user_chat')
            recent = _get_history(user)
            assistant_text = generate_assistant_reply(user, user_text, recent, request)

        ChatMessage.objects.create(
            user_sno=user.sno, role=ChatMessage.ROLE_USER, content=user_text or quick_key
        )
        ChatMessage.objects.create(
            user_sno=user.sno, role=ChatMessage.ROLE_ASSISTANT, content=assistant_text
        )
        return redirect('user_chat')

    history = _get_history(user)
    context = {
        'user': user,
        'chat_messages': history,
        'disclaimer': (
            'This assistant provides general information only, not medical advice. '
            'Always consult your doctor or emergency services for urgent concerns.'
        ),
    }
    return render(request, 'chatapp/user-chat.html', context)


MAX_SUPPORT_HISTORY = 200


def _get_support_thread(user_sno):
    return list(
        SupportMessage.objects.filter(user_sno=user_sno).order_by('-created_at')[:MAX_SUPPORT_HISTORY]
    )[::-1]


def _mark_support_read(user_sno, sender):
    SupportMessage.objects.filter(
        user_sno=user_sno, sender=sender, is_read=False
    ).update(is_read=True)


def _create_support_message(request, user_sno, sender, redirect_name, redirect_kwargs=None):
    text = (request.POST.get('message') or '').strip()
    uploaded_file = request.FILES.get('attachment')

    if not text and not uploaded_file:
        messages.warning(request, 'Please enter a message or attach a file.')
        return redirect(redirect_name, **(redirect_kwargs or {}))

    if uploaded_file:
        error = validate_support_attachment(uploaded_file)
        if error:
            messages.warning(request, error)
            return redirect(redirect_name, **(redirect_kwargs or {}))

    SupportMessage.objects.create(
        user_sno=user_sno,
        sender=sender,
        content=text,
        attachment=uploaded_file if uploaded_file else None,
    )
    if sender == SupportMessage.SENDER_ADMIN:
        from userapp.notifications import notify_user
        preview = text[:80] if text else 'New file from admin'
        notify_user(
            user_sno,
            'message',
            'New reply from admin',
            preview,
            '/user-messages',
        )
    return redirect(redirect_name, **(redirect_kwargs or {}))


@user_login_required
@require_http_methods(['GET', 'POST'])
def user_support(request):
    user = get_logged_in_user(request)

    if request.method == 'POST':
        return _create_support_message(
            request,
            user.sno,
            SupportMessage.SENDER_USER,
            'user_support',
        )

    _mark_support_read(user.sno, SupportMessage.SENDER_ADMIN)
    context = {
        'user': user,
        'support_messages': _get_support_thread(user.sno),
    }
    return render(request, 'chatapp/user-messages.html', context)


@admin_login_required
def admin_support_inbox(request):
    thread_stats = (
        SupportMessage.objects.values('user_sno')
        .annotate(
            last_at=Max('created_at'),
            unread=Count('id', filter=Q(sender=SupportMessage.SENDER_USER, is_read=False)),
        )
        .order_by('-last_at')
    )

    conversations = []
    for row in thread_stats:
        try:
            user = mainModel.objects.get(sno=row['user_sno'])
        except mainModel.DoesNotExist:
            continue
        last_msg = (
            SupportMessage.objects.filter(user_sno=row['user_sno'])
            .order_by('-created_at')
            .first()
        )
        conversations.append({
            'user': user,
            'last_message': last_msg,
            'last_at': row['last_at'],
            'unread': row['unread'],
        })

    return render(request, 'adminapp/admin-messages.html', {
        'conversations': conversations,
    })


@admin_login_required
@require_http_methods(['GET', 'POST'])
def admin_support_thread(request, user_sno):
    user = get_object_or_404(mainModel, sno=user_sno)

    if request.method == 'POST':
        return _create_support_message(
            request,
            user.sno,
            SupportMessage.SENDER_ADMIN,
            'admin_support_thread',
            {'user_sno': user_sno},
        )

    _mark_support_read(user.sno, SupportMessage.SENDER_USER)
    context = {
        'thread_user': user,
        'support_messages': _get_support_thread(user.sno),
    }
    return render(request, 'adminapp/admin-messages-thread.html', context)
