"""childbirth_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from adminapp import views as admin_views
from mainapp import views as main_views
from userapp import views as user_views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    #ADMIN URLS
    path('admin-dashboard', admin_views.admin_dash, name="admin_dash"),
    path('admin-all-users', admin_views.allusers, name="all_users"),
    path('admin-pending-users', admin_views.pending_users, name="pending_users"),
    path('view-dataset', admin_views.view_data, name="view_dataset"),
    path('upload-dataset', admin_views.upload_data, name="upload_dataset"),
    path('algorithm-analysis', admin_views.analysis, name="algorithm_analysis"),
    path('algorithm-svm', admin_views.logistic_reggression, name="svm"),
    path('algorithm-decision-tree', admin_views.dectree, name="decision_tree"),
    path('algorithm-knn', admin_views.ada_boost, name="knn"),
    path('algorithm-random-forest', admin_views.xg_boost, name="random_forest"),
    path('ada-runalgo/<int:id>/', admin_views.ada_runalgo, name="ada_runalgo"),
    path('xg-runalgo/<int:id>/', admin_views.xg_runalgo, name="xg_runalgo"),
    path('lr-runalgo/<int:id>/', admin_views.lr_runalgo, name="lr_runalgo"),
   
    #MAIN URLS
    path('adminlogin', main_views.adminlogin, name = "adminlogin"),
    path('register', main_views.register, name= "register"),
    path('', main_views.home, name="home"),
    path('about', main_views.about, name="about"),
    path('contact', main_views.contact, name="contact"),

    #USER URLS
    path('userlogin', user_views.userlogin, name ="userlogin" ),
    path('user-dashboard', user_views.user_dash, name ="user_dash"),
    path('user-profile', user_views.user_profile, name ="user_profile"),
    path('user-predict', user_views.user_predict, name ="user_predict"),
    path('user_predict_result/<str:result>/<str:con>',user_views.user_predict_result,name="user_predict_result"),

    #BUTTON FUNCTIONS URLS
    path('allow/<int:id>',admin_views.allow,name="allow"),
    path('reject/<int:id>',admin_views.reject,name="reject"),
    path('change_status/<int:id>',admin_views.change_status,name="change_status"),
    path('delete/<int:id>',admin_views.delete,name="delete"),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
