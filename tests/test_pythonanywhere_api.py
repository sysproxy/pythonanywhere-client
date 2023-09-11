import uuid


def test_create_list_delete_console(api):
    create_console = api.create_console()
    assert not create_console.error

    list_consoles = api.list_consoles()
    assert not list_consoles.error
    assert len(list_consoles.data) > 0

    delete_console = api.delete_console(create_console.data['id'])
    assert not delete_console.error


def test_console_input_output(api, web):
    string = uuid.uuid4().hex

    create_console = api.create_console()
    assert not create_console.error

    start_console = web.start_console(create_console.data['id'])
    assert not start_console.error

    input_response = api.console_input(create_console.data['id'], f'echo {string}\n')
    assert not input_response.error

    output_response = api.console_latest_output(create_console.data['id'])
    assert not output_response.error
    assert string in output_response.data['output']

    delete_console = api.delete_console(create_console.data['id'])
    assert not delete_console.error


def test_create_get_delete_file(api, constants):
    create_file = api.create_file(constants['FILE_PATH'], bytes(constants['FILE_CONTENT'], 'utf-8'))
    assert not create_file.error

    get_file = api.get_file(constants['FILE_PATH'])
    assert not get_file.error
    assert constants['FILE_CONTENT'] in get_file.data['content']

    delete_file = api.delete_file(constants['FILE_PATH'])
    assert not delete_file.error


def test_can_create_tasks(api):
    can_create_tasks = api.can_create_tasks()

    assert not can_create_tasks.error
    assert 'can_create_tasks' in can_create_tasks.data.keys()
    assert can_create_tasks.data['can_create_tasks'] is True


def test_create_delete_task(api, constants):
    task = api.create_task(*constants['TASK'])
    assert not task.error

    delete = api.delete_task(task.data['id'])
    assert not delete.error


def test_get_tasks(api, constants):
    tasks = api.get_tasks()

    assert not tasks.error
    assert len(tasks.data) == 0

    task = api.create_task(*constants['TASK'])
    tasks = api.get_tasks()
    api.delete_task(task.data['id'])

    assert not tasks.error
    assert len(tasks.data) == 1

    assert tasks.data[0]['description'] == task.data['description']
    assert tasks.data[0]['command'] == task.data['command']
    assert tasks.data[0]['hour'] == task.data['hour']
    assert tasks.data[0]['minute'] == task.data['minute']


def test_reload_app(api, constants):
    reload = api.reload_app(constants['PA_APP_NAME'])

    assert not reload.error
