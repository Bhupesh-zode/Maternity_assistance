from django.shortcuts import render, redirect
from mainapp.models import mainModel
from django.contrib import messages
import pandas as pd

from ml_compat import load_sklearn_pickle



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
            request.session["sno"] = user.sno
            print(request.session["sno"],'qweerty')
            messages.success(request,'Logged in successfully')
            return redirect("user_dash")
        except:
            messages.error(request,'incorrect details')
            return redirect("userlogin") #send it to login again
    return render(request, 'userapp/user-login.html')


def user_predict_result(request,result,con):
    context = {'result':result,
               'con':con}
    return render(request,'userapp/user-predict-result.html',context)

def user_dash(request):
    return render (request, 'userapp/user-dash.html')

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
        request.session['last_prediction'] = {
            'mode': con,
            'summary': f'The best way of child birth is {con}',
        }
        request.session.modified = True
        messages.success(request,f'The best way of child birth is  {type[0]}')
        resul=f'The best way of child birth is  {type[0]}'
        return redirect('user_predict_result',resul,con)
    return render(request, 'userapp/user-predict.html')