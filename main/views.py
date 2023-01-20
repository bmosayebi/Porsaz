from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework import status

from . import models, serializers


class Surveys(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                name = self.request.query_params['name']
                text = self.request.query_params.get('text')
            elif self.request.data:
                name = self.request.data['name']
                text = self.request.data.get('text')
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        survey = models.Survey.objects.create(user=self.request.user, name=name, text=text)
        survey.save()

        message = "پرسش‌نامه با موفقیت ساخته شد."
        data = {
            'survey_id': survey.id,
        }
        return Response({"message": message, 'data': data}, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        try:
            if self.request.query_params:
                q = self.request.query_params.get('q')
            else:
                q = None
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if q:
            surveys = models.Survey.objects.filter(name__contains=q) | models.Survey.objects.filter(text__contains=q)
        else:
            surveys = models.Survey.objects.all()
        
        surveys_count = surveys.count()
        survey_list = []

        for survey in surveys:
            survey_list.append(serializers.get_survey_dictionary(survey))
        data ={
            'surveys': survey_list,
            'count': surveys_count
        }
        message = f'{surveys_count} پرسش‌نامه یافت شد'

        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)

class Survey(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            survey_id = kwargs['survey_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        survey = models.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey = survey.first()

        data ={
            'survey': serializers.get_survey_dictionary(survey),
        }
        message = f'پرسش‌نامه {survey.name} یافت شد.'
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)

    def put(self, *args, **kwargs):
        try:
            if self.request.query_params:
                name = self.request.query_params.get('name')
                text = self.request.query_params.get('text')
            elif self.request.data:
                name = self.request.data.get('name')
                text = self.request.data.get('text')
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            survey_id = kwargs['survey_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        survey = models.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey = survey.first()

        if self.request.user != survey.user:
            message = "شما امکان ویرایش این پرسش‌نامه را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)
        
        updates = ""
        if name:
            survey.name = name
            updates += "نام، "
        if text:
            survey.text = text
            updates += "توضیحات، "

        if updates:
            message = f"مقادیر ({updates}) با موفقیت ویرایش شد."
            survey.save()
        else:
            message = "مقداری ویرایش نشد."
        return Response({"message": message,}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        try:
            survey_id = kwargs['survey_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        survey = models.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey = survey.first()

        if self.request.user != survey.user:
            message = "شما امکان ویرایش این پرسش‌نامه را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)
        
        survey.delete()

        message = "پرسش‌نامه موردنظر با موفقیت حذف شد."
        return Response({'message': message}, status=status.HTTP_200_OK)

