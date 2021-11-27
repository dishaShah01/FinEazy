from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from manager.views import *

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'), 
    path('register/',registerUser,name='register'),
    path('',home,name='home'),
    path('admin/', admin.site.urls),
    path('/dashboard',dashboard,name='dashboard'),
    path('/buy',buy,name='buy'),
    path('/buyform',buyform,name='buyform'),
    path('/goal',goal,name='goal'),
    path('crypto/<slug:name>',sell,name='sell'),
    path('/sellform',sellform,name='sellform'),
]
