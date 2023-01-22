from django.contrib import admin

from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin	
    
from . import models


class QuestionInline(StackedInlineJalaliMixin, admin.StackedInline):
    model = models.Question
    extra = 0
    classes = ['collapse', ]

class SurveyAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['name', 'user', 'get_created']
    search_fields = ['user', 'name', 'text']

    inlines = [QuestionInline, ]

    def get_created(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')
	
    get_created.short_description = 'زمان ایجاد'
    get_created.admin_order_field = 'created'


class QuestionMultipleChoiceInline(StackedInlineJalaliMixin, admin.StackedInline):
    model = models.QuestionMultipleChoice
    extra = 0
    classes = ['collapse', ]

class QuestionAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['title', 'number', 'survey', 'question_type']
    list_filter = ['question_type']
    search_fields = ['title', 'survey__name']

    inlines = [QuestionMultipleChoiceInline, ]


class QuestionMultipleChoiceAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['text', 'number', 'question']
    search_fields = ['text']


class QuestionMultipleChoiceAnswerInline(admin.TabularInline):
    model = models.QuestionMultipleChoiceAnswer
    extra = 0
    classes = ['collapse', ]

class SurveyAnswerAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['survey', 'user', 'get_created']

    inlines = [QuestionMultipleChoiceAnswerInline, ]

    def get_created(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')
	
    get_created.short_description = 'زمان ایجاد'
    get_created.admin_order_field = 'created'


admin.site.register(models.Survey, SurveyAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.QuestionMultipleChoice, QuestionMultipleChoiceAdmin)
admin.site.register(models.SurveyAnswer, SurveyAnswerAdmin)


