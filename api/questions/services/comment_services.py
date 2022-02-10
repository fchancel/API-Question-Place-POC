from questions.schemas.comment_schema import CommentPagination, CommentResponse
from users.schema.user_schema import UserBasicResponse


def create_comment_pagination_response(data: dict, pagination_param: dict):
    response_list = list()
    for i in range(0,  len(data['comments'])):
        response_list.append(CommentResponse(uid=data['comments'][i].uid,
                                             text=data['comments'][i].text,
                                             created=data['created_date'][i].created,
                                             edited=data['created_date'][i].edited,
                                             author=UserBasicResponse(**data['authors'][i].dict())))

    response = CommentPagination(skip=pagination_param['skip'],
                                 limit=pagination_param['limit'],
                                 total=data['total_comments'],
                                 data=response_list)
    return response


def create_simple_comment_response(data: dict):
    response = CommentResponse(uid=data['comment'].uid,
                               text=data['comment'].text,
                               created=data['created_date'].created,
                               edited=data['created_date'].edited,
                               author=UserBasicResponse(**data['author'].dict()))
    return response
