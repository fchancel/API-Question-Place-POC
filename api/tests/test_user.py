import copy
import datetime
import time

import pytest
from config import get_settings
from users.nodes.user_node import UserNode
from users.services.user_services import create_access_token


class TestCreateUser:
    url = 'api/users'
    user_payload = {'user_payload': {'email': 'johnsmith@test.fr',
                                     'password': 'Password123',
                                     'password2': 'Password123',
                                     'first_name': 'John',
                                     'last_name': 'Smith'
                                     },
                    'profile_payload': {'gender': 'M',
                                        'birthdate': '2000-01-01'}}

    @pytest.mark.parametrize("email", ['test', 'test@', 'test@test', 'test@test.', '', ' '])
    def test_invalid_mail(self, test_app, email):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = email
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == 'value is not a valid email address'

    @pytest.mark.parametrize("password", ['', ' ', 'test', 'testtest', 'Testtest', 'Test123', 'TESTTEST', '12345678',
                                          'test1234', 'TEST1234', '        '])
    def test_invalid_password(self, test_app, random_email, password):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['user_payload']['password'] = password
        payload['user_payload']['password2'] = password
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == 'value is not a valid password'

    @pytest.mark.parametrize("password, password2", [('Test1234', 'Test1233')])
    def test_invalid_password_match(self, test_app, random_email, password, password2):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['user_payload']['password'] = password
        payload['user_payload']['password2'] = password2
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == 'passwords do not match'

    @pytest.mark.parametrize("first_name", ['', '   ', '-', '--', '- -', 'J', 'li-a', 'Bruce--Lee', 'Bruce- Lee',
                                            'Bruce  Lee', 'Bruce-Lee--l', 'Bruce@lee', 'Bruce_Lee'])
    def test_invalid_first_name(self, test_app, random_email, first_name):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['user_payload']['first_name'] = first_name
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == 'value is not a valid name'

    @pytest.mark.parametrize("last_name", ['', '   ', '-', '--', '- -', 'J', 'li-a', 'Bruce--Lee', 'Bruce- Lee',
                                               'Bruce  Lee', 'Bruce-Lee--l', 'Bruce@lee', 'Bruce_Lee'])
    def test_invalid_last_name(self, test_app, random_email, last_name):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['user_payload']['last_name'] = last_name
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == 'value is not a valid name'

    @pytest.mark.parametrize("gender", ['R', '', 'm'])
    def test_invalid_gender(self, test_app, random_email, gender):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['profile_payload']['gender'] = gender
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == "value is not a valid enumeration member; permitted: 'M', 'F', 'O'"

    @pytest.mark.parametrize("birthdate", ['20-02-21', '1990-14-13'])
    def test_invalid_format_birthdate(self, test_app, random_email, birthdate):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['profile_payload']['birthdate'] = birthdate
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == "invalid date format"

    @pytest.mark.parametrize("birthdate", ['2016-01-01'])
    def test_invalid_birthdate(self, test_app, random_email, birthdate):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = random_email
        payload['profile_payload']['birthdate'] = birthdate
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == "user is too young"

    def test_create_user(self, test_app, random_email):
        response = test_app.post(self.url, json=self.user_payload)

        assert response.status_code == 201
        assert response.json() == {
            'username': 'johns1',
            'first_name': 'John',
            'last_name': 'Smith',
            'picture': 'media/picture/default.jpg'
        }

    def test_create_user_check_data(self, test_app):
        user_payload = {'user_payload': {'email': '   EdwaRd-JEFF@test.fr   ',
                                         'password': 'Password123',
                                         'password2': 'Password123',
                                         'first_name': 'edwaRD-jéFF',
                                         'last_name': 'SMITh'
                                         },
                        'profile_payload': {'gender': 'M',
                                            'birthdate': '2000-01-01'}}
        response = test_app.post(self.url, json=user_payload)
        assert response.status_code == 201
        assert response.json() == {
            'username': 'edwardjeffs1',
            'first_name': 'Edward-Jeff',
            'last_name': 'Smith',
            'picture': 'media/picture/default.jpg'
        }

    def test_email_already_used(self, test_app):
        response = test_app.post(self.url, json=self.user_payload)

        assert response.status_code == 422
        assert response.json()[
            'detail'][0]['msg'] == "value is not unique"

    def test_create_username_unique(self, test_app):
        payload = copy.deepcopy(self.user_payload)
        payload['user_payload']['email'] = 'johnsmith1@test.fr'
        response = test_app.post(self.url, json=payload)

        assert response.status_code == 201
        assert response.json() == {
            'username': 'johns2',
            'first_name': 'John',
            'last_name': 'Smith',
            'picture': 'media/picture/default.jpg'
        }

    def test_create_username_unique2(self, test_app):
        user_payload = {'user_payload': {'email': 'edward-jeff1@test.fr',
                                         'password': 'Password123',
                                         'password2': 'Password123',
                                         'first_name': 'EdwardJeff',
                                         'last_name': 'Smith'
                                         },
                        'profile_payload': {'gender': 'M',
                                            'birthdate': '2000-01-01'}}
        response = test_app.post(self.url, json=user_payload)
        assert response.status_code == 201
        assert response.json() == {
            'username': 'edwardjeffs2',
            'first_name': 'Edwardjeff',
            'last_name': 'Smith',
            'picture': 'media/picture/default.jpg'
        }

    def test_connection_nodes(self, test_app):
        user = UserNode.get_node_with_username('johns1')
        gamification = user.gamification

        assert gamification[0].dict()['level'] == 0
        assert gamification[0].dict()['experience'] == 0.0
        with pytest.raises(IndexError):
            gamification[1]

        statistic_profile = user.statistic_profile
        assert statistic_profile[0].dict()['response_time'] is None
        assert statistic_profile[0].dict()['response_rate'] is None
        assert statistic_profile[0].dict()['rating'] is None
        assert statistic_profile[0].dict()['last_connection'] is None
        assert statistic_profile[0].dict()['date_joined'] == datetime.date.today()
        with pytest.raises(IndexError):
            statistic_profile[1]

        profile = user.profile
        assert profile[0].dict()['gender'] == 'GenderEnum.male'
        assert profile[0].dict()['birthdate'] == datetime.date(2000, 1, 1)
        assert profile[0].dict()['job'] is None
        assert profile[0].dict()['biography'] is None
        with pytest.raises(IndexError):
            profile[1]

    def test_email_validation(self, test_app):
        user = UserNode.get_node_with_username('johns1')
        settings = get_settings()
        access_token_expires = datetime.timedelta(minutes=settings.access_token_expire_minutes_mail)
        access_token = create_access_token(data={"uid": user.uid}, expires_delta=access_token_expires)
        url = 'api/users/verify_email'

        response = test_app.get(f'{url}/{access_token}')
        assert response.status_code == 200
        assert response.json() == {'message': 'successfully activated'}

        access_token += '12dre'
        response = test_app.get(f'{url}/{access_token}')
        assert response.status_code == 400
        assert response.json() == {'error': 'invalid token'}

        access_token_expires = datetime.timedelta(milliseconds=1)
        access_token = create_access_token(data={"uid": user.uid}, expires_delta=access_token_expires)
        time.sleep(1)
        response = test_app.get(f'{url}/{access_token}')
        assert response.status_code == 400
        assert response.json() == {'error': 'activation expired'}
