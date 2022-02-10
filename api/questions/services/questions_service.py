from places.schema.place_schema import PlaceResponse
from questions.schemas.question_schema import (QuestionPagination,
                                               QuestionResponse)
from users.nodes.user_node import UserNode
from users.schema.user_schema import UserBasicResponse


def create_question_pagination_response(data: dict, pagination_param: dict, current_user: UserNode):
    response_list = list()
    for i in range(0,  len(data['questions'])):
        if not data['validated'][i]:
            validated = False
            deprecated = False
        else:
            validated = True
            if not data['validated'][i].deprecated:
                deprecated = False
            else:
                deprecated = True
        if not data['questions'][i].follow.is_connected(current_user):
            follow = False
        else:
            follow = True
        response_list.append(QuestionResponse(
            created=data['created_date'][i].created,
            edited=data['created_date'][i].edited,
            number_answers=data['number_answers'][i],
            place=data['places'][i].dict(),
            validated=validated,
            deprecated=deprecated,
            follow=follow,
            author=UserBasicResponse(**data['authors'][i].dict()),
            **data['questions'][i].dict()))

    response = QuestionPagination(skip=pagination_param['skip'],
                                  limit=pagination_param['limit'],
                                  total=data['total_question'],
                                  data=response_list)
    return response


def create_simple_question_response(data: dict, connected: bool, current_user: UserNode):
    if not data['validated']:
        validated = False
        deprecated = False
    else:
        validated = True
        if not data['validated'].deprecated:
            deprecated = False
        else:
            deprecated = True
    if not connected:
        follow = False
    else:
        if not data['question'].follow.is_connected(current_user):
            follow = False
        else:
            follow = True
    response = QuestionResponse(uid=data['question'].uid,
                                title=data['question'].title,
                                text=data['question'].text,
                                slug=data['question'].slug,
                                place=PlaceResponse(**data['place'].dict()),
                                created=data['created_date'].created,
                                edited=data['created_date'].edited,
                                number_answers=data['number_answers'],
                                hidden=data['question'].hidden,
                                validated=validated,
                                deprecated=deprecated,
                                follow=follow,
                                author=UserBasicResponse(**data['author'].dict()))
    return response
