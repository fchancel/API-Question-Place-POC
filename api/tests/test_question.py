import copy
import datetime

import pytest
from config import get_settings
from fastapi import Response
from users.nodes.user_node import UserNode
from users.services.user_services import create_access_token


@pytest.fixture(scope="module")
def get_user1(test_app):
    user_payload = {'user_payload': {'email': 'florian.chancelade@gmail.com',
                                     'password': 'Password123',
                                     'password2': 'Password123',
                                     'first_name': 'Florian',
                                     'last_name': 'Chancelade'
                                     },
                    'profile_payload': {'gender': 'M',
                                        'birthdate': '1993-03-12'}}
    user = UserNode.get_node_with_email(user_payload['user_payload']['email'])
    if not user:
        user = test_app.post('api/users', json=user_payload)
        user = UserNode.get_node_with_email(user_payload['user_payload']['email'])
        user.email_verified = True
        user.save()
    settings = get_settings()
    access_token_expires = datetime.timedelta(minutes=settings.access_token_expire_minutes_mail)
    access_token = create_access_token(data={"uid": user.uid}, expires_delta=access_token_expires)
    return (user, access_token)


@pytest.fixture(scope="module")
def get_user2(test_app):
    user_payload = {'user_payload': {'email': 'renaud.cepre@gmail.com',
                                     'password': 'Password123',
                                     'password2': 'Password123',
                                     'first_name': 'Renaud',
                                     'last_name': 'Cepre'
                                     },
                    'profile_payload': {'gender': 'M',
                                        'birthdate': '1991-08-05'}}
    user = UserNode.get_node_with_email(user_payload['user_payload']['email'])
    if not user:
        user = test_app.post('api/users', json=user_payload)
        user = UserNode.get_node_with_email(user_payload['user_payload']['email'])
        user.email_verified = True
        user.save()
    settings = get_settings()
    access_token_expires = datetime.timedelta(minutes=settings.access_token_expire_minutes_mail)
    access_token = create_access_token(data={"uid": user.uid}, expires_delta=access_token_expires)
    return (user, access_token)


class TestQuestion:
    url = 'api/questions/'

    question_payload = {'title': 'Testing',
                        'text': 'we are testing',
                        'place': {
                            'google_place_id': 'world'
                        }}

    @pytest.mark.parametrize("title", ['', ' ', '      ', 'a', 'ab', 'abc'])
    def test_invalid_title(self, get_user1, test_app, title):
        headers = {"Authorization": f"Bearer {get_user1[1]}"}
        payload = copy.deepcopy(self.question_payload)
        payload['title'] = title
        print('HEEEEEEEEEEEEEEEEEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
        print(headers)
        response = test_app.post(self.url, json=payload, headers=headers)
        assert response.status_code == 422
        # assert response.json()[
        # 'detail'][0]['msg'] == 'value is not a valid email address'
