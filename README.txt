IT Asset Manager Application - Localhost Setup Instructions
===========================================================

IMPORTANT TO NOTE THIS WEB APP CAN BE ACCESSED THROUGH THE ALREADY DEPLOYED WEBSERVICE AT:

https://itassetmanager.onrender.com/

For admin access use the following login credetials:

username: admin
password: admin

To access without admin privelages please register an account.

THE FOLLOWING IS INSTRUCTIONS TO RUN IT LOCALLY

Prerequisites
-------------
Before starting, ensure you have the following installed and set up on your local machine:

1. **Python 3.8+**  
   - Download and install Python from the official Python website: https://www.python.org/downloads/.
   - Ensure `pip` (Python package manager) is installed along with Python.
   - Verify both Python and pip installations using the following commands:
     ```
     python --version
     pip --version
     ```

2. **PostgreSQL**  
   - PostgreSQL is running on a remote web service and accessible.
   - On top of that, the DATABASE_URL is already set up in the settings.py file of the django app


3. **Virtual Environment Tool (venv)**  
   - This tool comes bundled with Python 3. Verify it's accessible by running:
     ```
     python -m venv --help
     ```

Step 1: Extract the Zip File
----------------------------
Unzip the project folder to your desired location on your local machine.

Step 2: Create and Activate a Virtual Environment
-------------------------------------------------
Navigate to the unzipped project folder and create a virtual environment using the `venv` tool.
Open PowerShell and cd into the yourlocalpath/ITAssetManager/ITAssetManager and create virtual enviroment
using the following command:

python -m venv venv

Activate the virtual environment:

- For **Windows**:

venv\Scripts\activate

- For **macOS/Linux**:
source venv/bin/activate


Step 3: Install Dependencies
----------------------------
With the virtual environment activated, install the required dependencies by running the following 
command:

pip install -r requirements.txt


This will install all necessary packages, including Django, PostgreSQL support, and others as specified in `requirements.txt`.

Step 4: Modify Django Settings
------------------------------
Open the `settings.py` file located in the Django project directory. Ensure the `ALLOWED_HOSTS` is configured to allow local access by updating it as follows:

```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

Also if running locally ensure DEBUG = True

Step 5: Apply Database Migrations
---------------------------------
To apply the database migrations and sync the database with the application models, run the following command:

python manage.py migrate

Step 6: Run the Development Server
----------------------------------
Start the Django development server by running:

You can now access the application in your web browser by visiting:

http://127.0.0.1:8000


ADMIN CREDENTIALS:

username: admin
password: admin

REGULAR USER CREDENTIALS:

Register an account


Run Tests Using Django's Test Runner
------------------------------------

Run the Django unit tests using the following command:

python manage.py test

This command will automatically discover and run all the test cases within your project.

Check Test Results
Once the tests complete, the result will display in your terminal or command prompt, showing how many tests passed or failed, along with any detailed errors.