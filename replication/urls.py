from django.urls import path

from . import views


app_name = 'replication'

urlpatterns = [
    path('survey-answers/', views.SurveyAnswers, name="survey_answers" ),
    path('survey-answers/<int:survey_answer_id>/', views.SurveyAnswer, name="survey_answer" ),

    path('question-answers/', views.QuestionAnswer, name="question_answers" ),
]