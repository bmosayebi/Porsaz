from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.apps import apps

# from main import models as main

"""
User
"""
class UserProfileManager(BaseUserManager):

    def create_user(self, username, first_name, last_name, password = None):
        user = self.model(first_name = first_name, last_name = last_name , username = username)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, username, first_name, last_name , password = None):

        user = self.create_user(username, first_name, last_name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):

    GOAL_CHOICES = (
        ('1', 'کارفرما'),
        ('2', 'کارجو')
    )
    username =  models.CharField(max_length = 20, unique = True, verbose_name = "شماره همراه")
    first_name = models.CharField(max_length = 50, verbose_name = "نام", blank = True, null = True)
    last_name = models.CharField(max_length = 50, verbose_name = "نام خانوادگی", blank = True, null = True)
    goal = models.CharField(max_length=2, blank=True, null=True, verbose_name="هدف ثبت‌نام")
    date_joined = models.DateTimeField(default = timezone.now, verbose_name = "زمان ثبت نام")
    

    is_active = models.BooleanField(default = True, verbose_name = "فعال")
    is_staff = models.BooleanField( default = False)

    r_code = models.DecimalField(decimal_places = 0, max_digits = 6, blank = True, default = 0)
    r_code_time = models.DateTimeField(default = timezone.now())
    phone_valid = models.BooleanField(default=False, verbose_name='تایید شماره همراه')
    security_code = models.CharField(max_length = 50, blank = True, null = True)
    register_complete = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
         verbose_name = 'کاربر'
         verbose_name_plural = 'کاربر ها'
         ordering = ('-date_joined',)

    def get_survey_answers(self):
        return apps.get_model('main.SurveyAnswer').objects.filter(user=self)


    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    