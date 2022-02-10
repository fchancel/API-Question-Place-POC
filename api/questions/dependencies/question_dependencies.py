from fastapi import Depends, HTTPException, status
from general.dependencies.pagination_dependencies import (
    pagination_param_desc, pagination_parameters)
from questions.nodes.question_node import QuestionNode
from users.dependencies.user_dependencies import GetCurrentUser
from users.nodes.user_node import UserNode


def get_question_dependancie(uid: str):
    question_node = QuestionNode.get_question_with_uid(uid=uid)
    if not question_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return question_node


def owner_question(question_node: QuestionNode = Depends(get_question_dependancie),
                   current_user: UserNode = Depends(GetCurrentUser())):
    if not question_node.created.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not owner")
    return {
        'user': current_user,
        'question': question_node
    }


async def pagination_parameters_question(sort_by: str = 'date',
                                         desc: str = Depends(pagination_param_desc),
                                         param: dict = Depends(pagination_parameters)):
    possibility = {
        'date': 'creator_rel.date',
        'answer': 'nb_answer',
    }
    if sort_by in possibility:
        sort_by = possibility[sort_by]
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
            {
                "loc": [
                    "body",
                    "question_dependencies",
                    "sort_by"
                ],
                "msg": "value is not a valid sort",
                "type": "value_error"
            }
        ])
    param.update({'sort_by': sort_by, 'desc': desc})
    return param
