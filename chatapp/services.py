import json
import os
import re
from pathlib import Path

from django.conf import settings

EMERGENCY_PATTERNS = [
    r'\bheavy bleeding\b',
    r'\bsevere pain\b',
    r'\bcan\'?t breathe\b',
    r'\bpassed out\b',
    r'\bfainted\b',
    r'\bno baby movement\b',
    r'\bbaby not moving\b',
    r'\breduced movement\b',
    r'\bvision changes\b',
    r'\bsuicid',
    r'\bharm myself\b',
    r'\bemergency\b',
    r'\b911\b',
    r'\b108\b',
    r'\b102\b',
]

TIPS_PATH = Path(__file__).resolve().parent / 'data' / 'pregnancy_tips.json'

SYSTEM_PROMPT = """You are a supportive pregnancy wellness assistant for the Maternity Assistance web app.

Rules (always follow):
- Give general wellness information only. You are NOT a doctor.
- Never diagnose conditions, prescribe medicines, or tell the user to ignore medical advice.
- For emergencies (bleeding, severe pain, no fetal movement, etc.), tell them to contact emergency services or their doctor immediately.
- Keep replies concise: 2–5 short paragraphs or bullet points.
- Encourage regular antenatal checkups.
- If asked about the app's ML prediction, say it is a guide only and clinical decisions belong to their healthcare provider.
- Be warm and respectful. User's name: {user_name}.
"""


def load_tips():
    with TIPS_PATH.open(encoding='utf-8') as f:
        return json.load(f)


def check_emergency(text):
    lowered = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, lowered):
            return (
                'This may be urgent. Please contact your doctor, maternity unit, or '
                'local emergency services right away. Do not wait for chat advice in an emergency.'
            )
    return None


def _format_bullets(items):
    return '\n'.join(f'• {item}' for item in items)


def get_last_prediction(request):
    if request is None:
        return None
    data = request.session.get('last_prediction')
    if not isinstance(data, dict):
        return None
    mode = (data.get('mode') or '').strip()
    if not mode:
        return None
    return data


def get_predict_help_reply(request, tips):
    last = get_last_prediction(request)
    if last:
        template = tips['app_help'].get(
            'predict_after',
            'Your latest ML suggestion: {mode}. Discuss this with your doctor.',
        )
        return template.format(mode=last['mode'])
    return tips['app_help']['predict']


def _predict_keywords_in(text):
    lowered = text.lower()
    return any(
        w in lowered
        for w in (
            'predict',
            'prediction',
            'delivery mode',
            'cesarean',
            'c-section',
            'normal delivery',
            'childbirth result',
            'my result',
            'already filled',
            'already submitted',
            'filled the form',
            'submitted the form',
        )
    )


def match_rule_reply(text, tips, request=None):
    lowered = text.lower()

    if any(w in lowered for w in ('red flag', 'warning sign', 'danger', 'emergency sign')):
        return 'Seek care immediately if you notice:\n' + _format_bullets(tips['red_flags'])

    if any(w in lowered for w in ('trimester 1', 'first trimester', 'early pregnancy', '1st trimester')):
        return 'First trimester tips:\n' + _format_bullets(tips['trimester_1'])

    if any(w in lowered for w in ('trimester 2', 'second trimester', '2nd trimester')):
        return 'Second trimester tips:\n' + _format_bullets(tips['trimester_2'])

    if any(w in lowered for w in ('trimester 3', 'third trimester', 'late pregnancy', '3rd trimester')):
        return 'Third trimester tips:\n' + _format_bullets(tips['trimester_3'])

    if _predict_keywords_in(text):
        return get_predict_help_reply(request, tips)

    if any(w in lowered for w in ('profile', 'update photo', 'my account')):
        return tips['app_help']['profile']

    if any(w in lowered for w in ('register', 'sign up', 'signup')):
        return tips['app_help']['register']

    if any(w in lowered for w in ('pending', 'approval', 'cannot login', "can't login")):
        return tips['app_help']['pending']

    if any(w in lowered for w in ('diet', 'food', 'eat', 'nutrition')):
        return 'General nutrition reminders:\n' + _format_bullets(tips['general_wellness'])

    if any(w in lowered for w in ('hello', 'hi', 'hey', 'start')):
        return tips['welcome']

    return None


def get_quick_reply(quick_key, tips):
    mapping = {
        'welcome': tips['welcome'],
        'trimester_1': 'First trimester tips:\n' + _format_bullets(tips['trimester_1']),
        'trimester_2': 'Second trimester tips:\n' + _format_bullets(tips['trimester_2']),
        'trimester_3': 'Third trimester tips:\n' + _format_bullets(tips['trimester_3']),
        'red_flags': 'Seek care immediately if you notice:\n' + _format_bullets(tips['red_flags']),
        'wellness': 'General wellness:\n' + _format_bullets(tips['general_wellness']),
    }
    return mapping.get(quick_key)


def _prediction_context_for_prompt(request):
    last = get_last_prediction(request)
    if not last:
        return ''
    return (
        f"\nApp context: The user completed Predict recently. "
        f"Latest ML-suggested delivery mode: {last['mode']}. "
        "If they ask about predict or their result, refer to this and stress it is not a diagnosis.\n"
    )


def _history_for_gemini(recent_messages):
    lines = []
    for msg in recent_messages:
        prefix = 'User' if msg.role == 'user' else 'Assistant'
        lines.append(f'{prefix}: {msg.content}')
    return '\n'.join(lines)


GEMINI_MODEL_FALLBACKS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
]


def get_gemini_reply(user_name, user_message, recent_messages, request=None):
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return None

    try:
        import google.generativeai as genai
    except ImportError:
        return None

    preferred = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()
    models_to_try = []
    if preferred:
        models_to_try.append(preferred)
    for name in GEMINI_MODEL_FALLBACKS:
        if name not in models_to_try:
            models_to_try.append(name)

    genai.configure(api_key=api_key)
    history = _history_for_gemini(recent_messages[-10:])
    prompt = (
        SYSTEM_PROMPT.format(user_name=user_name)
        + _prediction_context_for_prompt(request)
        + '\n\nRecent conversation:\n'
        + (history or '(no prior messages)')
        + f'\n\nUser: {user_message}\n\nAssistant:'
    )

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = (response.text or '').strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc
            continue

    if settings.DEBUG and last_error:
        return (
            'The AI service is temporarily unavailable. '
            f'({type(last_error).__name__}) Please try again later or use the quick topic buttons.'
        )
    return None


def generate_assistant_reply(user, user_message, recent_messages, request=None):
    tips = load_tips()
    text = (user_message or '').strip()
    if not text:
        return 'Please type a message or choose a quick topic below.'

    emergency = check_emergency(text)
    if emergency:
        return emergency

    gemini = get_gemini_reply(user.name, text, recent_messages, request)
    if gemini:
        return gemini

    quick = match_rule_reply(text, tips, request)
    if quick:
        return quick

    return (
        'I could not reach the AI service right now. Here are general reminders:\n'
        + _format_bullets(tips['general_wellness'])
        + '\n\nAdd GEMINI_API_KEY to your .env file for fuller answers, or try quick topics below.'
    )
