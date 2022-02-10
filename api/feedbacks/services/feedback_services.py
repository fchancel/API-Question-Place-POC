from feedbacks.schema.feedback_schema import (FeedbackPagination,
                                              FeedbackWithUser)
from users.schema.user_schema import UserBasicResponse


def create_feedback_pagination_response(data: dict, pagination_param: dict):
    response_list = list()
    for i in range(0,  len(data['feedbacks'])):
        response_list.append(FeedbackWithUser(
            date=data['created_date'][i],
            place=data['places'][i].dict(),
            distinction=data['distinctions'][i].dict(),
            user=UserBasicResponse(**data['users'][i].dict()),
            **data['feedbacks'][i].dict()))

    response = FeedbackPagination(skip=pagination_param['skip'],
                                  limit=pagination_param['limit'],
                                  total=data['total_feedbacks'],
                                  data=response_list)
    return response
