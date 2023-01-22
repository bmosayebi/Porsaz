from django.urls import path

from . import views


app_name = 'replication'

urlpatterns = [
    path('survey-answers/', views.SurveyAnswers.as_view(), name="survey_answers" ),

]