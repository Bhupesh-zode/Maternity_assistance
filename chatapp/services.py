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
- Answer any user question naturally using the app context provided below (predictions, appointments, general pregnancy topics).
- Do not wait for specific keywords — interpret intent from normal conversation.
- Give general wellness information only. You are NOT a doctor.
- Never diagnose conditions, prescribe medicines, or tell the user to ignore medical advice.
- For emergencies (bleeding, severe pain, no fetal movement, etc.), tell them to contact emergency services or their doctor immediately.
- Keep replies concise: 2–5 short paragraphs or bullet points.
- Encourage regular antenatal checkups.
- If asked about the app's ML prediction, use the prediction context below; say it is a guide only and clinical decisions belong to their healthcare provider.
- If asked about appointments, booking, or schedule, use the appointment context below; do not invent visits that are not listed.
- If app context is missing for something they ask, say what you do not have and point them to the relevant menu in the app.
- Be warm and respectful. User's name: {user_name}.
"""


def _gemini_api_key():
    return os.environ.get('GEMINI_API_KEY', '').strip()


def _gemini_configured():
    return bool(_gemini_api_key())


def _gemini_models_to_try():
    preferred = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash').strip()
    models = [preferred] if preferred else []
    for name in GEMINI_MODEL_FALLBACKS:
        if name not in models:
            models.append(name)
    return models


def _build_system_instruction(user_name, request):
    return (
        SYSTEM_PROMPT.format(user_name=user_name)
        + _prediction_context_for_prompt(request)
        + _appointment_context_for_prompt(request)
    )


def _build_gemini_history(recent_messages):
    """Convert stored chat rows to Gemini multi-turn history."""
    history = []
    for msg in recent_messages[-10:]:
        role = 'user' if msg.role == 'user' else 'model'
        if not history and role != 'user':
            continue
        if history and history[-1]['role'] == role:
            history[-1]['parts'][0] += '\n' + msg.content
        else:
            history.append({'role': role, 'parts': [msg.content]})
    return history

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
    """Offline fallback only when Gemini is not configured."""
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

    if any(w in lowered for w in ('hello', 'hi', 'hey', 'start')):
        return tips['welcome']

    return None


def _offline_fallback_reply(tips):
    return (
        'The AI assistant needs GEMINI_API_KEY in your .env file to answer freely. '
        'Until then, try a quick topic below or ask about trimesters, red flags, or predict care tips.\n\n'
        + tips['welcome']
    )


def _gemini_unavailable_reply(tips, last_error=None):
    if settings.DEBUG and last_error:
        return (
            'The AI service is temporarily unavailable. '
            f'({type(last_error).__name__}) Please try again in a moment.'
        )
    return (
        'The AI service is temporarily unavailable. Please try again shortly, '
        'or use a quick topic button below.'
    )


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


def _appointment_context_for_prompt(request):
    if request is None:
        return ''
    user_sno = request.session.get('sno')
    if user_sno is None:
        return ''
    from userapp.appointment_context import format_appointments_context_for_ai

    return format_appointments_context_for_ai(user_sno)


def get_gemini_reply(user_name, user_message, recent_messages, request=None):
    api_key = _gemini_api_key()
    if not api_key:
        return None

    try:
        import google.generativeai as genai
    except ImportError:
        return None

    genai.configure(api_key=api_key)
    system_instruction = _build_system_instruction(user_name, request)
    history = _build_gemini_history(recent_messages)

    last_error = None
    for model_name in _gemini_models_to_try():
        try:
            model = genai.GenerativeModel(
                model_name,
                system_instruction=system_instruction,
            )
            chat = model.start_chat(history=history)
            response = chat.send_message(user_message)
            text = format_chat_plaintext((response.text or '').strip())
            if text:
                return text
        except Exception as exc:
            last_error = exc
            continue

    return _gemini_unavailable_reply(load_tips(), last_error)


def generate_assistant_reply(user, user_message, recent_messages, request=None):
    tips = load_tips()
    text = (user_message or '').strip()
    if not text:
        return 'Please type a message or choose a quick topic below.'

    emergency = check_emergency(text)
    if emergency:
        return emergency

    if _gemini_configured():
        return get_gemini_reply(user.name, text, recent_messages, request)

    quick = match_rule_reply(text, tips, request, user)
    if quick:
        return quick

    return _offline_fallback_reply(tips)
