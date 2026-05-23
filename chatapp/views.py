from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from chatapp.models import ChatMessage
from chatapp.services import (
    generate_assistant_reply,
    get_predict_help_reply,
    get_quick_reply,
    load_tips,
)
from chatapp.utils import get_logged_in_user, user_login_required

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
            assistant_text = get_predict_help_reply(request, tips)
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
