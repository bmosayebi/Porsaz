from django.shortcuts import render
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token

import http.client
import json
import random
import string

from . import models, serializers


def get_sms_token():
    conn = http.client.HTTPSConnection("restfulsms.com")

    payload = "{\r\n\t\"UserApiKey\":\"ce0d433857024c83db93f3b\",\r\n\t\"SecretKey\":\"1273551893Bb#\"\r\n}\r\n"

    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "54b79b6e-85a7-0794-7b73-69ea5fb8cd7c"
    }

    conn.request("POST", "/api/Token", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return (json.loads(data.decode("utf-8"))['TokenKey'])


def generate_security_code(length):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for i in range(length))
    return code


class SendSMS(APIView):

    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                username = self.request.query_params['username']
            elif self.request.data:
                username = self.request.data['username']
            else:
                message = "پارامتری وجود ندارد"
                return Response({'message': message}, status=400)
        except:
            message = "پارامتری وجود ندارد"
            return Response({'message': message}, status=400)

        if len(username) != 11 or username[:2] != "09" or not username.isnumeric():
            message = "شماره همراه وارد شده معتبر نیست "
            return Response({'message': message}, status=400)

        users = models.UserProfile.objects.filter(username=username)
        if users.count() and users[0].register_complete:
            user = users[0]

            if user.r_code_time:
                td = (timezone.now().timestamp() -
                      user.r_code_time.timestamp())
                if td < 60:
                    message = "ارسال مجدد پس از ۶۰ ثانیه امکان‌پذیر است"
                    return Response({'message': message}, status=400)

            user.r_code_time = timezone.now()
            user.r_code = random.randint(1000, 9999)
            user.save()
            conn = http.client.HTTPSConnection("restfulsms.com")

            payload = {
                        'ParameterArray': [
                            {"Parameter": "VerificationCode","ParameterValue": str(user.r_code)},
                            ],

                        "Mobile": user.username,
                        "TemplateId": "72662",
                    }
            payload = json.dumps(payload)

            headers = {
                    'x-sms-ir-secure-token': get_sms_token(),
                    'content-type': "application/json",
                    'cache-control': "no-cache",
                    'postman-token': "48885b70-56a0-a612-3b1d-ed05385e3f05"
                    }

            conn.request("POST", "/api/UltraFastSend", payload, headers)

            res = conn.getresponse()
            data = res.read()
            message = "کد احراز هویت با موفقیت ارسال شد."
            return Response({'message': message, 'sms_sent': True, 'regsitered': True}, status=200)
        else:
            if users.count():
                user = users[0]
            else:
                user = models.UserProfile(username=username)
            
            if user.r_code_time:
                td = (timezone.now().timestamp() -
                      user.r_code_time.timestamp())
                if td < 60:
                    message = "ارسال مجدد پس از ۶۰ ثانیه امکان‌پذیر است"
                    return Response({'message': message}, status=400)
                    
            user.r_code_time = timezone.now()
            user.r_code = random.randint(1000, 9999)
            user.save()
            conn = http.client.HTTPSConnection("restfulsms.com")

            payload = {
                        'ParameterArray': [
                            { "Parameter": "VerificationCode","ParameterValue": str(user.r_code)},
                            ],

                        "Mobile": user.username,
                        "TemplateId": "72662",
                    }
            payload = json.dumps(payload)

            headers = {
                    'x-sms-ir-secure-token': get_sms_token(),
                    'content-type': "application/json",
                    'cache-control': "no-cache",
                    'postman-token': "48885b70-56a0-a612-3b1d-ed05385e3f05"
                    }

            conn.request("POST", "/api/UltraFastSend", payload, headers)

            res = conn.getresponse()
            data = res.read()
            message = "کد احراز هویت با موفقیت ارسال شد."
            return Response({'message': message, 'sms_sent': True, 'regsitered': False}, status=200)


class ValidateCode(APIView):
    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                username = self.request.query_params['username']
                rcode = self.request.query_params['code']
            elif self.request.data:
                username = self.request.data['username']
                rcode = self.request.data['code']
            else:
                message = "پارامتری وجود ندارد"
                return Response({'message': message}, status=400)
        except:
            message = "پارامترها ناقص است"
            return Response({'message': message}, status=400)

        if len(username) != 11 or username[:2] != "09" or not username.isnumeric():
            message = "شماره همراه وارد شده معتبر نیست "
            return Response({'message': message}, status=400)

        user = models.UserProfile.objects.filter(username=username)

        if user.count():
            user = user[0]
            if int(rcode) == user.r_code:
                user.phone_valid = True
                if user.register_complete:
                    user.save()
                    token, created = Token.objects.get_or_create(user=user)
                    user = serializers.UserReadSerializer(user).data
                    message = "لاگین با موفقیت انجام شد."
                    return Response({'message': message, 'code_valid': True, 'registered': True, 'token': token.key, 'user': user}, status=200)
                
                security_code = generate_security_code(30)
                user.security_code = security_code
                user.save()
                message = "کد احراز هویت صحیح است."
                return Response({'message': message, 'code_valid': True, 'registered': False, 'security_code': security_code}, status=200)
            else:
                message = "کد احراز هویت صحیح نمی‌باشد."
                return Response({'message': message, 'code_valid': False}, status=200)
        else:
            message = "کاربری با این شماره همراه یافت نشد"
            return Response({'message': message}, status=400)

class Register(APIView):
    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                username = self.request.query_params['username']
                security_code = self.request.query_params['security_code']
                first_name = self.request.query_params['first_name']
                last_name = self.request.query_params['last_name']
                goal = self.request.query_params.get('goal')
            elif self.request.data:
                username = self.request.data['username']
                security_code = self.request.data['security_code']
                first_name = self.request.data['first_name']
                last_name = self.request.data['last_name']
                goal = self.request.data.get('goal')
            else:
                message = "پارامتری وجود ندارد"
                return Response({'message': message}, status=400)
        except:
            message = "پارامترها ناقص است"
            return Response({'message': message}, status=400)

        user = models.UserProfile.objects.filter(username = username)

        if user.count() and user[0].phone_valid:
            user = user[0]
            if user.security_code == security_code:
                user.first_name = first_name
                user.last_name = last_name
                
                if goal and goal in ['1', '2', 1, 2]:
                    user.goal = str(goal)
                    
                user.register_complete = True
                user.save()
                token, created = Token.objects.get_or_create(user=user)
                user = serializers.UserReadSerializer(user).data
                message = "کاربر با موفقیت ثبت‌نام شد."
                return Response({'message': message,'registered': True, 'token': token.key, 'user': user}, status=200)
            else:
                message = "کد امنیتی صحیح نمی‌باشد"
                return Response({'message': message}, status=400)
        else:
            message = "کاربری با این شماره همراه یافت نشد"
            return Response({'message': message}, status=400)


class UpdateName(generics.RetrieveUpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            message = "توکن کاربر معتبر نیست"
            return Response({'message': message}, status=400)
        
        user = serializers.UserReadSerializer(self.request.user).data
        message = "اطلاعات کابر به این صورت است."
        return Response({'message': message,'user': user}, status=200)
        
        
        
    def post(self, *args, **kwargs):
        try:
            if self.request.query_params:
                first_name = self.request.query_params['first_name']
                last_name = self.request.query_params['last_name']
            elif self.request.data:
                first_name = self.request.data['first_name']
                last_name = self.request.data['last_name']
            else:
                message = "پارامتری وجود ندارد"
                return Response({'message': message}, status=400)
        except:
            message = "پارامترها ناقص است"
            return Response({'message': message}, status=400)
        
        if not self.request.user.is_authenticated:
            message = "توکن کاربر معتبر نیست"
            return Response({'message': message}, status=400)
            
        user = self.request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        user = serializers.UserReadSerializer(user).data
        message = "اطلاعات کاربر با موفقیت ویرایش شد"
        return Response({'message': message, 'user': user}, status=200)
