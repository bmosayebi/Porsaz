from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework import status

from main import models as main
from main import serializers


class SurveyAnswers(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                survey_id = self.request.query_params['survey_id']
            elif self.request.data:
                survey_id = self.request.data['survey_id']
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)
        
        survey = main.Survey.objects.filter(id=survey_id)
        if not survey:
            message = "پرسش‌نامه‌ای یافت نشد."
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        survey = survey[0]

        survey_answer = main.SurveAnswer.objects.create(user=self.request.user, survey=survey)
        survey_answer.save()

        message = "پاسخ پرسش‌نامه با موفقیت ساخته شد."
        data = {
            'survey_answer_id': survey_answer.id,
        }
        return Response({"message": message, 'data': data}, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        survey_answers = request.user.get_survey_answers()
        surveys_count = survey_answers.count()

        survey_list = []
        for survey_answer in survey_answers:
            survey_list.append(serializers.get_survey_answer_dictionary())

        data ={
            'survey_answers': survey_list,
            'count': surveys_count
        }
        message = f'{surveys_count} پاسخ پرسش‌نامه یافت شد'

        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)

class SurveyAnswer(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            survey_answer_id = kwargs['survey_answer_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        survey_answer = main.SurveyAnswer.objects.filter(id=survey_answer_id)
        if not survey_answer:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey_answer = survey_answer.first()

        if survey_answer.user != self.request.user:
            message = "این پاسخ پرسش‌نامه متعلق به شما نمی‌باشد."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)

        data ={
            'survey_answer': serializers.get_survey_answer_dictionary(survey_answer),
        }
        message = "پاسخ پرسش‌نامه یافت شد."
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)



class QuestionAnswer(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        try:
            if self.request.query_params:
                question_id = self.request.query_params['question_id']
                answer = self.request.query_params['answer']
            elif self.request.data:
                question_id = self.request.data['question_id']
                answer = self.request.query_params['answer']
            else:
                message = "پارامتری وجود ندارد."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            survey_answer_id = kwargs['survey_answer_id']
        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
        

        if not self.request.user.is_authenticated:
            message = "لطفا ابتدا وارد شوید."
            return Response({'message': message}, status=status.HTTP_401_UNAUTHORIZED)

        survey_answer = main.SurveyAnswer.objects.filter(id=survey_answer_id)
        if not survey_answer:
            message = "پرسش‌نامه موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        survey_answer = survey_answer.first()

        if survey_answer.user != self.request.user:
            message = "این پاسخ پرسش‌نامه متعلق به شما نمی‌باشد."
            return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)

        question = main.Question.objects.filter(id=question_id)
        if not question:
            message = "سوال موردنظر یافت نشد."
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
        question = question.first()

        try:
            if question.question_type == '1':
                choice = main.QuestionMultipleChoice.objects.filter(id=answer)
                if not choice:
                    message="گزینه مورد نظر یافت نشد."
                    return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
                choice = choice.first()

                if choice.question != question:
                    message="گزینه مورد نظر مربوط به این سوال نیست."
                    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                question_answer = main.QuestionMultipleChoiceAnswer(question=question, survey=survey_answer, answer=choice)
                question_answer.save()

            elif question.question_type == '2':
                if len(answer) > 250:
                    message="حداکثر طول پاسخ ۲۵۰ کاراکتر است."
                    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                question_answer = main.QuestionShortAnswer(question=question, survey=survey_answer, answer=answer)
                question_answer.save()

            elif question.question_type == '3':
                question_answer = main.QuestionLongAnswer(question=question, survey=survey_answer, answer=answer)
                question_answer.save()

            elif question.question_type == '4':
                if not answer.isnumeric():
                    message="پاسخ این سوال باید کاملا عددی باشد."
                    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                question_answer = main.QuestionNumberAnswer(question=question, survey=survey_answer, answer=int(answer))
                question_answer.save()

            elif question.question_type == '5':
                if not answer.isnumeric():
                    message="پاسخ این سوال باید کاملا عددی باشد."
                    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                answer = int(answer)
                if answer > question.star_count:
                    message = f"تعداد ستاره‌های انتخابی باید کمتر از {question.star_count} باشد."
                    return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                question_answer = main.QuestionStarAnswer(question=question, survey=survey_answer, answer=answer)
                question_answer.save()
            
            elif question.question_type == '6':
                for ans in answer:
                    choice = main.QuestionMultipleChoice.objects.filter(id=answer)
                    if not choice:
                        message="گزینه مورد نظر یافت نشد."
                        return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)
                    choice = choice.first()

                    if choice.question != question:
                        message="گزینه مورد نظر مربوط به این سوال نیست."
                        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

                    question_answer = main.QuestionMultipleChoiceAnswer(question=question, survey=survey_answer, answer=choice)
                    question_answer.save()

            else:
                message = "نوع سوال نامعتبر است."
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            message = repr(e)
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        data ={
            'survey_answer': serializers.get_survey_answer_dictionary(survey_answer),
        }
        message = "پاسخ پرسش‌نامه با موفقیت ثبت شد."
        return Response({"message": message, 'data': data}, status=status.HTTP_200_OK)

