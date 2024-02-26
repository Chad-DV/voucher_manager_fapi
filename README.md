# Voucher Manager
Voucher generation and redemption interface using Fast-API and Postgresql 

## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Set up a virtual environment.
4. Install dependencies from `requirements.txt`.
5. create psql user with below commands

CREATE USER your_postgres_username WITH PASSWORD 'your_postgres_password'; <br />
ALTER USER your_postgres_username CREATEDB; <br />
CREATE DATABASE your_database_name; <br />
GRANT ALL PRIVILEGES ON DATABASE CREATE DATABASE your_database_name TO your_postgres_username; <br />
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_postgres_username; <br />

6. Change config settings in voucher_manager_fapi-master\voucher_management\databaseconfig.json
7. Run the FastAPI application. (main.py) (set to run on local-host port 8000)
