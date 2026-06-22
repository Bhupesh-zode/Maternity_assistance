from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import pandas as pd

from chatapp.utils import get_logged_in_user, user_login_required
from mainapp.models import mainModel
from ml_compat import load_sklearn_pickle
from userapp.models import Appointment, PredictionHistory, UserNotification
from userapp.appointment_slots import booked_times_for_date, is_slot_booked
from userapp.notifications import notify_user
from userapp.prediction_store import FIELD_LABELS, save_user_prediction


def _appointment_slot_is_past(appt_date, preferred_time):
    """True if the date/time slot is not strictly after now (local timezone)."""
    today = timezone.localdate()
    if appt_date < today:
        return True
    if appt_date > today:
        return False
    now = timezone.localtime()
    hour, minute = map(int, preferred_time.split(':'))
    slot_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return slot_dt <= now



# Create your views here.
def userlogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("pwd")
        print(email,password)
        try:
            user = mainModel.objects.get(email=email, password=password)
            print(user)
            print(user.sno,'jhgfdsakjhgfds')
            if user.status == "pending":
                messages.info(request,'your account is on pending')
                return redirect('userlogin')
            request.session['sno'] = user.sno
            print(request.session['sno'], 'qweerty')
            messages.success(request,'Logged in successfully')
            return redirect("user_dash")
        except:
            messages.error(request,'incorrect details')
            return redirect("userlogin") #send it to login again
    return render(request, 'userapp/user-login.html')


def user_logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('home')


def user_predict_result(request,result,con):
    context = {'result':result,
               'con':con}
    return render(request,'userapp/user-predict-result.html',context)

def _shift_month(year, month, delta):
    month += delta
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def _dashboard_chart_data(user_sno):
    now = timezone.now()
    six_months_ago = now - timedelta(days=180)
    monthly_rows = (
        PredictionHistory.objects.filter(user_sno=user_sno, created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    month_counts = {(row['month'].year, row['month'].month): row['count'] for row in monthly_rows}
    activity_labels = []
    activity_values = []
    for offset in range(5, -1, -1):
        year, month = _shift_month(now.year, now.month, -offset)
        activity_labels.append(date(year, month, 1).strftime('%b %Y'))
        activity_values.append(month_counts.get((year, month), 0))
    activity_total = sum(activity_values)

    status_order = [
        Appointment.STATUS_PENDING,
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_RESCHEDULED,
        Appointment.STATUS_COMPLETED,
        Appointment.STATUS_CANCELLED,
    ]
    status_map = {
        Appointment.STATUS_PENDING: 'Pending',
        Appointment.STATUS_CONFIRMED: 'Confirmed',
        Appointment.STATUS_RESCHEDULED: 'Rescheduled',
        Appointment.STATUS_COMPLETED: 'Completed',
        Appointment.STATUS_CANCELLED: 'Cancelled',
    }
    appt_counts = {
        row['status']: row['count']
        for row in Appointment.objects.filter(user_sno=user_sno)
        .values('status')
        .annotate(count=Count('id'))
    }
    appt_labels = [status_map[status] for status in status_order if appt_counts.get(status)]
    appt_values = [appt_counts[status] for status in status_order if appt_counts.get(status)]
    appt_total = sum(appt_values)

    return {
        'activity': {'labels': activity_labels, 'values': activity_values, 'total': activity_total},
        'appointments': {'labels': appt_labels, 'values': appt_values, 'total': appt_total},
        'summaries': {
            'activity': f'{activity_total} in 6 mo',
            'appointments': f'{appt_total} total',
        },
        'has_activity': activity_total > 0,
        'has_appointments': appt_total > 0,
    }


@user_login_required
def user_dash(request):
    user = get_logged_in_user(request)
    latest_prediction = PredictionHistory.objects.filter(user_sno=user.sno).first()
    appointment_qs = Appointment.objects.filter(user_sno=user.sno)
    pending_appointments = appointment_qs.filter(status=Appointment.STATUS_PENDING).count()
    chart_data = _dashboard_chart_data(user.sno)
    context = {
        'user': user,
        'latest_prediction': latest_prediction,
        'user_stats': {
            'predictions': PredictionHistory.objects.filter(user_sno=user.sno).count(),
            'appointments': appointment_qs.count(),
            'appointments_hint': (
                f'{pending_appointments} pending approval'
                if pending_appointments
                else 'Book a consultation anytime'
            ),
        },
        'chart_data': chart_data,
    }
    return render(request, 'userapp/user-dash.html', context)

def user_profile(request):
    s_id = request.session["sno"]
    user = mainModel.objects.get(sno = s_id)
    if request.method=="POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        relation = request.POST.get("relation")
        address = request.POST.get("address")
        if len(request.FILES)!= 0:
            img = request.FILES["img"]
            user.image = img
            user.name = name
            user.email = email
            user.phone = phone
            user.relation = relation
            user.address = address
            user.save()
            messages.info(request,'Changes updated')
            return redirect('user_profile')
        else:
            user.name = name
            user.email = email
            user.phone = phone
            user.relation = relation
            user.address = address
            user.save()
            messages.info(request,'Changes updated')
            return redirect('user_profile')
    context = {"user": user}
    # print(fname,email, phone, relation, address, img)
    return render(request, 'userapp/user-myprofile.html', context)

def user_predict(request):
    #create model and make a function to accept values
    if request.method=="POST":
        age = request.POST.get("age")
        BMI = request.POST.get("BMI")
        Weight = request.POST.get("Weight")
        Height = request.POST.get("Height")
        Complications = request.POST.get("Complications")
        Robson = request.POST.get("Robson")
        art = request.POST.get("art")
        Amniocentesis = request.POST.get("Amniocentesis")
        EPISITOMY = request.POST.get("EPISITOMY")
        Previous = [request.POST.get("Previous")]
        parity = request.POST.get("parity")
        Obstetric = request.POST.get("Obstetric")
        Comorbidity = request.POST.get("Comorbidity")
        Number_of_previous_Cesarean = request.POST.get("Number_of_previous_Cesarean")
        Weight_increased_during = request.POST.get("Weight_increased_during")
        Start_of_Antenatal_Care = request.POST.get("Start_of_Antenatal_Care")
        ArT = request.POST.get("ArT")
        Amniotic_Liquid = request.POST.get("Amniotic_Liquid")
        Repeated_Miscarriages = request.POST.get("Repeated_Miscarriages")

        Gestational = request.POST.get("Gestational")
        Cardiotocography = request.POST.get("Cardiotocography")
        Maternal_Education = request.POST.get("Maternal_Education")
        
        # EPISITOMY='T'
        data = {'PREVIOUS CESAREAN':Previous, 'COMPLICATIONS':Complications, 'ROBSON GROUP':Robson, 
                'ART MODE':art,'AMNIOCENTESIS':Amniocentesis, 'EPISIOTOMY':EPISITOMY, 
                                'OBSTETRIC RISK':Obstetric, 'COMORBIDITY':Comorbidity, 
                                'START  ANTENATAL CARRE':Start_of_Antenatal_Care, 'ART':ArT,
                                'AMNIOTIC LIQUID':Amniotic_Liquid, 'REPEATED MISCARRIAGES ':Repeated_Miscarriages, 
                                'CARDIOTOCOGRAPHY  ':Cardiotocography,'MATERNAL EDUCATION':Maternal_Education}
        df = pd.DataFrame(data, index=[0])

        encoder = load_sklearn_pickle('encoder_newf.pkl')
        y_encoder = load_sklearn_pickle('y_encoder.pkl')
        print(df,'llllllllllllllllllllllllllllllllllllllllllllllllllllllll')

 
        encoded=encoder.transform(df)
        

        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')


        df_encoded = pd.DataFrame(encoded, columns=['PREVIOUS CESAREAN', 'COMPLICATIONS', 'ROBSON GROUP', 'ART MODE',
       'AMNIOCENTESIS', 'EPISIOTOMY', 'OBSTETRIC RISK', 'COMORBIDITY', 'START  ANTENATAL CARRE', 'ART',
       'AMNIOTIC LIQUID', 'REPEATED MISCARRIAGES ', 'CARDIOTOCOGRAPHY  ',
       'MATERNAL EDUCATION'])
        print(df_encoded,'hgffsrfsfukgdty')
        
        data = {'PREVIOUS CESAREAN':df_encoded['PREVIOUS CESAREAN'][0], 'COMPLICATIONS':df_encoded['COMPLICATIONS'][0],
                  'ROBSON GROUP':df_encoded['ROBSON GROUP'][0],
                  'ART MODE':df_encoded['ART MODE'][0],
                  'AMNIOCENTESIS':df_encoded['AMNIOCENTESIS'][0], 'EPISIOTOMY':df_encoded['EPISIOTOMY'][0],
                  'PARITY':int(parity), 'OBSTETRIC RISK':df_encoded['OBSTETRIC RISK'][0],
                  'COMORBIDITY': df_encoded['COMORBIDITY'][0],'NUMBER OF PREV CESAREAN':int(Number_of_previous_Cesarean), 
                  'KG INCREASED PREGNANCY':float(Weight_increased_during),
                  'START  ANTENATAL CARRE':df_encoded['START  ANTENATAL CARRE'][0], 
                  'ART':df_encoded['ART'][0], 'AMNIOTIC LIQUID':df_encoded['AMNIOTIC LIQUID'][0],
                  'REPEATED MISCARRIAGES ':df_encoded['REPEATED MISCARRIAGES '][0], 
                  'GESTAGIONAL AGE ':int(Gestational), 'HEIGHT':float(Height),'WEIGHT':float(Weight),
                  'BMI':float(BMI),
                  'AGE':int(age), 'CARDIOTOCOGRAPHY  ':df_encoded['CARDIOTOCOGRAPHY  '][0], 
                  'MATERNAL EDUCATION':df_encoded['MATERNAL EDUCATION'][0]}
        df = pd.DataFrame(data, index=[0])
        print(df,'dfgftyasdkaJtkwtdfwtydfwtdfwtyf')
        print(df.head().T)
                #df.to_csv('my_data.csv', index=False)
        # print(df.head().T,'sdagfdakjseudgyfesufgeyfgegdegg')
        
        # X=encoder.transform(df)

        model = load_sklearn_pickle('XGB.pkl')
        prediction=model.predict(df)
        

        type=y_encoder.inverse_transform(prediction)
        # print(type,'asugychsugyjdefayugvedjyhv')



        con = type[0]
        form_snapshot = {
            'age': age,
            'BMI': BMI,
            'Weight': Weight,
            'Height': Height,
            'parity': parity,
            'Gestational': Gestational,
            'Weight_increased_during': Weight_increased_during,
            'Number_of_previous_Cesarean': Number_of_previous_Cesarean,
            'Complications': Complications,
            'Robson': Robson,
            'art': art,
            'Amniocentesis': Amniocentesis,
            'EPISITOMY': EPISITOMY,
            'Previous': request.POST.get('Previous'),
            'Obstetric': Obstetric,
            'Comorbidity': Comorbidity,
            'Start_of_Antenatal_Care': Start_of_Antenatal_Care,
            'ArT': ArT,
            'Amniotic_Liquid': Amniotic_Liquid,
            'Repeated_Miscarriages': Repeated_Miscarriages,
            'Cardiotocography': Cardiotocography,
            'Maternal_Education': Maternal_Education,
        }
        save_user_prediction(request.session.get('sno'), con, form_snapshot)
        messages.success(request,f'The best way of child birth is  {type[0]}')
        resul=f'The best way of child birth is  {type[0]}'
        return redirect('user_predict_result',resul,con)
    return render(request, 'userapp/user-predict.html')


@user_login_required
def user_prediction_history(request):
    user = get_logged_in_user(request)
    history = PredictionHistory.objects.filter(user_sno=user.sno)
    paginator = Paginator(history, 8)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'userapp/user-prediction-history.html', {
        'user': user,
        'history': page,
    })


@user_login_required
def user_prediction_detail(request, history_id):
    user = get_logged_in_user(request)
    record = get_object_or_404(PredictionHistory, id=history_id, user_sno=user.sno)
    fields = []
    for key, label in FIELD_LABELS.items():
        val = (record.form_data or {}).get(key)
        if val is not None and str(val).strip():
            fields.append({'label': label, 'value': str(val).strip()})
    return render(request, 'userapp/user-prediction-detail.html', {
        'user': user,
        'record': record,
        'fields': fields,
    })


@user_login_required
@require_http_methods(['GET', 'POST'])
def user_appointments(request):
    user = get_logged_in_user(request)

    if request.method == 'POST':
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        notes = (request.POST.get('notes') or '').strip()

        if not preferred_date or not preferred_time:
            messages.warning(request, 'Please select a date and time slot.')
            return redirect('user_appointments')

        try:
            appt_date = date.fromisoformat(preferred_date)
        except ValueError:
            messages.warning(request, 'Invalid date selected.')
            return redirect('user_appointments')

        if _appointment_slot_is_past(appt_date, preferred_time):
            messages.warning(request, 'Please choose a date and time in the future.')
            return redirect('user_appointments')

        if is_slot_booked(appt_date, preferred_time):
            messages.warning(request, 'That time slot is already booked. Please choose another.')
            return redirect('user_appointments')

        Appointment.objects.create(
            user_sno=user.sno,
            preferred_date=appt_date,
            preferred_time=preferred_time,
            notes=notes,
        )
        messages.success(request, 'Appointment request submitted. Admin will confirm soon.')
        return redirect('user_appointments')

    appointments = Appointment.objects.filter(user_sno=user.sno)
    return render(request, 'userapp/user-appointments.html', {
        'user': user,
        'appointments': appointments,
        'time_slots': Appointment.TIME_SLOTS,
        'min_appointment_date': timezone.localdate().isoformat(),
        'booked_slots_url': reverse('user_appointment_booked_slots'),
    })


@user_login_required
def user_appointment_booked_slots(request):
    date_str = request.GET.get('date', '').strip()
    if not date_str:
        return JsonResponse({'booked': []})
    try:
        appt_date = date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid date.'}, status=400)
    return JsonResponse({
        'booked': sorted(booked_times_for_date(appt_date)),
    })


@user_login_required
def user_cancel_appointment(request, appt_id):
    user = get_logged_in_user(request)
    appt = get_object_or_404(Appointment, id=appt_id, user_sno=user.sno)
    if appt.status != Appointment.STATUS_PENDING:
        messages.warning(request, 'Only pending requests can be cancelled.')
        return redirect('user_appointments')
    appt.status = Appointment.STATUS_CANCELLED
    appt.save()
    messages.info(request, 'Appointment request cancelled.')
    return redirect('user_appointments')


@user_login_required
def user_notifications(request):
    user = get_logged_in_user(request)
    UserNotification.objects.filter(user_sno=user.sno, is_read=False).update(is_read=True)
    items = UserNotification.objects.filter(user_sno=user.sno)[:50]
    return render(request, 'userapp/user-notifications.html', {
        'user': user,
        'notifications': items,
    })


@user_login_required
@require_http_methods(['POST'])
def user_clear_notifications(request):
    user = get_logged_in_user(request)
    UserNotification.objects.filter(user_sno=user.sno).delete()
    messages.success(request, 'All alerts cleared.')
    next_url = request.POST.get('next') or reverse('user_dash')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('user_dash')
    return redirect(next_url)