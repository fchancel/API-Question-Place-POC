import re

from users.nodes.user_node import UserNode


def password_validator(password):
    # ?# REGEX PASSWORD : minimum 8 characters, 1 lowercase, 1 uppercase,
    # ?# 1 digits and can contain @$!%*?.&()[]{}
    regex_password = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$&+=-_!%*?.()\[\]{}]{8,}"
    pattern_password = re.compile(regex_password)

    if not pattern_password.match(password):
        raise ValueError(
            """value is not a valid password""")
    return password


def passwords_match(password2, values, **kwargs):
    if 'password' in values and password2 != values['password']:
        raise ValueError('passwords do not match')
    return password2


def unique_email(email):
    email = email.strip(' ')
    email = email.lower()
    user = UserNode.nodes.first_or_none(email=email)
    if user:
        raise ValueError(
            'value is not unique')
    return email
