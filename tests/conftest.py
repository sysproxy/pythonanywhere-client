import os

import pytest

from pythonanywhere_client import PythonAnywhereClient


@pytest.fixture(scope='module')
def constants():
    return {
        'PA_USERNAME': os.environ.get('PA_USERNAME'),
        'PA_PASSWORD': os.environ.get('PA_PASSWORD'),
        'PA_APP_NAME': os.environ.get('PA_APP_NAME'),
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/108.0.0.0 Safari/537.36',
        'CSRF_TOKEN_LENGTH': 64,
        'TASK': (
            'python3.10 -c "print(1)"',
            'Test command',
            7,
            0,
            True
        )
    }


@pytest.fixture(scope='module')
def pa(constants):
    p = PythonAnywhereClient(
        os.environ.get('PA_USERNAME'),
        os.environ.get('PA_PASSWORD')
    )

    p.create_session(constants['USER_AGENT'])
    p.login()

    yield p

    p.logout()
