from fastapi import APIRouter, Depends, HTTPException, Response, status
from general.dependencies.pagination_dependencies import (
    pagination_param_desc, pagination_parameters)
from neomodel import db
from places.nodes.place_node import PlaceNode
from places.schema.place_schema import PlaceResponse
from questions.dependencies.answer_dependencies import \
    pagination_parameters_answer
from questions.dependencies.question_dependencies import (
    get_question_dependancie, owner_question, pagination_parameters_question)
from questions.nodes.answer_node import AnswerNode
from questions.nodes.question_node import QuestionNode
from questions.schemas.answer_schema import (AnswerPagination, AnswerPayload,
                                             AnswerResponse)
from questions.schemas.question_schema import (QuestionPagination,
                                               QuestionPayload,
                                               QuestionResponse)
from questions.services.answer_services import \
    create_answer_pagination_response
from questions.services.questions_service import (
    create_question_pagination_response, create_simple_question_response)
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode
from users.schema.user_schema import UserBasicResponse

router = APIRouter(tags={"Question"}, prefix='/questions')


@router.post('/', status_code=201, response_model=QuestionResponse)
def create_question(question_data: QuestionPayload,
                    current_user: UserNode = Depends(GetCurrentUser())):
    db.begin()
    try:
        question_node = QuestionNode.create_and_save(title=question_data.title, text=question_data.text)

        created_rel = question_node.created.connect(current_user)
        place_rel = question_node.place.connect(
            PlaceNode.get_or_create_node_with_google_place_id(question_data.place.google_place_id))

        place_str = place_rel.end_node().google_place_id

        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    place = PlaceResponse(google_place_id=place_str)
    response = QuestionResponse(created=created_rel.created,
                                edited=created_rel.edited,
                                place=place,
                                number_answers=0,
                                validated=False,
                                deprecated=False,
                                follow=False,
                                author=UserBasicResponse(**current_user.dict()),
                                **question_node.dict())
    return response


@router.get('/mine', response_model=QuestionPagination,  status_code=200)
def get_my_questions(param_pagination: dict = Depends(pagination_parameters_question),
                     current_user: UserNode = Depends(GetCurrentUser())):
    results = QuestionNode.get_mine_questions(username=current_user.username,
                                              skip=param_pagination['skip'],
                                              limit=param_pagination['limit'],
                                              sort_by=param_pagination['sort_by'],
                                              desc=param_pagination['desc'])
    if not results:
        return QuestionPagination(skip=param_pagination['skip'],
                                  limit=param_pagination['limit'],
                                  total=0,
                                  data=[])
    else:
        return create_question_pagination_response(results, param_pagination, current_user)


@ router.get('/follow',  status_code=200, response_model=QuestionPagination)
def get_followed_questions(desc: str = Depends(pagination_param_desc),
                           param_pagination: dict = Depends(pagination_parameters),
                           current_user: UserNode = Depends(GetCurrentUser())):
    results = QuestionNode.get_followed_questions(username=current_user.username,
                                                  skip=param_pagination['skip'],
                                                  limit=param_pagination['limit'],
                                                  desc=desc)
    if not results:
        return QuestionPagination(skip=param_pagination['skip'],
                                  limit=param_pagination['limit'],
                                  total=0,
                                  data=[])
    else:
        return create_question_pagination_response(results, param_pagination, current_user)


@ router.get('/{uid}', status_code=200, response_model=QuestionResponse)
def get_question(uid: str, current_user=Depends(GetCurrentUser(auto_error=False))):
    results = QuestionNode.get_question_complete_response(uid)
    if results['question'].hidden:
        if not results['question'].created.is_connected(current_user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        if not current_user:
            connected = False
        else:
            connected = True
        response = create_simple_question_response(results, connected, current_user)
    return response


@ router.put('/{uid}', status_code=200, response_model=QuestionResponse)
def edit_question(data_question: QuestionPayload,
                  data: dict = Depends(owner_question)):
    current_user = data['user']
    question_node = data['question']
    db.begin()
    try:
        results = question_node.edit_question(username=current_user.username,
                                              title=data_question.title,
                                              text=data_question.text,
                                              google_place_id=data_question.place.google_place_id)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        response = create_simple_question_response(results, True, current_user)
    return response


@ router.put('/{uid}/undelete',  status_code=200, response_model=QuestionResponse)
def undelete_question(data: dict = Depends(owner_question)):
    question_node = data['question']
    current_user = data['user']
    db.begin()
    try:
        question_node.hidden = False
        question_node.save()
        results = QuestionNode.get_question_complete_response(question_node.uid)
        if not results:
            raise
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response = create_simple_question_response(results, True, current_user)
    return response


@ router.delete('/{uid}',  status_code=200, response_model=QuestionResponse)
def delete_question(data: dict = Depends(owner_question)):
    question_node = data['question']
    current_user = data['user']
    db.begin()
    try:
        question_node.hidden = True
        question_node.follow.disconnect_all()
        question_node.save()
        results = QuestionNode.get_question_complete_response(question_node.uid)
        if not results:
            raise
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response = create_simple_question_response(results, True, current_user)
    return response


@ router.put('/{uid}/follow', status_code=204)
def bookmark(question_node: QuestionNode = Depends(get_question_dependancie),
             current_user: UserNode = Depends(GetCurrentUser())):
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if question_node.follow.is_connected(current_user):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        db.begin()
        try:
            question_node.follow.connect(current_user)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@ router.delete('/{uid}/follow', status_code=204)
def delete_bookmark(question_node: QuestionNode = Depends(get_question_dependancie),
                    current_user: UserNode = Depends(GetCurrentUser())):
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not question_node.follow.is_connected(current_user):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        db.begin()
        try:
            question_node.follow.disconnect(current_user)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@ router.post('/{uid}/answer', status_code=201, response_model=AnswerResponse)
def create_answer(data_answer: AnswerPayload,
                  question_node: QuestionNode = Depends(get_question_dependancie),
                  current_user: UserNode = Depends(GetCurrentUser())):
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    db.begin()
    try:
        answer_node = AnswerNode.create_and_save(text=data_answer.text)
        rel = answer_node.created.connect(current_user)
        answer_node.answer.connect(question_node)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    response = AnswerResponse(question_uid=question_node.uid,
                              created=rel.created,
                              edited=rel.edited,
                              vote=0,
                              validated=False,
                              deprecated=False,
                              number_comments=0,
                              author=UserBasicResponse(**current_user.dict()),
                              **answer_node.dict())
    return response


@ router.get('/{uid}/answers', status_code=200, response_model=AnswerPagination)
def get_answers(param_pagination: dict = Depends(pagination_parameters_answer),
                question_node: QuestionNode = Depends(get_question_dependancie),
                current_user: UserNode = Depends(GetCurrentUser(auto_error=False))):
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    results = AnswerNode.get_all_answers(question_node.uid, param_pagination['skip'],
                                         param_pagination['limit'],
                                         param_pagination['sort_by'],
                                         param_pagination['desc'])
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        response = create_answer_pagination_response(results, param_pagination)
        return response
