from . import models


def get_survey_dictionary(survey):
    data = {
        'survey_id': survey.id,
        'name': survey.name,
        'text': survey.text
    }
    return data

def get_question_dictionary(question):
    data = {
        'question_id': question.id,
        'survey_id': question.survey.id,
        'question_type': question.question_type,
        'question_type_display': question.get_question_type_display(),
        'title': question.title,
        'number':question.number,
        'subtitle': '',
        'image': '',
        'star_count': '',
    }

    if question.subtitle:
        data['subtitle'] = question.subtitle
    if question.image:
        data['image'] = question.image.url
    if question.star_count:
        data['star_count'] = question.star_count
    return data

def get_question_choice_dictionary(question_choice):
    data = {
        'question_choice_id': question_choice.id,
        'question_id': question_choice.question.id,
        'number': question_choice.number,
        'text': question_choice.text
    }
    return data


def get_survey_answer_dictionary(survey):
    data = {
        'survey_answer_id': survey.id,
        'survey_id': survey.survey.id,
        'created': survey.created,
    }
    return data