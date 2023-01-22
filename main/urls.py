from django.urls import path

from . import views


app_name = 'main'

urlpatterns = [
    path('surveys/', views.Surveys.as_view(), name="surveys"),
    path('surveys/<int:survey_id>/', views.Survey.as_view(), name="survey"),

    path('publish-survey/', views.SurveyPublish.as_view(), name="survey_publish"),

    path('questions/', views.Questions.as_view(), name="questions"),
    path('questions/<int:question_id>/', views.Question.as_view(), name="question"),

    path('questionsChoices/', views.QuestionChoices.as_view(), name="question_choices"),
    path('questionsChoices/<int:question_choice_id>/', views.QuestionChoice.as_view(), name="question_choice"),

    path('questionImages/', views.QuestionImages.as_view(), name="question_images"),
]