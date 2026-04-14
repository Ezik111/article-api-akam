# Article Management API

Secure HTTP API server for managing articles and users, built with **FastAPI**

## Technical Stack

* **Framework**: FastAPI (Python 3.11)
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Authentication**: OAuth2 with JWT (JSON Web Tokens)
* **Security**: Password hashing with Bcrypt & Security Headers (HSTS, XSS)
* **Validation**: Pydantic V2
* **Containerization**: Docker & Docker Compose
* **Testing**: Pytest

## Core Features

* **User System**: Secure registration and authentication with JWT-based access control.
* **Article Management**: Full CRUD operations with author-based access control (users can only modify/delete their own content).
* **Bulk Import**: Dedicated endpoint for mass importing articles from external JSON sources.
* **Notification System**: Integrated mechanism to notify subscribers about new content via system logs.
* **Security Middleware**: Custom implementation of security headers to ensure a secure communication channel.

## Security Highlights

* **Data Integrity**: Strict input validation using Pydantic V2 schemas.
* **Resource Protection**: Resource-level authorization to prevent unauthorized data modification.
* **Secure Storage**: Passwords are encrypted using the industry-standard Bcrypt algorithm.
* **Infrastructure Security**: Protection against common web vulnerabilities like Clickjacking and XSS via automated headers.

## Project Structure

The project follows a modular design for high readability and maintainability:

- `app/` - Application source code.
  - `main.py` - API entry point, middleware, and route definitions.
  - `models.py` - SQLAlchemy database entities.
  - `schemas.py` - Pydantic models for data validation.
  - `security.py` - Logic for hashing and JWT token management.
  - `database.py` - Engine configuration and session management.
- `tests/` - Comprehensive test suite covering core flows and edge cases.
- `docker-compose.yml` - Service orchestration (API & Database).

## Prerequisites

Before running the project, ensure you have the following installed:
* Docker Desktop
* Docker Compose

## Getting Started

1.  **Environment Configuration**:
    Create a local `.env` file from the provided example:
    ```bash
    cp .env.example .env
    ```

2.  **Launch Services**:
    ```bash
    docker-compose up --build -d
    ```

3.  **API Documentation**:
    Once the build is complete, access the interactive documentation at:
    * **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
    * **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing

To verify the system integrity, run the automated test suite while the containers are active:

```bash
docker-compose exec web pytest
```

## Author
Name: Bartosz Żurawski
Email: bartoszzurawski.03@gmail.com

## License
This project is licensed under the MIT License.