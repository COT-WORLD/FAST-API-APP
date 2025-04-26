# FAST-API-APP

A modern, scalable, and production-ready FastAPI application designed for managing users, posts, and votes. This project demonstrates best practices in API development, testing, and deployment, making it an excellent showcase for recruiters and collaborators.

---

## 🚀 Features

- **User Management**: Create, retrieve, and manage users with secure authentication.
- **Post Management**: Full CRUD operations for posts with ownership validation.
- **Voting System**: Users can upvote or remove votes on posts.
- **Authentication**: Secure user authentication using OAuth2 and JWT tokens.
- **Database Integration**: SQLModel and Alembic for database modeling and migrations.
- **Testing**: Comprehensive unit and integration tests using `pytest`.
- **Containerization**: Docker support for seamless development and production environments.
- **CI/CD**: Automated testing and deployment pipelines using GitHub Actions and Render.
- **API Documentation**: Interactive API documentation with Swagger UI and ReDoc.

---

## 🛠️ Technologies Used

### Backend Framework

- **FastAPI**: High-performance, modern web framework for building APIs with Python 3.12+.

### Database

- **PostgreSQL**: Relational database for storing application data.
- **SQLModel**: Combines SQLAlchemy and Pydantic for database modeling.
- **Alembic**: Database migrations.

### Authentication

- **OAuth2**: Secure authentication with JWT tokens.

### Testing

- **Pytest**: Unit and integration testing framework.
- **HTTPX**: Asynchronous HTTP client for testing API endpoints.

### Containerization

- **Docker**: Containerization for development and production environments.
- **Docker Compose**: Simplified multi-container orchestration.

### CI/CD

- **GitHub Actions**: Automated testing and deployment pipelines.
- **Render**: Cloud platform for deploying the application.

### API Documentation

- **Swagger UI**: Interactive API documentation [[Swagger UI](https://fast-api-app-f69e.onrender.com/docs)].
- **ReDoc**: Alternative API documentation interface [[ReDoc](https://fast-api-app-f69e.onrender.com/redoc)].

---

## 🧪 Testing

## This project includes a robust test suite to ensure the reliability of the application. Both **unit tests** and **integration tests** are implemented to validate individual components and their interactions.

### Running Tests

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the test suite:
   ```bash
   pytest -v -s
   ```

### Test Coverage

#### Unit Tests

- **Users**:
  - User creation and validation.
  - Token generation and authentication.
- **Posts**:
  - CRUD operations for posts.
  - Ownership validation.
- **Votes**:
  - Adding and removing votes.
  - Duplicate vote handling.

#### Integration Tests

Integration tests validate the interaction between multiple components, such as database operations, authentication, and API endpoints.

Example: Integration test for creating a post and voting on it:

```python
# filepath: tests/test_integration.py
import pytest

def test_create_post_and_vote(client, test_user, token_headers):
    # Create a post
    response = client.post(
        "/posts/",
        json={"title": "Integration Test Post", "content": "This is a test."},
        headers=token_headers,
    )
    assert response.status_code == 201
    post_id = response.json()["id"]

    # Vote on the post
    vote_response = client.post(
        "/vote/",
        json={"post_id": post_id, "dir": 1},
        headers=token_headers,
    )
    assert vote_response.status_code == 201
    assert vote_response.json()["message"] == "Vote added successfully"
```

---

## 🌐 API Endpoints

### Authentication

- `POST /login`: User login and token generation.

### Users

- `GET /users/`: Retrieve all users.
- `POST /users/`: Create a new user.
- `GET /users/{id}`: Retrieve a user by ID.

### Posts

- `GET /posts/`: Retrieve all posts.
- `POST /posts/`: Create a new post.
- `GET /posts/{id}`: Retrieve a post by ID.
- `PUT /posts/{id}`: Update a post.
- `DELETE /posts/{id}`: Delete a post.

### Votes

- `POST /vote/`: Add or remove a vote on a post.

---

## 🚀 Deployment

### Local Deployment

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/fast-api-app.git
   cd fast-api-app
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:

   ```bash
   alembic upgrade head
   ```

4. Start the application:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. Access the API at [http://localhost:8000/docs](http://localhost:8000/docs).

### Docker Deployment

1. Build and run the Docker container:

   ```bash
   docker-compose -f docker-compose-prod.yml up --build
   ```

2. Access the API at [http://localhost](http://localhost).

---

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for automated testing and deployment:

1. **Continuous Integration (CI)**:

   - Runs tests on every push or pull request.
   - Ensures code quality and reliability.

2. **Continuous Deployment (CD)**:
   - Deploys the application to Render after successful tests.

---

## 📜 Environment Variables

| Variable                      | Description                      |
| ----------------------------- | -------------------------------- |
| `DATABASE_URL`                | Database connection URL          |
| `SECRET_KEY`                  | Secret key for JWT               |
| `ALGORITHM`                   | Algorithm for JWT                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes |

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```

```
