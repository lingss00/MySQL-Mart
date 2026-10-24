# MySQL Mart — Class 12 Computer Science Project

A local online-shopping demo website using HTML/CSS, Python Flask, and a real MySQL database.

## Features
- Dashboard with product/customer/order/sales counts
- Product list, search, add, update, and delete
- Place an order and automatically reduce product stock
- SQL learning notes and a short MCQ quiz
- Parameterized SQL queries to reduce SQL injection risk

## Requirements
- Python 3.10 or newer
- MySQL Server 8.0+ and MySQL Workbench
- Google Chrome or another modern browser

## Setup
1. Install MySQL Server and MySQL Workbench.
2. Open Workbench and connect to your local server.
3. Open `schema.sql` in Workbench and execute the script. It creates the `mysql_mart` database and tables, then inserts sample products.
4. Open a terminal in this project folder.
5. Create and activate a virtual environment (recommended):
   - Windows: `py -m venv .venv`
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Windows Command Prompt: `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
6. Install packages: `python -m pip install -r requirements.txt`
7. Set your MySQL password in the environment:
   - Windows PowerShell: `$env:MYSQL_PASSWORD="your_actual_mysql_password"`
   - Windows Command Prompt: `set MYSQL_PASSWORD=your_actual_mysql_password`
   - macOS/Linux: `export MYSQL_PASSWORD='your_actual_mysql_password'`
   If your MySQL username is not `root`, set `MYSQL_USER` too. The app defaults to `root`, an empty password, and database `mysql_mart`.
8. Start the website: `python app.py`
9. In Chrome, open `http://127.0.0.1:5000`

## Important
- Keep the terminal running while you use the website.
- This runs locally on your computer; it is not published to the public internet.
- Never publish your MySQL password or use a database administrator account for a public production website.
- The Flask debug server is for local school-project development, not public production hosting.
- If MySQL is running on another port, set `MYSQL_PORT`.
- If you get a connection error, check that the MySQL server is running and the credentials match your local setup.

## Suggested project report
**Aim:** To develop a web-based online shopping management system connected to a MySQL database.

**Objectives:** Store product information, search products, update stock and prices, place orders, and demonstrate SQL database operations through a browser interface.

**Tools:** Python, Flask, MySQL, HTML, CSS, Google Chrome.

**Conclusion:** The website demonstrates how a Python backend communicates with MySQL to store, retrieve, and update real records.


## Publish online (Railway + MySQL)

The app supports Railway's standard MySQL variables (`MYSQLHOST`, `MYSQLPORT`,
`MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`) and uses Gunicorn for hosting.

1. Create a GitHub repository and upload the contents of this project folder.
   Do not upload passwords or any `.env` file containing secrets.
2. Sign in to Railway and create a new project.
3. Add a MySQL database service to the project. Railway documents this under
   its MySQL database guide: https://docs.railway.com/databases/mysql
4. Deploy the GitHub repository as an application service in the same Railway project.
   Railway's Flask deployment guide: https://docs.railway.com/guides/flask
5. In the app service, make sure the MySQL connection variables are available from
   the MySQL service. Railway's service reference/variable UI can be used to link
   the database variables. The app understands both MYSQLHOST-style and MYSQL_HOST-style names.
6. Open the hosted MySQL database using the connection details supplied by Railway,
   select the database named by MYSQLDATABASE, and execute `schema_hosted.sql`.
   Do not run the local `schema.sql` blindly against a hosted database if its database
   name differs; `schema_hosted.sql` creates the tables in the selected database.
7. Set the app service start command to `gunicorn app:app` if Railway does not detect
   the included `Procfile` automatically.
8. In Railway, open the app service's Settings/Networking section and generate a public domain.
   Open that HTTPS URL to test the website.

Costs and free credits/limits can change; check the current plan before deploying.
Do not expose the database publicly just to connect the app: keep it private within
the same project and use the host-provided internal connection variables.
