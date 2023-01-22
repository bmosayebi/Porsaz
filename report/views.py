from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework import status

from main import models as main
from main import serializers


class MySurveys(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        surveys = main.Survey.objects.filter(user=self.request.user)

        surveys_list = []
        for s in surveys:
            d = serializers.get_survey_dictionary(s)
            d['is_published'] = s.is_published
            surveys_list.append(d)

        count = len(surveys_list)
        data ={
            'surveys': surveys_list,
            'count': count
        }
        message = f"{count} پرسش‌نامه یافت شد."
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)


class MySurvey(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            survey_id = kwargs['survey_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        survey = main.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey = survey.first()

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        if self.request.user != survey.user:
            message = "شما امکان ویرایش این پرسش‌نامه را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)

        d = serializers.get_survey_dictionary(survey)
        d['is_published'] = survey.is_published

        survey_answers = []
        for sa in survey.answers.all():
            survey_answers.append(sa.id)
        
        count = len(survey_answers)

        data ={
            'survey': d,
            'survey_answers': survey_answers,
            'survey_answers_count': count
        }
        message = "پرسش‌نامه یافت شد."
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)


class SurveyAnswer(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            survey_answer_id = kwargs['survey_answer_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        survey_answer = main.SurveyAnswer.objects.filter(id=survey_answer_id)
        if not survey_answer:
            message = "پاسخ پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey_answer = survey_answer.first()
        survey = survey_answer.survey
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        if self.request.user != survey.user:
            message = "شما امکان مشاهده این پاسخ را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)

        questions = survey.questions.all()
        question_list = []

        for q in questions:
            question_list.append(q.get_report(survey_answer))


        count = len(questions)

        data ={
            'questions': questions,
            'count': count
        }
        message = "پاسخ‌ها یافت شد."
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)