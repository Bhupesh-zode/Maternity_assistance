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

GEMINI_MODEL_FALLBACKS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
]

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


def format_chat_plaintext(text):
    """Normalize model output for the chat UI (plain text, single-level bullets)."""
    if not text:
        return text
    lines = []
    for raw in text.replace('\r\n', '\n').split('\n'):
        line = raw.strip()
        if not line:
            lines.append('')
            continue
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        line = re.sub(r'\*([^*]+)\*', r'\1', line)
        if re.match(r'^[-*]\s+', line):
            line = '• ' + line.lstrip('-* ').strip()
        elif re.match(r'^\*\s+\*', line):
            line = '• ' + line.replace('*', '', 2).strip()
        lines.append(line)
    out = '\n'.join(lines)
    while '\n\n\n' in out:
        out = out.replace('\n\n\n', '\n\n')
    return out.strip()


def get_last_prediction(request):
    if request is None:
        return None
    user_sno = request.session.get('sno')
    if user_sno is None:
        return None
    from userapp.prediction_store import get_user_prediction

    return get_user_prediction(user_sno)


def _normalize_delivery_key(mode):
    m = (mode or '').lower()
    if 'vacuum' in m:
        return 'vacuum_extraction'
    if 'forceps' in m:
        return 'forceps_delivery'
    if 'emergency' in m and 'cesarean' in m:
        return 'emergency_cesarean'
    if 'cesarean' in m:
        return 'cesarean_birth'
    if 'vaginal' in m:
        return 'vaginal_birth'
    return 'default'


def _rule_based_delivery_guidance(mode, tips, user_name=None):
    guidance = tips.get('delivery_guidance', {})
    key = _normalize_delivery_key(mode)
    block = guidance.get(key) or guidance.get('default', {})
    precautions = block.get('precautions', [])
    assistance = block.get('assistance', [])
    greeting = f'Hi {user_name},\n\n' if user_name else ''

    lines = [
        f'{greeting}Your app\'s ML suggestion: {mode}',
        '(Guide only — not a diagnosis. Your doctor decides your delivery plan.)',
        '',
        'PRECAUTIONS',
        _format_bullets(precautions),
        '',
        'SUPPORT & RECOVERY',
        _format_bullets(assistance),
        '',
        'WHEN TO SEEK URGENT CARE',
        '• Heavy bleeding, severe or worsening pain, high fever',
        '• Sudden fluid leakage or concerns about baby\'s movement',
        '• Any symptom your maternity team told you to report immediately',
    ]
    return '\n'.join(lines)


def get_gemini_predict_guidance(user_name, mode, form_data):
    """Precautions and assistance for the saved prediction — no form field dump."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return None

    try:
        import google.generativeai as genai
    except ImportError:
        return None

    # Short internal context for the model only (not echoed as a data list).
    context_bits = []
    fd = form_data or {}
    if fd.get('Gestational'):
        context_bits.append(f"gestational age about {fd['Gestational']} weeks")
    if fd.get('parity') is not None:
        context_bits.append(f"parity {fd['parity']}")
    if str(fd.get('Number_of_previous_Cesarean', '')).strip() not in ('', '0'):
        context_bits.append('has previous cesarean history')
    clinical_hint = ', '.join(context_bits) if context_bits else 'no extra clinical detail'

    prompt = (
        f"You are a pregnancy wellness assistant speaking to {user_name}.\n"
        f"The ML model suggested this delivery mode: {mode}\n"
        f"Internal context only (do not list as form fields): {clinical_hint}.\n\n"
        "Write a plain-text reply. STRICT formatting rules:\n"
        "- No markdown, no **bold**, no nested lists, no numbered lists\n"
        "- Line 1: Hi {name}, + one sentence naming {mode} and that this is not a diagnosis\n"
        "- Then exactly these section headers on their own line:\n"
        "  PRECAUTIONS\n"
        "  SUPPORT & RECOVERY\n"
        "  WHEN TO SEEK URGENT CARE\n"
        "- Under each header, 3-4 bullet lines starting with the character •\n"
        "- Do NOT mention exploring the app, app features, or antenatal checkups in general\n"
        "- Focus only on precautions and practical help for {mode}\n"
        "- Maximum 220 words\n"
    ).format(name=user_name, mode=mode)

    preferred = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()
    models_to_try = [preferred] if preferred else []
    for name in GEMINI_MODEL_FALLBACKS:
        if name not in models_to_try:
            models_to_try.append(name)

    genai.configure(api_key=api_key)
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = format_chat_plaintext((response.text or '').strip())
            if text and mode.lower() in text.lower():
                return text
        except Exception:
            continue
    return None


def get_predict_guidance_reply(user, request, tips):
    """Precautions and patient assistance for the user's saved Predict result."""
    last = get_last_prediction(request)
    if not last:
        return tips['app_help']['predict']

    mode = last['mode']
    # Curated tips: consistent plain-text sections (no markdown / nested lists).
    return _rule_based_delivery_guidance(mode, tips, user.name)


def get_predict_help_reply(user, request, tips):
    """Alias for predict quick-topic and keyword handling."""
    if user is None:
        last = get_last_prediction(request)
        if last:
            return _rule_based_delivery_guidance(last['mode'], tips, None)
        return tips['app_help']['predict']
    return get_predict_guidance_reply(user, request, tips)


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


def match_rule_reply(text, tips, request=None, user=None):
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
        return get_predict_help_reply(user, request, tips)

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
    from userapp.prediction_store import format_prediction_context_for_ai

    return (
        '\nApp context (saved Predict data for this user):\n'
        + format_prediction_context_for_ai(last)
        + '\nIf they ask about predict or their result, use the above and stress it is not a diagnosis.\n'
    )


def _history_for_gemini(recent_messages):
    lines = []
    for msg in recent_messages:
        prefix = 'User' if msg.role == 'user' else 'Assistant'
        lines.append(f'{prefix}: {msg.content}')
    return '\n'.join(lines)


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
            text = format_chat_plaintext((response.text or '').strip())
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

    quick = match_rule_reply(text, tips, request, user)
    if quick:
        return quick

    return (
        'I could not reach the AI service right now. Here are general reminders:\n'
        + _format_bullets(tips['general_wellness'])
        + '\n\nAdd GEMINI_API_KEY to your .env file for fuller answers, or try quick topics below.'
    )
