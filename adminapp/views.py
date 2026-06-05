from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from adminapp.models import *
from mainapp.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
import pandas as pd

from chatapp.utils import admin_login_required
from userapp.models import Appointment, PredictionHistory
from userapp.notifications import notify_user
from sklearn.model_selection import train_test_split

from ml_compat import load_sklearn_pickle
from sklearn.metrics import accuracy_score,f1_score, recall_score, precision_score, auc, roc_auc_score, roc_curve
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
    try:
        print('testttttttttttt')
        data = Dataset.objects.all().order_by('-data_id').first()
        print(data,'data')
        gbc_a = data.ad_accuracy*100
        gbc_p = data.ad_precision*100
        gbc_r = data.ad_recall*100
        gbc_f = data.ad_f1_score*100
        rfc_a = data.xg_accuracy*100
        rfc_p = data.xg_precision*100
        rfc_r = data.xg_recall*100
        rfc_f = data.xg_f1_score*100
        ada_a = data.lr_accuracy*100
        ada_p = data.lr_precision*100
        ada_r = data.lr_recall*100
        ada_f = data.lr_f1_score*100
        context = {
            'gbc_a':gbc_a,
            'gbc_p':gbc_p,
            'gbc_r':gbc_r,
            'gbc_f':gbc_f,
            'rfc_a':rfc_a,
            'rfc_p':rfc_p,
            'rfc_r':rfc_r,
            'rfc_f':rfc_f,
            'ada_a':ada_a,
            'ada_p':ada_p,
            'ada_r':ada_r,
            'ada_f':ada_f,
        }
        return render(request,'adminapp/admin-algocomp.html',context)
    except:
        messages.warning(request,'Run all 3 algorithms to compare values')
        return redirect('view_dataset')


def logistic_reggression(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    context={'data':data}
    return render(request, 'adminapp/admin-svm.html',context)

def dectree(request):
    #
    return render(request, 'adminapp/admin-dectree.html')

def ada_boost(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    context={'data':data}
    return render(request, 'adminapp/admin-knn.html',context)


def xg_boost(request):
    data = Dataset.objects.all().order_by('-data_id').first()
    context={'data':data}
    return render(request, 'adminapp/admin-randfor.html',context)

def ada_runalgo(request,id):
    data =Dataset.objects.get(data_id=id)
    file=str(data.data_set)
    # print(file,'kjhgdfdfghjkhgfdhhhhhhhhhhhhhhhhhhhhhhhhhh')
    df=pd.read_csv(file)
    df['NUMBER OF PREV CESAREAN'] = df['NUMBER OF PREV CESAREAN'].astype('object')
    encoder = load_sklearn_pickle('encoder.pkl')
    y_encoder = load_sklearn_pickle('y_encoder.pkl')
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)
    model = load_sklearn_pickle('GradientBoostingClassifier.pkl')
    prediction=model.predict(x_test)
    Accuracy = accuracy_score(prediction,y_test)
    precision = precision_score(prediction,y_test,average = 'macro')
    recal = recall_score(prediction,y_test,average = 'macro')
    f_score = f1_score(prediction,y_test,average = 'macro')
    data.ad_accuracy = Accuracy
    data.ad_precision = precision
    data.ad_recall = recal
    data.ad_f1_score = f_score
    data.ad_algo = 'Gradient Boost'
    data.save()
    return redirect('knn')

def xg_runalgo(request,id):
    data =Dataset.objects.get(data_id=id)

    file=str(data.data_set)
    # print(file,'kjhgdfdfghjkhgfdhhhhhhhhhhhhhhhhhhhhhhhhhh')
    df=pd.read_csv(file)
    print(len(df.columns),'ghfhfhfhfyfhc')
    df['NUMBER OF PREV CESAREAN'] = df['NUMBER OF PREV CESAREAN'].astype('object')
    encoder = load_sklearn_pickle('encoder.pkl')
    y_encoder = load_sklearn_pickle('y_encoder.pkl')
    
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)

    model = load_sklearn_pickle('XGB.pkl')
    prediction=model.predict(x_test)
    Accuracy = accuracy_score(prediction,y_test)
    precision = precision_score(prediction,y_test,average = 'macro')
    recal = recall_score(prediction,y_test,average = 'macro')
    f_score = f1_score(prediction,y_test,average = 'macro')
    data.xg_accuracy = Accuracy
    data.xg_precision = precision
    data.xg_recall = recal
    data.xg_f1_score = f_score
    data.xg_algo = 'XG Boost'
    data.save()
    return redirect('random_forest')

def lr_runalgo(request,id):
    data =Dataset.objects.get(data_id=id)
    
    file=str(data.data_set)
    # print(file,'kjhgdfdfghjkhgfdhhhhhhhhhhhhhhhhhhhhhhhhhh')
    df=pd.read_csv(file)
    # print(len(df.columns),'ghfhfhfhfyfhc')
    df['NUMBER OF PREV CESAREAN'] = df['NUMBER OF PREV CESAREAN'].astype('object')

    encoder = load_sklearn_pickle('encoder.pkl')
    y_encoder = load_sklearn_pickle('y_encoder.pkl')
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)
    model = load_sklearn_pickle('LogisticRegression.pkl')
    prediction=model.predict(x_test)
    Accuracy = accuracy_score(prediction,y_test)
    precision = precision_score(prediction,y_test,average = 'macro')
    recal = recall_score(prediction,y_test,average = 'macro')
    f_score = f1_score(prediction,y_test,average = 'macro')
    data.lr_accuracy = Accuracy
    data.lr_precision = precision
    data.lr_recall = recal
    data.lr_f1_score = f_score
    data.lr_algo = 'Logistic Regression'
    data.save()
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
    history = PredictionHistory.objects.all()
    paginator = Paginator(history, 10)
    page = paginator.get_page(request.GET.get('page'))

    rows = []
    for record in page:
        try:
            user = mainModel.objects.get(sno=record.user_sno)
        except mainModel.DoesNotExist:
            user = None
        rows.append({'record': record, 'user': user})

    return render(request, 'adminapp/admin-prediction-history.html', {
        'history': page,
        'history_rows': rows,
    })

