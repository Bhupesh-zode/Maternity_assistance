from django.shortcuts import render, redirect
from mainapp.models import mainModel
from django.contrib import messages

# Create your views here.
def adminlogin(request):
    if request.method =="POST":
        email=request.POST.get("email")
        password = request.POST.get("pwd")
        print(email,password)
        try:
           if email=="admin" and password=="admin":
            messages.success(request,'logined succesfully')
            return redirect("admin_dash") 
        except:
            messages.error(request,'incorrect details')
            return redirect("register")
    return render(request, 'mainapp/main-admin-login.html')


def register(request):
    if request.method == "POST" and request.FILES["image"]:
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")   
        relation = request.POST.get("relation")
        password = request.POST.get("pwd")
        image = request.FILES["image"]
        print(name, email, phone, address, relation, password)
        mainModel.objects.create(name=name, email=email, phone = phone, address= address, relation=relation,password = password, image=image)
        messages.success(request,'user has been registered')
        return redirect("userlogin")
    return render(request, 'mainapp/main-user-register.html')

def home(request):
   return render(request, 'mainapp/main-home.html')

def about(request):
   return render(request, 'mainapp/main-about.html')

def contact(request):
   #ask if page needs to be redone or take in the values
   return render(request, 'mainapp/main-contact.html')