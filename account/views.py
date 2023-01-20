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

