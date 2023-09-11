# PythonAnywhere Client

This is a Python client library for interacting with the PythonAnywhere platform. The library provides functions to 
manage web applications, tasks, and other features offered by PythonAnywhere. It uses the requests library for making 
HTTP requests and provides a simple interface to perform various tasks.

## Installation
You can install it using pip
```shell
pip install pythonanywhere-client
```

## Usage

### PythonAnywhereWeb
```python
from pythonanywhere_client import PythonAnywhereWeb

# Replace with your PythonAnywhere username and password
username = 'your_username'
password = 'your_password'

# Replace with your User-Agent
user_agent_string = 'my_user_agent_string'

# Create client and request session
client = PythonAnywhereWeb(username, password)
client.create_session(user_agent_string)

# Logging in
login_response = client.login()

if login_response.error:
    print('Login failed:', login_response.data['message'])
else:
    print('Login successful!')

# Get web application expiry date
app_name = 'your_app_name'

expiry_response = client.get_app_expiry_date(app_name)

if expiry_response.error:
    print('Error:', expiry_response.data['message'])
else:
    print('Expiry Date:', expiry_response.data['expiry_date'])

# ... (other methods)
```

### PythonAnywhereApi
```python
from pythonanywhere_client import PythonAnywhereApi

# Replace with your API token
token = 'my_api_token'

# Replace with your User-Agent
user_agent_string = 'my_user_agent_string'

client = PythonAnywhereApi(token)
client.create_session(user_agent_string)

file_response = client.get_file('/home/myusername/test.txt')

if file_response.error:
    print('Error: ', file_response.data['message'])
else:
    print('File content: ', file_response.data['content'])
    
# ... (other methods)
```

## Methods
### PythonAnywhereWeb
* `login()` - Log in to the PythonAnywhere platform
* `logout()`- Log out from the PythonAnywhere platform
* `get_app_expiry_date(app_name)` - Get the expiry date of a web application
* `reload_app(app_name)` - Reload a web application
* `extend_task(task_id)`- Extend the schedule of a task
* `extend_app(app_name)`- Extend the schedule of a web application


### PythonAnywhereApi
* `create_console()` - Create a console
* `start_console(console_id)` - Start a console
* `delete_console(console_id)` - Delete a console
* `list_consoles()` - List active consoles
* `console_latest_output(console_id)` - Get the latest output from the console
* `console_input(console_id, input_string)` - Send the input to the console
* `get_file(path)` - Get the contents of the file
* `create_file(path, content)` - Create a file
* `delete_file(path)` - Delete a file
* `can_create_tasks()`- Check if the user is allowed to create tasks
* `create_task(command, description, hour, minute, enabled=True, interval='daily')` - Create a new task
* `delete_task(task_id)`- Delete a task
* `get_tasks()`: Get a list of user's tasks.


## Contributing
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, 
feel free to open an issue or submit a pull request.