from django.urls import path

from . import views


app_name = 'report'

urlpatterns = [
    path('my-surveys/', views.MySurveys.as_view(), name="my_surveys"),
    path('my-surveys/<int:survey_id>/', views.MySurvey.as_view(), name="my_survey"),
    path('survey-answers/<int:survey_answer_id>/', views.SurveyAnswer.as_view(), name="survey_answer"),

]