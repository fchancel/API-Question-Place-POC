from fastapi import Depends, HTTPException, status
from general.dependencies.pagination_dependencies import (
    pagination_param_desc, pagination_parameters)


async def pagination_parameters_feedback(sort_by: str = 'rating',
                                         desc: str = Depends(pagination_param_desc), 
                                         param: dict = Depends(pagination_parameters)):
    possibility = {
        'rating': 'feedback.rating',
        'date': 'rel.date',
        'distinction': 'distinction.name'
    }
    if sort_by in possibility:
        sort_by = possibility[sort_by]
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
            {
                "loc": [
                    "body",
                    "feedback_dependencies",
                    "sort_by"
                ],
                "msg": "value is not a valid sort",
                "type": "value_error"
            }
        ])
    param.update({'sort_by': sort_by, 'desc': desc})
    return param
