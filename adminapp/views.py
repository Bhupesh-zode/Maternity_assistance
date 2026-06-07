from datetime import date
import json

from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import *
from mainapp.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.views.decorators.http import require_http_methods
import pandas as pd

from chatapp.utils import admin_login_required
from userapp.models import Appointment, PredictionHistory, UserPrediction
from userapp.prediction_store import FIELD_LABELS, backfill_prediction_history
from userapp.notifications import notify_user
from sklearn.model_selection import train_test_split

from ml_compat import load_sklearn_pickle
from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

TARGET_COLUMN = 'TYPE OF BIRTH    '
TRAIN_TEST_RANDOM_STATE = 0
TRAIN_TEST_SIZE = 0.2


def _prepare_algorithm_dataset(data):
    df = pd.read_csv(str(data.data_set))
    df['NUMBER OF PREV CESAREAN'] = df['NUMBER OF PREV CESAREAN'].astype('object')
    encoder = load_sklearn_pickle('encoder.pkl')
    y_encoder = load_sklearn_pickle('y_encoder.pkl')
    X = encoder.transform(df.drop([TARGET_COLUMN], axis=1))
    Y = y_encoder.transform(df[[TARGET_COLUMN]]).ravel()
    return train_test_split(
        X, Y, test_size=TRAIN_TEST_SIZE, random_state=TRAIN_TEST_RANDOM_STATE,
    )


def _evaluate_classifier(model, x_test, y_test):
    prediction = model.predict(x_test)
    return {
        'accuracy': accuracy_score(y_test, prediction),
        'precision': precision_score(y_test, prediction, average='macro', zero_division=0),
        'recall': recall_score(y_test, prediction, average='macro', zero_division=0),
        'f1_score': f1_score(y_test, prediction, average='macro', zero_division=0),
    }


def _save_algorithm_metrics(data, prefix, metrics, algo_name):
    setattr(data, f'{prefix}_accuracy', metrics['accuracy'])
    setattr(data, f'{prefix}_precision', metrics['precision'])
    setattr(data, f'{prefix}_recall', metrics['recall'])
    setattr(data, f'{prefix}_f1_score', metrics['f1_score'])
    setattr(data, f'{prefix}_algo', algo_name)
    data.save()


ALGORITHM_METRIC_SPECS = (
    ('lr', 'Logistic Regression'),
    ('ad', 'Gradient Boost'),
    ('xg', 'XG Boost'),
)


def _metric_pct(value):
    return round(float(value) * 100, 2)


def _format_metric_pct(value):
    if value is None:
        return '—'
    return f'{_metric_pct(value)}%'


def _algorithm_display_metrics(data, prefix):
    if data is None:
        empty = '—'
        return {
            'accuracy': empty,
            'precision': empty,
            'recall': empty,
            'f1_score': empty,
        }
    return {
        'accuracy': _format_metric_pct(getattr(data, f'{prefix}_accuracy', None)),
        'precision': _format_metric_pct(getattr(data, f'{prefix}_precision', None)),
        'recall': _format_metric_pct(getattr(data, f'{prefix}_recall', None)),
        'f1_score': _format_metric_pct(getattr(data, f'{prefix}_f1_score', None)),
    }


def _build_analysis_metrics(data):
    algorithms = []
    missing = []
    for prefix, label in ALGORITHM_METRIC_SPECS:
        accuracy = getattr(data, f'{prefix}_accuracy', None)
        if accuracy is None:
            missing.append(label)
            continue
        algorithms.append({
            'name': label,
            'accuracy': _metric_pct(accuracy),
            'precision': _metric_pct(getattr(data, f'{prefix}_precision')),
            'recall': _metric_pct(getattr(data, f'{prefix}_recall')),
            'f1_score': _metric_pct(getattr(data, f'{prefix}_f1_score')),
        })
    return algorithms, missing
# Create your views here.

def admin_dash(request):
    return render(request, 'adminapp/admin-dash.html')

def allusers(request):
    #
    all_users=mainModel.objects.filter(Q(status="accepted")|Q(status="restricted"))
    paginator = Paginator(all_users, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    all_details={'allusers':post}
    return render(request, 'adminapp/admin-allusers.html',all_details)

def pending_users(request):
    #2 functions
    pendingusers=mainModel.objects.filter(status="pending")
    paginator = Paginator(pendingusers, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    data={'details':post}
    return render(request, 'adminapp/admin-pendingusers.html',data)

def view_data(request):
    data =Dataset.objects.all().order_by('-data_id').first()
    file=str(data.data_set)
    # print(file,'kjhgdfdfghjkhgfdhhhhhhhhhhhhhhhhhhhhhhhhhh')
    df=pd.read_csv(file,index_col=0)
    # print(df.head())
    table=df.to_html(table_id='data_table')

    

    return render(request, "adminapp/admin-view.html",{"data":table})

def upload_data(request):
    if request.method=='POST':
        dataset = request.FILES['data']
        data_file = Dataset.objects.create(data_set=dataset)
        print(dataset,'asdfgvadfg')
        return redirect('view_dataset')
    return render(request, 'adminapp/admin-upload.html')

def analysis(request):
    data = Dataset.objects.order_by('-data_id').first()
    if not data:
        messages.warning(request, 'Upload a dataset before running analysis.')
        return redirect('view_dataset')

    algorithms, missing = _build_analysis_metrics(data)
    if missing:
        messages.warning(
            request,
            f'Run all three algorithms on dataset #{data.data_id} first. Missing: {", ".join(missing)}.',
        )
        return redirect('view_dataset')

    return render(request, 'adminapp/admin-algocomp.html', {
        'dataset_id': data.data_id,
        'algorithms': algorithms,
        'chart_data_json': json.dumps(algorithms),
    })


def logistic_reggression(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-svm.html', {
        'data': data,
        'metrics': _algorithm_display_metrics(data, 'lr'),
    })

def dectree(request):
    #
    return render(request, 'adminapp/admin-dectree.html')

def ada_boost(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-knn.html', {
        'data': data,
        'metrics': _algorithm_display_metrics(data, 'ad'),
    })


def xg_boost(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    return render(request, 'adminapp/admin-randfor.html', {
        'data': data,
        'metrics': _algorithm_display_metrics(data, 'xg'),
    })

def ada_runalgo(request,id):
    data = Dataset.objects.get(data_id=id)
    x_train, x_test, y_train, y_test = _prepare_algorithm_dataset(data)
    model = GradientBoostingClassifier(random_state=TRAIN_TEST_RANDOM_STATE)
    model.fit(x_train, y_train)
    _save_algorithm_metrics(
        data,
        'ad',
        _evaluate_classifier(model, x_test, y_test),
        'Gradient Boost',
    )
    return redirect('knn')

def xg_runalgo(request,id):
    data = Dataset.objects.get(data_id=id)
    x_train, x_test, y_train, y_test = _prepare_algorithm_dataset(data)
    model = XGBClassifier(random_state=TRAIN_TEST_RANDOM_STATE, verbosity=0)
    model.fit(x_train, y_train)
    _save_algorithm_metrics(
        data,
        'xg',
        _evaluate_classifier(model, x_test, y_test),
        'XG Boost',
    )
    return redirect('random_forest')

def lr_runalgo(request,id):
    data = Dataset.objects.get(data_id=id)
    x_train, x_test, y_train, y_test = _prepare_algorithm_dataset(data)
    model = LogisticRegression(random_state=TRAIN_TEST_RANDOM_STATE, max_iter=1000)
    model.fit(x_train, y_train)
    _save_algorithm_metrics(
        data,
        'lr',
        _evaluate_classifier(model, x_test, y_test),
        'Logistic Regression',
    )
    return redirect('svm')


#button fuctions

def allow(request,id):
    status_update = mainModel.objects.get(sno=id)
    status_update.status = "accepted"
    status_update.save()
    messages.info(request,'status has been accepted')
    return redirect('pending_users')

def reject(request,id):
    status_update = mainModel.objects.get(sno=id)
    status_update.status = "rejected"
    status_update.save()
    messages.info(request,'status has been rejected')
    return redirect('pending_users')

def change_status(request,id):
    status_change = mainModel.objects.get(sno=id)
    if status_change.status == "accepted":
        status_change.status = "restricted"
        status_change.save()
        messages.info(request,'status changed to restricted')
        return redirect('all_users')
    elif status_change.status == "restricted":
        status_change.status = "accepted"
        status_change .save()
        messages.info(request,'status changed to accepted')
        return redirect('all_users')
    
def delete(request,id):
    status_delete = mainModel.objects.get(sno=id)
    status_delete.delete()
    messages.info(request,'user deleted')
    return redirect('all_users')


@admin_login_required
def admin_appointments(request):
    appointments = Appointment.objects.all()
    paginator = Paginator(appointments, 8)
    page = paginator.get_page(request.GET.get('page'))

    rows = []
    for appt in page:
        try:
            user = mainModel.objects.get(sno=appt.user_sno)
        except mainModel.DoesNotExist:
            user = None
        rows.append({'appt': appt, 'user': user})

    return render(request, 'adminapp/admin-appointments.html', {
        'appointments': page,
        'appointment_rows': rows,
        'time_slots': Appointment.TIME_SLOTS,
    })


@admin_login_required
@require_http_methods(['POST'])
def admin_update_appointment(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id)
    action = request.POST.get('action')

    if action == 'confirm':
        appt.status = Appointment.STATUS_CONFIRMED
        appt.confirmed_date = appt.preferred_date
        appt.confirmed_time = appt.preferred_time
        appt.admin_notes = (request.POST.get('admin_notes') or '').strip()
        appt.save()
        notify_user(
            appt.user_sno, 'appointment', 'Appointment confirmed',
            f'Confirmed for {appt.confirmed_date} at {appt.confirmed_time}',
            '/user-appointments',
        )
        messages.success(request, 'Appointment confirmed.')

    elif action == 'reschedule':
        new_date = request.POST.get('confirmed_date')
        new_time = request.POST.get('confirmed_time')
        if not new_date or not new_time:
            messages.warning(request, 'Date and time required to reschedule.')
            return redirect('admin_appointments')
        try:
            appt.confirmed_date = date.fromisoformat(new_date)
        except ValueError:
            messages.warning(request, 'Invalid date.')
            return redirect('admin_appointments')
        appt.confirmed_time = new_time
        appt.status = Appointment.STATUS_RESCHEDULED
        appt.admin_notes = (request.POST.get('admin_notes') or '').strip()
        appt.save()
        notify_user(
            appt.user_sno, 'appointment', 'Appointment rescheduled',
            f'New slot: {appt.confirmed_date} at {appt.confirmed_time}',
            '/user-appointments',
        )
        messages.success(request, 'Appointment rescheduled.')

    elif action == 'complete':
        appt.status = Appointment.STATUS_COMPLETED
        appt.save()
        notify_user(
            appt.user_sno, 'appointment', 'Appointment completed',
            'Your consultation has been marked complete.',
            '/user-appointments',
        )
        messages.success(request, 'Marked as completed.')

    elif action == 'cancel':
        appt.status = Appointment.STATUS_CANCELLED
        appt.admin_notes = (request.POST.get('admin_notes') or '').strip()
        appt.save()
        notify_user(
            appt.user_sno, 'appointment', 'Appointment cancelled',
            appt.admin_notes or 'Your appointment was cancelled by admin.',
            '/user-appointments',
        )
        messages.info(request, 'Appointment cancelled.')

    return redirect('admin_appointments')


@admin_login_required
def admin_prediction_history(request):
    backfill_prediction_history()

    summary_rows = list(
        PredictionHistory.objects
        .values('user_sno')
        .annotate(run_count=Count('id'), latest_at=Max('created_at'))
    )

    known_snos = {row['user_sno'] for row in summary_rows}
    for snapshot in UserPrediction.objects.exclude(user_sno__in=known_snos):
        summary_rows.append({
            'user_sno': snapshot.user_sno,
            'run_count': 1,
            'latest_at': snapshot.updated_at,
        })

    summary_rows.sort(key=lambda row: row['latest_at'], reverse=True)

    paginator = Paginator(summary_rows, 12)
    page = paginator.get_page(request.GET.get('page'))

    user_snos = [row['user_sno'] for row in page.object_list]
    users_by_sno = {
        user.sno: user
        for user in mainModel.objects.filter(sno__in=user_snos)
    }

    user_rows = []
    for row in page.object_list:
        user_rows.append({
            'user_sno': row['user_sno'],
            'user': users_by_sno.get(row['user_sno']),
            'run_count': row['run_count'],
            'latest_at': row['latest_at'],
        })

    return render(request, 'adminapp/admin-prediction-history.html', {
        'users_page': page,
        'user_rows': user_rows,
    })


@admin_login_required
def admin_user_prediction_history(request, user_sno):
    user = get_object_or_404(mainModel, sno=user_sno)
    history = PredictionHistory.objects.filter(user_sno=user_sno)
    paginator = Paginator(history, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'adminapp/admin-user-prediction-history.html', {
        'user': user,
        'history': page,
    })


@admin_login_required
def admin_user_prediction_detail(request, user_sno, history_id):
    user = get_object_or_404(mainModel, sno=user_sno)
    record = get_object_or_404(PredictionHistory, id=history_id, user_sno=user_sno)
    fields = []
    for key, label in FIELD_LABELS.items():
        val = (record.form_data or {}).get(key)
        if val is not None and str(val).strip():
            fields.append({'label': label, 'value': str(val).strip()})

    return render(request, 'adminapp/admin-user-prediction-detail.html', {
        'user': user,
        'record': record,
        'fields': fields,
    })

