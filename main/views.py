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


class Questions(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                survey_id = self.request.query_params['survey_id']
                question_type = self.request.query_params['question_type']
                title = self.request.query_params['title']
                number = self.request.query_params['number']
                subtitle = self.request.query_params.get('subtitle')
                star_count = self.request.query_params.get('star_count')
            elif self.request.data:
                survey_id = self.request.data['survey_id']
                question_type = self.request.data['question_type']
                title = self.request.data['title']
                number = self.request.data['number']
                subtitle = self.request.data.get('subtitle')
                star_count = self.request.data.get('star_count')
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
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
            message = "شما امکان اضافه کردن سوال به این پرسش‌نامه را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)
        
        if question_type < '1' or question_type > '6':
            message = "نوع سوال نامعتبر است."
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if question_type == '6' and (not star_count or not star_count.isnumeric()):
            message = "تعداد ستاره‌ها نامعتبر است."
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        qs = survey.questions.all()
        for q in qs:
            print(q.number, '==', number)
            if str(q.number) == str(number):
                message = "شماره سوال موردنظر تکراری است."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        question = models.Question.objects.create(survey=survey, question_type=question_type, title=title, number=number)
        if subtitle:
            question.subtitle = subtitle
        if question_type == '6' and star_count:
            star_count = star_count
        question.save()
        
        message = f"سوال با موفقیت به پرسش‌نامه {survey.name} اضافه شد."
        data = {
            'question': serializers.get_question_dictionary(question),
        }
        return Response({"message": message, 'data': data}, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        try:
            if self.request.query_params:
                survey_id = self.request.query_params['survey_id']
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        survey = models.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey = survey.first()

        questions = []
        for question in survey.questions.all():
            questions.append(serializers.get_question_dictionary(question))
        
        data ={
            'survey_id': survey.id,
            'questions': questions
        }
        message = f'{len(questions)} سوال یافت شد.'
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)

class Question(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, *args, **kwargs):
        try:
            question_id = kwargs['question_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        question = models.Question.objects.filter(id=question_id)
        if not question:
            message = "سوال موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        question = question.first()

        data = {
            'question': serializers.get_question_dictionary(question),
        }
        message = "سوال یافت شد."
        return Response({'message': message, 'data':data}, status=status.HTTP_200_OK)

    
    def put(self, *args, **kwargs):
        try:
            if self.request.query_params:
                number = self.request.query_params.get('number')
                question_type = self.request.query_params.get('question_type')
                title = self.request.query_params.get('title')
                subtitle = self.request.query_params.get('subtitle')
                star_count = self.request.query_params.get('star_count')
            elif self.request.data:
                number = self.request.data.get('number')
                question_type = self.request.data.get('question_type')
                title = self.request.data.get('title')
                subtitle = self.request.data.get('subtitle')
                star_count = self.request.data.get('star_count')
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

            question_id = kwargs['question_id']
            
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        question = models.Question.objects.filter(id=question_id)
        if not question:
            message = "سوال موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        question = question.first()

        survey = question.survey
        if self.request.user != survey.user:
            message = "شما امکان ویرایش این سوال را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)
        
        updates = ""
        if number:
            question.number = number
            updates += "شماره سوال، "
        if question_type:
            if not (question_type == '6' and (not star_count or not star_count.isnumeric()) ):
                question.question_type = question_type
                updates += "نوع سوال، "
        
        if title:
            question.title = title
            updates += " متن سوال، "
        if subtitle:
            question.subtitle = subtitle
            updates += "توضیحات سوال، "
        if star_count and star_count.isnumeric() and question_type == '6':
            question.star_count = star_count
            updates += "تعداد ستاره، "
        
        if updates:
            message = f"مقادیر ({updates}) با موفقیت ویرایش شد."
            question.save()
        else:
            message = "مقداری ویرایش نشد."
        
        return Response({'message': message}, status=status.HTTP_200_OK)
        
    def delete(self, request, *args, **kwargs):
        try:
            question_id = kwargs['question_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        question = models.Question.objects.filter(id=question_id)
        if not question:
            message = "سوال موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        question = question.first()

        if self.request.user != question.survey.user:
            message = "شما امکان ویرایش این سوال را ندارید."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)
        
        question.delete()

        message = "سوال موردنظر با موفقیت حذف شد."
        return Response({'message': message}, status=status.HTTP_200_OK)

