
from fastapi import APIRouter, Depends, HTTPException, responses, status
from feedbacks.dependencies.feedback_dependencies import \
    pagination_parameters_feedback
from feedbacks.nodes.distinction_node import DistinctionNode
from feedbacks.nodes.feedback_node import FeedbackNode
from feedbacks.schema.distinction_schema import (DistinctionNumber,
                                                 DistinctionResponse)
from feedbacks.schema.feedback_schema import (FeedbackPagination,
                                              FeedbackPayload,
                                              FeedbackRatingWithNumber,
                                              FeedbackResponse,
                                              FeedbacksNumber)
from feedbacks.services.feedback_services import \
    create_feedback_pagination_response
from places.nodes.place_node import PlaceNode
from places.schema.place_schema import PlaceResponse
from pydantic.typing import Dict, List
from users.dependencies.user_dependencies import (GetCurrentUser,
                                                  get_target_user)
from users.nodes.user_node import UserNode

router = APIRouter(tags={"Feedback"}, prefix='/feedbacks')


@router.post('', response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED,
             summary='Create a new feedback between two users')
def create_feedback(feedback: FeedbackPayload,
                    user_receiver: UserNode = Depends(get_target_user),
                    user_giver: UserNode = Depends(GetCurrentUser())
                    ):

    if user_giver == user_receiver:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="you can't feedback yourself.")
    feedback_node = FeedbackNode.create_and_save(rating=feedback.rating,
                                                 comment=feedback.comment)

    distinction_rel = feedback_node.distinction.connect(
        DistinctionNode.get_node_with_name(name=feedback.distinction.name))
    place_rel = feedback_node.place.connect(
        PlaceNode.get_or_create_node_with_google_place_id(feedback.place.google_place_id))
    received_rel = feedback_node.user_receveid.connect(user_receiver)
    feedback_node.user_given.connect(user_giver)
    distinction_response = DistinctionResponse(name=distinction_rel.end_node().name)
    place_response = PlaceResponse(google_place_id=place_rel.end_node().google_place_id)
    created_date = received_rel.date
    response = FeedbackResponse(distinction=distinction_response,
                                date=created_date,
                                place=place_response,
                                **feedback_node.dict())
    return response


@ router.get('/received', response_model=FeedbackPagination, status_code=200,
             summary="List the feedbacks received according to the given page")
def list_feedback_received(username_target: str,
                           pagination_param: Dict = Depends(pagination_parameters_feedback),
                           user_connect: UserNode = Depends(GetCurrentUser())):

    result = FeedbackNode.get_feedbacks(True,
                                        username_target,
                                        pagination_param['skip'],
                                        pagination_param['limit'],
                                        pagination_param['sort_by'],
                                        pagination_param['desc'])

    if not result:
        if UserNode.get_user_actif_only_with_username(username_target):
            return responses.JSONResponse({}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return create_feedback_pagination_response(result, pagination_param)


@ router.get('/given', response_model=FeedbackPagination, status_code=200,
             summary="List the feedbacks given according to the given page")
def list_feedback_given(username_target: str,
                        pagination_param: Dict = Depends(pagination_parameters_feedback),
                        user_connect: UserNode = Depends(GetCurrentUser())):
    result = FeedbackNode.get_feedbacks(False,
                                        username_target,
                                        pagination_param['page'],
                                        pagination_param['per_page'],
                                        pagination_param['sort_by'],
                                        pagination_param['desc'])

    if not result:
        if UserNode.get_user_actif_only_with_username(username_target):
            return responses.JSONResponse({}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return create_feedback_pagination_response(result, pagination_param)


@ router.get('/received/numbers', response_model=FeedbacksNumber, status_code=200)
def how_many_feedbacks_receiver(username_target: str,
                                user_connect: UserNode = Depends(GetCurrentUser())):

    result = FeedbackNode.get_how_many_feedbacks(receiver=True, username=username_target)
    numbers = FeedbacksNumber(number=result)
    return numbers


@ router.get('/given/numbers', response_model=FeedbacksNumber, status_code=200)
def how_many_feedbacks_given(username_target: str,
                             user_connect: UserNode = Depends(GetCurrentUser())):
    result = FeedbackNode.get_how_many_feedbacks(receiver=False, username=username_target)
    if not result:
        if UserNode.get_user_actif_only_with_username(username_target):
            return responses.JSONResponse({}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    numbers = FeedbacksNumber(number=result)
    return numbers


@ router.get('/distinctions', response_model=List[DistinctionNumber], status_code=200,
             summary="Retrieve the distinction with the number that the username has")
def get_distinctions(username_target: str,
                     user_connect: UserNode = Depends(GetCurrentUser())):
    results = DistinctionNode.get_distinctions_number(username_target)
    if not results:
        if UserNode.get_user_actif_only_with_username(username_target):
            return responses.JSONResponse({}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        result_list = list()
        for i in range(0,  len(results['distinctions'])):
            result_list.append(DistinctionNumber(name=results['distinctions'][i],
                                                 number=results['numbers'][i]))
        return result_list


@ router.get('/ratings', response_model=List[FeedbackRatingWithNumber], status_code=200,
             summary="Retrieve the rating with the number that the username has")
def get_ratings(username_target: str,
                user_connect: UserNode = Depends(GetCurrentUser())):
    results = FeedbackNode.get_how_many_rating(username_target)
    if not results:
        if UserNode.get_user_actif_only_with_username(username_target):
            return responses.JSONResponse({}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        result_list = list()
        for i in range(0,  len(results['ratings'])):
            result_list.append(FeedbackRatingWithNumber(rating=results['ratings'][i],
                                                        number=results['numbers'][i]))
        return result_list
