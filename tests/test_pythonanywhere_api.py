import uuid


def test_create_list_delete_console(api):
    create_console = api.create_console()
    assert not create_console.error

    list_consoles = api.list_consoles()
    assert not list_consoles.error
    assert len(list_consoles.data) > 0

    delete_console = api.delete_console(create_console.data['id'])
    assert not delete_console.error


def test_list_consoles(api):
    consoles = api.list_consoles()

    assert not consoles.error
    assert len(consoles.data) > 0


def test_console_input_output(api, constants):
    string = uuid.uuid4().hex

    input_response = api.console_input(constants['PA_CONSOLE_ID'], f'echo {string}\n')
    assert not input_response.error

    output_response = api.console_latest_output(constants['PA_CONSOLE_ID'])
    assert not output_response.error
    assert string in output_response.data['output']


def test_create_get_delete_file(api, constants):
    create_file = api.create_file(constants['FILE_PATH'], bytes(constants['FILE_CONTENT'], 'utf-8'))
    assert not create_file.error

    get_file = api.get_file(constants['FILE_PATH'])
    assert not get_file.error
    assert constants['FILE_CONTENT'] in get_file.data['content']

    delete_file = api.delete_file(constants['FILE_PATH'])
    assert not delete_file.error
