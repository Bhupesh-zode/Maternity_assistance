from django.shortcuts import render, redirect
from adminapp.models import *
from mainapp.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
from pickle import load
from sklearn.model_selection import train_test_split
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
    encoder=load(open('encoder.pkl','rb'))
    y_encoder=load(open('y_encoder.pkl','rb'))
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)
    model = load(open('GradientBoostingClassifier.pkl','rb'))
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
    encoder=load(open('encoder.pkl','rb'))
    y_encoder=load(open('y_encoder.pkl','rb'))
    
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)

    model = load(open('XGB.pkl','rb'))
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

    encoder=load(open('encoder.pkl','rb'))
    y_encoder=load(open('y_encoder.pkl','rb'))
    X=encoder.transform(df.drop(['TYPE OF BIRTH    '],axis=1))
    Y=y_encoder.transform(df[['TYPE OF BIRTH    ']])
    x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.2,random_state=0)
    model = load(open('LogisticRegression.pkl','rb'))
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

