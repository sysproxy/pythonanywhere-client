import uuid


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


def test_get_file(api, constants):
    file = api.get_file(constants['FILE_PATH'])

    assert not file.error
    assert constants['FILE_CONTENT'] in file.data['content']
