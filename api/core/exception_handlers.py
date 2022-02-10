# from fastapi import Request, status
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse


# async def validation_exception_handler(request: Request, exc: RequestValidationError):

#     errors = []
#     for original_error in exc.errors():
#         error = {}
#         error["location"] = original_error["loc"][-1]
#         error["message"] = original_error["msg"]
#         error["type"] = original_error["type"]
#         errors.append(error)
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={"error": errors})
