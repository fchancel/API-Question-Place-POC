from questions.schemas.answer_schema import AnswerPagination, AnswerResponse
from users.schema.user_schema import UserBasicResponse


def create_answer_pagination_response(data: dict, pagination_param: dict):
    response_list = list()
    for i in range(0,  len(data['answers'])):
        if not data['validated'][i]:
            validated = False
            deprecated = False
        else:
            validated = True
            if not data['validated'][i].deprecated:
                deprecated = False
            else:
                deprecated = True
        response_list.append(AnswerResponse(uid=data['answers'][i].uid,
                                            text=data['answers'][i].text,
                                            created=data['created_date'][i].created,
                                            edited=data['created_date'][i].edited,
                                            number_comments=data['number_comments'][i],
                                            vote=data['total_vote'][i],
                                            validated=validated,
                                            deprecated=deprecated,
                                            author=UserBasicResponse(**data['authors'][i].dict())))

    response = AnswerPagination(skip=pagination_param['skip'],
                                limit=pagination_param['limit'],
                                total=data['total_answers'],
                                data=response_list)
    return response


def create_simple_answer_response(data: dict):
    if not data['validated']:
        validated = False
        deprecated = False
    else:
        validated = True
        if not data['validated'].deprecated:
            deprecated = False
        else:
            deprecated = True

    response = AnswerResponse(uid=data['answer'].uid,
                              text=data['answer'].text,
                              created=data['created_date'].created,
                              edited=data['created_date'].edited,
                              number_comments=data['number_comments'],
                              vote=data['total_vote'],
                              validated=validated,
                              deprecated=deprecated,
                              author=UserBasicResponse(**data['author'].dict()))
    return response
