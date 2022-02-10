from fastapi import HTTPException, status


async def pagination_param_desc(desc: bool = False):
    if desc:
        desc = "desc"
    else:
        desc = ""
    return desc


async def pagination_parameters(skip: int = 0, limit: int = 10):
    if skip < 0:
        skip = 0
    if limit <= 0:
        limit = 10
    if skip >= limit:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
            {
                "loc": [
                    "body",
                    "pagination_dependencies",
                    "skip / limit"
                ],
                "msg": "value is not a valid sort",
                "type": "value_error"
            }
        ])
    return {"skip": skip, "limit": limit}
