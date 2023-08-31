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
```python
from pythonanywhere_client import PythonAnywhereClient

# Replace with your PythonAnywhere username and password
username = 'your_username'
password = 'your_password'

client = PythonAnywhereClient(username, password)

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

# ... (other tasks)

```
## Methods
* `login()` - Log in to the PythonAnywhere platform
* `logout()`- Log out from the PythonAnywhere platform
* `get_app_expiry_date(app_name)` - Get the expiry date of a web application
* `reload_app(app_name)` - Reload a web application.
* `get_tasks()`: Get a list of user's tasks.
* `create_task(command, description, hour, minute, enabled=True, interval='daily')` - Create a new task.
* `delete_task(task_id)`- Delete a task.
* `extend_task(task_id)`- Extend the schedule of a task.
* `extend_app(app_name)`- Extend the schedule of a web application.
* `can_create_tasks()`- Check if the user is allowed to create tasks.


## Contributing
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, 
feel free to open an issue or submit a pull request.