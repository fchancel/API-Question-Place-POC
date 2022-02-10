from fastapi import APIRouter, Depends, HTTPException, Response, status
from neomodel import db
from questions.dependencies.comment_dependencies import owner_comment
from questions.nodes.comment_node import CommentNode
from questions.schemas.comment_schema import CommentPayload, CommentResponse
from questions.services.comment_services import create_simple_comment_response

router = APIRouter(tags={"Question"}, prefix='/comments')


@router.put('/{uid}', status_code=200, response_model=CommentResponse)
def edit_comment(data_comment: CommentPayload,
                 data: dict = Depends(owner_comment)):
    current_user = data['user']
    comment_node: CommentNode = data['comment']
    db.begin()
    try:
        result = comment_node.edit_comment(current_user.username, data_comment.text)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response = create_simple_comment_response(result)
    return response


@router.delete('/{uid}', status_code=204)
def delete_comment(data: dict = Depends(owner_comment)):
    comment_node: CommentNode = data['comment']
    db.begin()
    try:
        comment_node.delete_comment()
        db.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
