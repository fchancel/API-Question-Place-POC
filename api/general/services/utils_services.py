import json

from config import get_settings, log
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from pydantic.typing import Any, List


async def send_email(email_body: str, to_email: List[EmailStr], email_subject: str):
    if get_settings().is_dev():
        log.info(email_body)
    else:
        message = MessageSchema(
            subject=email_subject,
            recipients=to_email,
            body=email_body,
            subtype="html"
        )
        fm = FastMail(get_settings().mail_conf)
        await fm.send_message(message)


async def save_json_file(file_name: str, data: Any):
    with open(file_name, 'wb') as my_file:
        json.dump(data, my_file)


def read_json_file(file_name: str):
    try:
        with open(file_name, 'r') as my_file:
            return json.load(my_file)

    except FileNotFoundError:
        return None
