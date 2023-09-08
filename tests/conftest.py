import os

import pytest

from pythonanywhere_client import PythonAnywhereWeb, PythonAnywhereApi


@pytest.fixture(scope='module')
def constants():
    return {
        'PA_USERNAME': os.environ.get('PA_USERNAME'),
        'PA_PASSWORD': os.environ.get('PA_PASSWORD'),
        'PA_APP_NAME': os.environ.get('PA_APP_NAME'),
        'PA_TOKEN': os.environ.get('PA_TOKEN'),
        'PA_REGION': os.environ.get('PA_REGION'),
        'PA_CONSOLE_ID': os.environ.get('PA_CONSOLE_ID'),
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/108.0.0.0 Safari/537.36',
        'CSRF_TOKEN_LENGTH': 64,
        'TASK': (
            'python3.10 -c "print(1)"',
            'Test command',
            7,
            0,
            True
        ),
        'FILE_PATH': f"/home/{os.environ.get('PA_USERNAME')}/.test.txt",
        'FILE_CONTENT': 'Test content',
    }


@pytest.fixture(scope='module')
def web(constants):
    p = PythonAnywhereWeb(
        os.environ.get('PA_USERNAME'),
        os.environ.get('PA_PASSWORD')
    )

    p.create_session(constants['USER_AGENT'])
    p.login()

    yield p

    p.logout()


@pytest.fixture(scope='module')
def api(constants):
    p = PythonAnywhereApi(
        os.environ.get('PA_USERNAME'),
        os.environ.get('PA_TOKEN'),
        os.environ.get('PA_REGION'),
    )

    p.create_session(constants['USER_AGENT'])

    yield p
