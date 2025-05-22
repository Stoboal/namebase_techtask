# Name Origin API

## Description

This project is an API service that predicts the probable country of origin for a given name. The service utilizes external APIs (Nationalize.io for name-based predictions and REST Countries for detailed country information) to gather and aggregate data. Results are cached in a local database to improve performance and reduce the load on external services.

The API also provides an endpoint to retrieve a list of the most frequently requested names for a specified country, based on accumulated statistics.

## Tech Stack

* **Language:** Python 3.12
* **Framework:** Django 5.2.1, Django REST Framework 3.16
* **Database:** PostgreSQL 15
* **Containerization:** Docker 26.1, Docker Compose 2.27
* **Linting/Formatting:** Ruff 0.11
* **API Documentation:** drf-spectacular (Swagger UI & ReDoc)
* **Authentication:** Token Authentication (DRF)

## Setup and Running

### Prerequisites

* Docker (version 26.1)
* Docker Compose (version 2.27)

### Steps to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Stoboal/namebase_techtask.git
    cd <your_project_folder_name>
    ```

2.  **Create and configure the `.env` file:**
    In the project's root directory, create a file named `.env`. You can copy variables from below:
    ```env
    # Django settings
    DJANGO_SECRET_KEY=secret_key
    DEBUG=True

    # PostgreSQL settings
    DB_NAME=name_origin_db
    DB_USER=db_user
    DB_PASS=complexpassword
    
    # Database connection for Django (inside Docker)
    DB_HOST=db
    DB_PORT=5432
    ```

3.  **Build and run Docker containers:**
    ```bash
    docker-compose up --build
    ```
    This command will build the image for the Django application (if it's not already built or if the `Dockerfile` has changed) and start the `web` (your application) and `db` (PostgreSQL) services.

4.  **Apply database migrations:**
    In a **new terminal window/tab**, while in the project's root folder, run:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Create a superuser (for Django Admin access and token generation):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create a user.

### Accessing the Application

* **API Documentation (Swagger UI):** `http://localhost:8000/api/schema/swagger-ui/`
* **API Documentation (ReDoc):** `http://localhost:8000/api/schema/redoc/`
* **Django Admin:** `http://localhost:8000/admin/` (use your superuser credentials)

## Environment Variables (`.env`)

Below is a list of environment variables required for the application to run. They should be defined in an `.env` file in the project root.

* `DJANGO_SECRET_KEY`: **Required.** Django secret key. Used for cryptographic signing of sessions and other data. Must be unique and complex.
    * _Example:_ `django-insecure-your-very-secret-and-long-key-here`
* `DEBUG`: **Required.** Django debug mode. Set to `True` for development (shows detailed errors) and `False` for production.
    * _Example:_ `True`
* `DB_NAME`: **Required.** Name for the PostgreSQL database to be created and used.
    * _Example:_ `name_api_db`
* `DB_USER`: **Required.** Username for connecting to PostgreSQL.
    * _Example:_ `api_user`
* `DB_PASS`: **Required.** Password for the PostgreSQL user.
    * _Example:_ `complex_password_123`
* `DB_HOST`: **Required.** Hostname of the PostgreSQL database as defined in `docker-compose.yml`. For inter-container communication, this is the service name `db`.
    * _Example:_ `db`
* `DB_PORT`: **Required.** Port on which PostgreSQL listens inside the Docker network.
    * _Example:_ `5432`

## API Endpoint Descriptions

The API provides the following main endpoints:

* **`GET /api/names/?name=<name>`**:
    * Predicts the probable nationality (list of countries with probabilities) for the given name.
    * Requires Token Authentication.
    * Query parameter: `name` (string, required) – The name to analyze.
* **`GET /api/popular-names/?country=<country_code>`**:
    * Returns the top 5 most frequently requested names associated with the specified country code (ISO 3166-1 alpha-2).
    * Requires Token Authentication.
    * Query parameter: `country` (string, required) – The two-letter country code.

Full interactive API documentation is available via Swagger UI and ReDoc (see "Accessing the Application" for links).

## Authentication

The API uses Token Authentication (`TokenAuthentication` from Django REST Framework).

To access protected endpoints, the token must be included in the `Authorization` header:
* **`Authorization: Token <YOUR_API_TOKEN>`**

To obtain a token follow the next steps:
1.  Enter the Django shell: `docker-compose exec web python manage.py shell`
2.  Execute the following commands:
    ```python
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token
    user = User.objects.get(username='your_username')
    token, created = Token.objects.get_or_create(user=user)
    print(token.key)
    ```

## Running Tests

To run the unit tests, execute the following command:
```bash
docker-compose exec web python manage.py test