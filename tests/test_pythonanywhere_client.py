import datetime

from pythonanywhere_client import PythonAnywhereClient, add_months


def test_create_url(pa):
    assert pa.create_url('') == PythonAnywhereClient.BASE_URL
    assert pa.create_url('/login/') == f'{PythonAnywhereClient.BASE_URL}/login/'


def test_create_session(pa, constants):
    assert pa.session.headers.get('User-Agent') == constants['USER_AGENT']


def test_extract_csrf_token(pa, constants):
    url = pa.create_url('/login/')
    response = pa.session.get(url)

    csrf_token = pa.extract_csrf_token(response.text)

    assert csrf_token is not None
    assert len(csrf_token) == constants['CSRF_TOKEN_LENGTH']


def test_get_cookies(pa):
    cookies = pa.get_cookies()

    assert type(cookies) is dict
    assert 'csrftoken' in cookies


def test_load_cookies(pa, constants):
    cookies = pa.get_cookies()

    pa_new = PythonAnywhereClient(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    pa_new.create_session(constants['USER_AGENT'])
    pa_new.load_cookies(cookies)

    new_cookies = pa_new.get_cookies()
    assert type(new_cookies) is dict
    assert 'csrftoken' in new_cookies


def test_logout(constants):
    pa = PythonAnywhereClient(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    pa.create_session(constants['USER_AGENT'])
    pa.login()

    logout = pa.logout()

    assert not logout.error


def test_login(constants):
    pa = PythonAnywhereClient(constants['PA_USERNAME'], constants['PA_PASSWORD'])
    pa.create_session(constants['USER_AGENT'])
    login = pa.login()

    assert not login.error


def test_get_app_expiry_date(pa, constants):
    expiry_date = pa.get_app_expiry_date(constants['PA_APP_NAME'])

    assert not expiry_date.error
    assert expiry_date.data['expiry_date'] > datetime.datetime.now().date()


def test_get_csrf_token(pa, constants):
    csrf_token = pa.get_csrf_token()

    assert not csrf_token.error
    assert len(csrf_token.data['csrf_token']) == constants['CSRF_TOKEN_LENGTH']


def test_reload_app(pa, constants):
    reload = pa.reload_app(constants['PA_APP_NAME'])

    assert not reload.error


def test_extend_app(pa, constants):
    extend = pa.extend_app(constants['PA_APP_NAME'])
    date = add_months(datetime.datetime.now(), 3)

    assert not extend.error
    assert pa.get_app_expiry_date(constants['PA_APP_NAME']).data['expiry_date'] >= date


def test_create_task(pa, constants):
    task = pa.create_task(*constants['TASK'])

    pa.delete_task(task.data['id'])

    assert not task.error


def test_delete_task(pa, constants):
    task = pa.create_task(*constants['TASK'])

    delete = pa.delete_task(task.data['id'])

    assert not delete.error
    assert len(pa.get_tasks().data) == 0


def test_update_task():
    pass


def test_extend_task(pa, constants):
    task = pa.create_task(*constants['TASK'])

    extend_task = pa.extend_task(task.data['id'])
    pa.delete_task(task.data['id'])

    assert not extend_task.error


def test_can_create_tasks(pa):
    can_create_tasks = pa.can_create_tasks()

    assert not can_create_tasks.error
    assert 'can_create_tasks' in can_create_tasks.data.keys()


def test_get_tasks(pa, constants):
    tasks = pa.get_tasks()

    assert not tasks.error
    assert len(tasks.data) == 0

    task = pa.create_task(*constants['TASK'])
    tasks = pa.get_tasks()
    pa.delete_task(task.data['id'])

    assert not tasks.error
    assert len(tasks.data) == 1

    assert tasks.data[0]['description'] == task.data['description']
    assert tasks.data[0]['command'] == task.data['command']
    assert tasks.data[0]['hour'] == task.data['hour']
    assert tasks.data[0]['minute'] == task.data['minute']
