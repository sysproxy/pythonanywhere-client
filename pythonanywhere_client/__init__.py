__version__ = '1.0.0'

import calendar
import datetime
import json
import re
from dataclasses import dataclass
from typing import Union, Optional

import requests
from requests.cookies import cookiejar_from_dict


def add_months(date: datetime.date, months: int) -> datetime.date:
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])

    return datetime.datetime(year, month, day).date()


@dataclass
class Response:
    status_code: Optional[int] = 200
    error: Optional[bool] = False
    data: Optional[Union[dict, list, tuple, None]] = None


class PythonAnywhereClient:
    BASE_URL = 'https://www.pythonanywhere.com'

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = None

    @staticmethod
    def create_url(uri: str) -> str:
        return f'{PythonAnywhereClient.BASE_URL}{uri}'

    def create_session(self, user_agent: str):
        self.session = requests.session()
        self.session.headers = {'User-Agent': user_agent}

    @staticmethod
    def extract_csrf_token(response_text: str) -> str:
        pattern = '<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"(.*)\">'
        result = re.findall(pattern, response_text)

        if result:
            return result[0]

    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()

    def load_cookies(self, cookies: dict):
        self.session.cookies.update(cookiejar_from_dict(cookies))

    def logout(self) -> Response:
        url = self.create_url('/logout/')

        csrf_token = self.get_csrf_token()

        if csrf_token.error:
            return csrf_token

        response = self.session.post(
            url,
            {'csrfmiddlewaretoken': csrf_token.data['csrf_token']},
            headers={'Referer': self.create_url('/')},
            allow_redirects=False
        )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 302
        )

    def login(self) -> Response | bool:
        url = self.create_url('/login/')

        response = self.session.get(url)

        csrf_token = self.extract_csrf_token(response.text)

        if not csrf_token:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'CSRF token extraction failed'}
            )

        data = {
            'csrfmiddlewaretoken': csrf_token,
            'auth-username': self.username,
            'auth-password': self.password,
            'login_view-current_step': 'auth'
        }

        response = self.session.post(
            url,
            data,
            headers={'Referer': url}
        )

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Login failed'}
            )

        pattern = '<p id=\"id_login_error\">The user name or password is incorrect. Please try again.</p>'
        result = re.findall(pattern, response.text)

        if result:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'The user name or password is incorrect'}
            )

        return Response(
            status_code=response.status_code,
            error=False
        )

    def get_app_expiry_date(self, app_name: str) -> Response:
        url = self.create_url(f'/user/{self.username}/webapps/')

        response = self.session.get(url)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Get app page failed'}
            )

        pattern = f'<div class="tab-pane.*\" id=\"id_{app_name}_pythonanywhere_com">' \
                  f'[\\S\\s]*<p class=\"webapp_expiry\">[\\S\\s]*<strong>(.*)</strong>[\\S\\s]*</div>'
        result = re.findall(pattern, response.text)

        if result:
            try:
                return Response(
                    status_code=response.status_code,
                    error=False,
                    data={'expiry_date': datetime.datetime.strptime(result[0], '%A %d %B %Y').date()}
                )
            except ValueError:
                return Response(
                    status_code=response.status_code,
                    error=True,
                    data={'message': 'Extracting failed'}
                )

    def get_csrf_token(self) -> Response:
        app_url = self.create_url(f'/user/{self.username}/webapps/')

        response = self.session.get(app_url)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Get app page failed'}
            )

        csrf_token = self.extract_csrf_token(response.text)

        if not csrf_token:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'CSRF token extraction failed'}
            )

        return Response(
            status_code=response.status_code,
            error=False,
            data={'csrf_token': csrf_token}
        )

    def reload_app(self, app_name: str) -> Response:
        csrf_token = self.get_csrf_token()

        if csrf_token.error:
            return csrf_token

        response = self.session.post(
            self.create_url(f'/user/{self.username}/webapps/{app_name}.pythonanywhere.com/reload'),
            {'csrfmiddlewaretoken': csrf_token.data['csrf_token']},
            headers={'Referer': self.create_url(f'/user/{self.username}/webapps/')}
        )

        if response.status_code != 200 or response.text != 'OK':
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Reload failed'}
            )

        return Response(
            status_code=response.status_code,
            error=False
        )

    def extend_app(self, app_name: str) -> Response:
        csrf_token = self.get_csrf_token()

        if csrf_token.error:
            return csrf_token

        response = self.session.post(
            self.create_url(f'/user/{self.username}/webapps/{app_name}.pythonanywhere.com/extend'),
            {'csrfmiddlewaretoken': csrf_token.data['csrf_token']},
            headers={'Referer': self.create_url(f'/user/{self.username}/webapps/')}
        )

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Extend app failed'}
            )

        return Response(
            status_code=response.status_code,
            error=False
        )

    def extend_task(self, task_id: int) -> Response:
        csrf_token = self.get_csrf_token()

        if csrf_token.error:
            return csrf_token

        response = self.session.post(
            self.create_url(f'/user/{self.username}/schedule/task/{task_id}/extend'),
            {'csrfmiddlewaretoken': csrf_token.data['csrf_token']},
            headers={'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}
        )

        if response.status_code != 200 or response.json()['status'] != 'success':
            return Response(
                status_code=response.status_code,
                error=True,
                data={'message': 'Extend task failed'}
            )
        return Response(
            status_code=response.status_code,
            error=False
        )

    def get_tasks(self) -> Response:
        url = self.create_url(f'/api/v0/user/{self.username}/schedule/')

        response = self.session.get(
            url,
            headers={'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}
        )

        try:
            return Response(
                status_code=response.status_code,
                error=False,
                data=json.loads(response.text)
            )
        except (KeyError, ValueError):
            return Response(
                status_code=response.status_code,
                error=True,
            )

    def create_task(self, command: str, description: str, hour: int, minute: int, enabled: bool = True,
                    interval: str = 'daily') -> Response:
        url = self.create_url(f'/api/v0/user/{self.username}/schedule/')

        data = {
            'command': command,
            'description': description,
            'hour': hour,
            'minute': minute,
            'enabled': enabled,
            'interval': interval
        }

        headers = {
            'Referer': self.create_url(f'/user/{self.username}/tasks_tab/'),
            'X-CSRFToken': self.get_csrf_token().data['csrf_token']
        }

        response = self.session.post(
            url,
            data=data,
            headers=headers
        )

        if response.status_code != 201:
            return Response(
                status_code=response.status_code,
                error=True
            )

        return Response(
            status_code=response.status_code,
            error=False,
            data=json.loads(response.text)
        )

    def update_task(self, task_id: int):
        pass

    def delete_task(self, task_id: int) -> Response:
        url = self.create_url(f'/api/v0/user/{self.username}/schedule/{task_id}/')

        headers = {
            'Referer': self.create_url(f'/user/{self.username}/tasks_tab/'),
            'X-CSRFToken': self.get_csrf_token().data['csrf_token']
        }

        response = self.session.delete(
            url,
            headers=headers
        )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 204,
        )

    def can_create_tasks(self) -> Response:
        url = self.create_url(f'/api/v0/user/{self.username}/user_perms/schedule/')

        response = self.session.get(
            url,
            headers={'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}
        )

        print(response.status_code)
        print(response.text)

        if response.status_code != 200:
            return Response(
                status_code=response.status_code,
                error=True
            )

        return Response(
            status_code=response.status_code,
            error=False,
            data=json.loads(response.text)
        )
