import datetime

from pythonanywhere_client import PythonAnywhereWeb, add_months


def test_create_url(web):
    assert web.create_url('') == PythonAnywhereWeb.BASE_URL
    assert web.create_url('/login/') == f'{PythonAnywhereWeb.BASE_URL}/login/'


def test_create_session(web, constants):
    assert web.session.headers.get('User-Agent') == constants['USER_AGENT']


def test_extract_csrf_token(web, constants):
    url = web.create_url('/login/')
    response = web.session.get(url)

    csrf_token = web.extract_csrf_token(response.text)

    assert csrf_token is not None
    assert len(csrf_token) == constants['CSRF_TOKEN_LENGTH']


def test_get_cookies(web):
    cookies = web.get_cookies()

    assert type(cookies) is dict
    assert 'csrftoken' in cookies


def test_load_cookies(web, constants):
    cookies = web.get_cookies()

    web_new = PythonAnywhereWeb(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    web_new.create_session(constants['USER_AGENT'])
    web_new.load_cookies(cookies)

    new_cookies = web_new.get_cookies()
    assert type(new_cookies) is dict
    assert 'csrftoken' in new_cookies


def test_logout(constants):
    web = PythonAnywhereWeb(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    web.create_session(constants['USER_AGENT'])
    web.login()

    logout = web.logout()

    assert not logout.error


def test_login(constants):
    web = PythonAnywhereWeb(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    web.create_session(constants['USER_AGENT'])
    login = web.login()

    assert not login.error


def test_get_app_expiry_date(web, constants):
    expiry_date = web.get_app_expiry_date(constants['PA_APP_NAME'])

    assert not expiry_date.error
    assert expiry_date.data['expiry_date'] > datetime.datetime.now().date()


def test_get_csrf_token(web, constants):
    csrf_token = web.get_csrf_token()

    assert not csrf_token.error
    assert len(csrf_token.data['csrf_token']) == constants['CSRF_TOKEN_LENGTH']


def test_reload_app(web, constants):
    reload = web.reload_app(constants['PA_APP_NAME'])

    assert not reload.error


def test_extend_app(web, constants):
    extend = web.extend_app(constants['PA_APP_NAME'])
    date = add_months(datetime.datetime.now(), 3)

    assert not extend.error
    assert web.get_app_expiry_date(constants['PA_APP_NAME']).data['expiry_date'] >= date


def test_extend_task(api, web, constants):
    task = api.create_task(*constants['TASK'])

    extend_task = web.extend_task(task.data['id'])
    api.delete_task(task.data['id'])

    assert not extend_task.error


def test_start_console(api, web):
    create_console = api.create_console()
    assert not create_console.error

    start_console = web.start_console(create_console.data['id'])
    assert not start_console.error

    delete_console = api.delete_console(create_console.data['id'])
    assert not delete_console.error
