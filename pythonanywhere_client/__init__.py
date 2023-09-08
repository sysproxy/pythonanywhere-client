__version__ = '1.1.0'

import calendar
import datetime
import json
import re
import traceback
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

    def to_dict(self):
        return {
            'status_code': self.status_code,
            'error': self.error,
            'data': self.data
        }


class PythonAnywhereApi:
    def __init__(self, username, token, region='us'):
        self.username = username
        self.token = token
        self.region = region

        if self.region == 'us':
            self.base_url = f'https://www.pythonanywhere.com/api/v0/user/{self.username}'
        elif self.region == 'eu':
            self.base_url = f'https://eu.pythonanywhere.com/api/v0/user/{self.username}'
        else:
            raise Exception('Invalid region provided')

    def create_url(self, uri: str) -> str:
        return f'{self.base_url}{uri}'

    def create_session(self, user_agent: str, timeout: int = 10):
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': user_agent,
            'Authorization': f'Token {self.token}'
        }
        self.session.timeout = timeout

    def list_consoles(self) -> Response:
        url = self.create_url('/consoles/')

        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 200,
            data=json.loads(response.text)
        )

    def console_latest_output(self, console_id: int) -> Response:
        url = self.create_url(f'/consoles/{console_id}/get_latest_output')

        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 200,
            data=json.loads(response.text)
        )

    def console_input(self, console_id: int, input_string: str) -> Response:
        url = self.create_url(f'/consoles/{console_id}/send_input/')

        data = {'input': input_string}

        try:
            response = self.session.post(url, data=data)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 200,
            data=json.loads(response.text)
        )

    def get_file(self, path: str) -> Response:
        url = self.create_url(f'/files/path{path}')

        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 200,
            data={'content': response.text}
        )


class PythonAnywhereWeb:
    BASE_URL = 'https://www.pythonanywhere.com'

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = None

    @staticmethod
    def create_url(uri: str) -> str:
        return f'{PythonAnywhereWeb.BASE_URL}{uri}'

    def create_session(self, user_agent: str, timeout: int = 10):
        self.session = requests.session()
        self.session.headers = {'User-Agent': user_agent}
        self.session.timeout = timeout

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

        try:
            data = {'csrfmiddlewaretoken': csrf_token.data['csrf_token']}
            headers = {'Referer': self.create_url('/')}
            response = self.session.post(url, data=data, headers=headers, allow_redirects=False)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 302
        )

    def login(self) -> Response | bool:
        url = self.create_url('/login/')

        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

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

        headers = {'Referer': url}

        try:
            response = self.session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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

        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

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

        return Response(
            status_code=response.status_code,
            error=True,
        )

    def get_csrf_token(self) -> Response:
        app_url = self.create_url(f'/user/{self.username}/webapps/')

        try:
            response = self.session.get(app_url)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

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

        url = self.create_url(f'/user/{self.username}/webapps/{app_name}.pythonanywhere.com/reload')
        data = {'csrfmiddlewaretoken': csrf_token.data['csrf_token']}
        headers = {'Referer': self.create_url(f'/user/{self.username}/webapps/')}

        try:
            response = self.session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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

        url = self.create_url(f'/user/{self.username}/webapps/{app_name}.pythonanywhere.com/extend')
        data = {'csrfmiddlewaretoken': csrf_token.data['csrf_token']}
        headers = {'Referer': self.create_url(f'/user/{self.username}/webapps/')}

        try:
            response = self.session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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

        url = self.create_url(f'/user/{self.username}/schedule/task/{task_id}/extend')
        data = {'csrfmiddlewaretoken': csrf_token.data['csrf_token']}
        headers = {'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}

        try:
            response = self.session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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
        headers = {'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}

        try:
            response = self.session.get(url, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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

        try:
            response = self.session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
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

        try:
            response = self.session.delete(url, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

        return Response(
            status_code=response.status_code,
            error=response.status_code != 204,
        )

    def can_create_tasks(self) -> Response:
        url = self.create_url(f'/api/v0/user/{self.username}/user_perms/schedule/')
        headers = {'Referer': self.create_url(f'/user/{self.username}/tasks_tab/')}
        try:
            response = self.session.get(url, headers=headers)
        except requests.exceptions.RequestException:
            return Response(
                status_code=None,
                error=True,
                data={'message': traceback.format_exc()}
            )

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
