from django.db import models
from django.utils import timezone

from account import models as account


class Survey(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="زمان ایجاد")
    user = models.ForeignKey(account.UserProfile, on_delete=models.CASCADE, verbose_name="کاربر سازنده")
    name = models.CharField(max_length=255, verbose_name="نام")
    text = models.TextField(verbose_name="توضیحات")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پرسش‌نامه"
        verbose_name_plural="پرسش‌نامه‌ها"
        ordering = ('-created',)
    

class Question(models.Model):
    QUESTION_TYPE = (
        ('1', 'چند گزینه‌ای'),
        ('2', 'متنی کوتاه‌پاسخ'),
        ('3', 'متنی بلند‌پاسخ'),
        ('4', 'عددی'),
        ('5', 'چند‌گزینه‌ای (انتخاب چند گزینه همزمان)'),
        ('6', 'امتیازدهی (با ستاره)'),
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions", verbose_name="پرسش‌نامه")
    number = models.PositiveIntegerField(verbose_name="شماره سوال")
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE, verbose_name="نوع سوال")
    title = models.TextField(verbose_name="متن سوال")
    subtitle = models.TextField(blank=True, null=True, verbose_name="توضیحات سوال")
    image = models.FileField(upload_to='questions/files/', blank=True, null=True, verbose_name="فایل سوال")
    star_count = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="تعداد ستاره")
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural="سوال‌ها"
        ordering = ('number', )


class QuestionMultipleChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='multiple_choices', verbose_name="سوال")
    number = models.PositiveIntegerField(verbose_name="شماره گزینه")
    text = models.CharField(max_length=255, verbose_name="متن گزینه")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "گزینه سوال چند گزینه‌ای"
        verbose_name_plural = "گزینه‌های سوال چند گزینه‌ای"
        ordering = ('number', )


class SurveyAnswer(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name="زمان ایجاد")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="answers", verbose_name="پرسش‌نامه")
    user = models.ForeignKey(account.UserProfile, on_delete=models.CASCADE, related_name="answers", verbose_name="کاربر پاسخ‌دهنده")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ پرسش‌نامه"
        verbose_name_plural="پاسخ‌های پرسش‌نامه"


class QuestionMultipleChoiceAnswer(models.Model):
    survey = models.ForeignKey(SurveyAnswer, on_delete=models.CASCADE, related_name='multiple_choice_answers', verbose_name="پاسخ پرسش‌نامه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='multiple_choice_answers', verbose_name="سوال")
    answer = models.ForeignKey(QuestionMultipleChoice, on_delete=models.CASCADE, related_name='multiple_choice_answers', verbose_name="پاسخ")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ گزینه سوال چند گزینه‌ای"
        verbose_name_plural = "پاسخ‌های گزینه سوال چند گزینه‌ای"



class QuestionShortAnswer(models.Model):
    survey = models.ForeignKey(SurveyAnswer, on_delete=models.CASCADE, related_name='short_answer_answers', verbose_name="پاسخ پرسش‌نامه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='short_answer_answers', verbose_name="سوال")
    answer = models.CharField(max_length=255, verbose_name="پاسخ")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ سوال کوتاه‌پاسخ"
        verbose_name_plural = "پاسخ‌های سوال کوتاه‌پاسخ"


class QuestionLongAnswer(models.Model):
    survey = models.ForeignKey(SurveyAnswer, on_delete=models.CASCADE, related_name='long_answer_answers', verbose_name="پاسخ پرسش‌نامه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='long_answer_answers', verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ سوال بلند‌پاسخ"
        verbose_name_plural = "پاسخ‌های سوال بلند‌پاسخ"


class QuestionNumberAnswer(models.Model):
    survey = models.ForeignKey(SurveyAnswer, on_delete=models.CASCADE, related_name='number_answers', verbose_name="پاسخ پرسش‌نامه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='number_answers', verbose_name="سوال")
    answer = models.IntegerField(verbose_name="پاسخ")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ سوال عددی"
        verbose_name_plural = "پاسخ‌های سوال عددی"


class QuestionStarAnswer(models.Model):
    survey = models.ForeignKey(SurveyAnswer, on_delete=models.CASCADE, related_name='star_answers', verbose_name="پاسخ پرسش‌نامه")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='start_answers', verbose_name="سوال")
    answer = models.PositiveSmallIntegerField(verbose_name="پاسخ")


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "پاسخ سوال ستاره‌ای"
        verbose_name_plural = "پاسخ‌های سوال ستاره‌ای"