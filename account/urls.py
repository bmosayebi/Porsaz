from django.urls import path

from . import views


app_name = 'account'

urlpatterns = [
    path('send-sms/', views.SendSMS.as_view()),
    path('validate-code/', views.ValidateCode.as_view()),
    path('register/', views.Register.as_view()),
    path('update/', views.UpdateName.as_view()),
]