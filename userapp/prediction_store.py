"""Persist and load per-user Predict form data and ML results."""

from userapp.models import UserPrediction

# Labels for assistant / Gemini context (form field keys → readable names).
FIELD_LABELS = {
    'age': 'Age',
    'BMI': 'BMI',
    'Weight': 'Weight (kg)',
    'Height': 'Height (cm)',
    'parity': 'Parity',
    'Gestational': 'Gestational age (weeks)',
    'Weight_increased_during': 'Weight gain in pregnancy (kg)',
    'Number_of_previous_Cesarean': 'Previous cesareans',
    'Complications': 'Complications',
    'Robson': 'Robson group',
    'art': 'ART mode',
    'Amniocentesis': 'Amniocentesis',
    'EPISITOMY': 'Episiotomy',
    'Previous': 'Previous cesarean (raw)',
    'Obstetric': 'Obstetric risk',
    'Comorbidity': 'Comorbidity',
    'Start_of_Antenatal_Care': 'Antenatal care start',
    'ArT': 'ART',
    'Amniotic_Liquid': 'Amniotic fluid',
    'Repeated_Miscarriages': 'Repeated miscarriages',
    'Cardiotocography': 'Cardiotocography',
    'Maternal_Education': 'Maternal education',
}


def save_user_prediction(user_sno, predicted_mode, form_data):
    mode = (predicted_mode or '').strip()
    if not mode or user_sno is None:
        return None
    obj, _ = UserPrediction.objects.update_or_create(
        user_sno=user_sno,
        defaults={
            'predicted_mode': mode,
            'summary': f'The best way of child birth is {mode}',
            'form_data': form_data or {},
        },
    )
    return obj


def get_user_prediction(user_sno):
    if user_sno is None:
        return None
    try:
        obj = UserPrediction.objects.get(user_sno=user_sno)
    except UserPrediction.DoesNotExist:
        return None
    return {
        'user_sno': obj.user_sno,
        'mode': obj.predicted_mode,
        'summary': obj.summary,
        'form_data': obj.form_data or {},
        'updated_at': obj.updated_at,
    }


def format_form_data_summary(form_data):
    """Short bullet list of submitted predict fields for chat replies."""
    if not form_data:
        return ''
    lines = []
    for key, label in FIELD_LABELS.items():
        val = form_data.get(key)
        if val is None or str(val).strip() == '':
            continue
        lines.append(f'• {label}: {str(val).strip()}')
    return '\n'.join(lines)


def format_prediction_context_for_ai(record):
    if not record:
        return ''
    parts = [
        f'Latest ML-suggested delivery mode: {record["mode"]}.',
        'This is model output only, not a medical diagnosis.',
    ]
    summary = format_form_data_summary(record.get('form_data') or {})
    if summary:
        parts.append('User\'s last Predict form values:\n' + summary)
    updated = record.get('updated_at')
    if updated:
        parts.append(f'Last updated: {updated.strftime("%Y-%m-%d %H:%M")} UTC.')
    return '\n'.join(parts)
