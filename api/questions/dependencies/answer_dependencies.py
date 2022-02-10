from fastapi import Depends, HTTPException, status
from general.dependencies.pagination_dependencies import (
    pagination_param_desc, pagination_parameters)
from questions.nodes.answer_node import AnswerNode
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode


def get_answer_dependancie(uid: str):
    answer_node = AnswerNode.get_answer_with_uid(uid=uid)
    if not answer_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return answer_node


def owner_answer(answer_node: AnswerNode = Depends(get_answer_dependancie),
                 current_user: UserNode = Depends(GetCurrentUser())):
    if not answer_node.created.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not owner")
    return {
        'user': current_user,
        'answer': answer_node
    }


async def pagination_parameters_answer(sort_by: str = 'date',
                                       desc: str = Depends(pagination_param_desc),
                                       param: dict = Depends(pagination_parameters)):
    possibility = {
        'date': 'created_rel.date',
        'comment': 'number_comments',
        'vote': 'total_vote',
    }
    if sort_by in possibility:
        sort_by = possibility[sort_by]
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
            {
                "loc": [
                    "body",
                    "answer_dependencies",
                    "sort_by"
                ],
                "msg": "value is not a valid sort",
                "type": "value_error"
            }
        ])
    param.update({'sort_by': sort_by, 'desc': desc})
    return param
