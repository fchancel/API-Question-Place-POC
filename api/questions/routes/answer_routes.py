from fastapi import APIRouter, Depends, HTTPException, Response, status
from general.dependencies.pagination_dependencies import pagination_parameters
from neomodel import db
from questions.dependencies.answer_dependencies import (get_answer_dependancie,
                                                        owner_answer)
from questions.nodes.answer_node import AnswerNode
from questions.nodes.comment_node import CommentNode
from questions.schemas.answer_schema import (AnswerPayload, AnswerResponse,
                                             VoteEnum)
from questions.schemas.comment_schema import (CommentPagination,
                                              CommentPayload, CommentResponse)
from questions.services.answer_services import create_simple_answer_response
from questions.services.comment_services import \
    create_comment_pagination_response
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode
from users.schema.user_schema import UserBasicResponse

router = APIRouter(tags={"Question"}, prefix='/answers')


@router.put('/{uid}', status_code=200, response_model=AnswerResponse)
def edit_answer(data_answer: AnswerPayload,
                data: dict = Depends(owner_answer)):
    current_user = data['user']
    answer_node: AnswerNode = data['answer']
    db.begin()
    try:
        results = answer_node.edit_answer(username=current_user.username,
                                          text=data_answer.text)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        response = create_simple_answer_response(results)
        return response


@router.delete("/{uid}", status_code=204)
def delete_answer(data: dict = Depends(owner_answer)):
    answer_node: AnswerNode = data['answer']
    if answer_node.nodes.has(validated=True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="the answer has been validated")
    else:
        db.begin()
        try:
            answer_node.delete_answer()
            db.commit()
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{uid}/vote', status_code=204)
def add_vote(type_vote: VoteEnum,
             answer_node: AnswerNode = Depends(get_answer_dependancie),
             current_user: UserNode = Depends(GetCurrentUser())):
    question_node = answer_node.answer.single()
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if answer_node.voted.is_connected(current_user):
        vote_rel = answer_node.voted.relationship(current_user)
        if vote_rel.type_vote == type_vote.value:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            answer_node.voted.disconnect(current_user)
    db.begin()
    try:
        vote_rel = answer_node.voted.connect(current_user, {'type_vote': type_vote.value})
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/{uid}/vote', status_code=204)
def delete_vote(type_vote: VoteEnum,
                answer_node: AnswerNode = Depends(get_answer_dependancie),
                current_user: UserNode = Depends(GetCurrentUser())):
    question_node = answer_node.answer.single()
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if answer_node.voted.is_connected(current_user):
        answer_node.voted.disconnect(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{uid}/validate', status_code=204)
def validate_answer(answer_node: AnswerNode = Depends(get_answer_dependancie),
                    current_user: UserNode = Depends(GetCurrentUser())):
    question_node = answer_node.answer.single()
    if not question_node.created.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not owner")
    if AnswerNode.get_validated_answer(question_node.uid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="an other answer is already validated")
    else:
        db.begin()
        try:
            answer_node.validated.connect(question_node, {'deprecated': False})
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/{uid}/validate', status_code=204)
def delete_validate_answer(answer_node: AnswerNode = Depends(get_answer_dependancie),
                           current_user: UserNode = Depends(GetCurrentUser())):
    question_node = answer_node.answer.single()
    if not question_node.created.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not owner")
    if not answer_node.validated.relationship(question_node):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="question is not validated")
    else:
        db.begin()
        try:
            answer_node.validated.disconnect(question_node)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/{uid}/comment', status_code=201, response_model=CommentResponse)
def create_comment(data_comment: CommentPayload,
                   answer_node: AnswerNode = Depends(get_answer_dependancie),
                   current_user: UserNode = Depends(GetCurrentUser())):
    question_node = answer_node.answer.single()
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db.begin()
    try:
        comment_node = CommentNode.create_and_save(text=data_comment.text)
        answer_node.comment.connect(comment_node)
        created_rel = comment_node.created.connect(current_user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = CommentResponse(created=created_rel.created,
                               edited=created_rel.edited,
                               author=UserBasicResponse(**current_user.dict()),
                               **comment_node.dict())
    return response


@router.get('/{uid}/comments', status_code=200, response_model=CommentPagination)
def get_comments(param_pagination: dict = Depends(pagination_parameters),
                 answer_node: AnswerNode = Depends(get_answer_dependancie),
                 current_user: UserNode = Depends(GetCurrentUser(auto_error=False))):
    question_node = answer_node.answer.single()
    if question_node.hidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    results = CommentNode.get_all_comments(answer_node.uid,
                                           param_pagination['skip'],
                                           param_pagination['limit'])
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        response = create_comment_pagination_response(results, param_pagination)
        return response
