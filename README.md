# Fastapi 2FA Example

A simple example of a FastAPI application implementing user registration with 2 Factor Authentication.

## Getting Started

The application is designed to operate in a micro-services architecture and thus can be shipped as a docker image.
Since the application depends on both a database (Postgres) and a cache (Redis), the easiest way to get started is to use docker-compose.

### Prerequisites

- Docker
- Docker Compose (>= v2.25.0, necessary for the `--watch` flag)
- uv

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dadodimauro/fastapi-2fa-example.git
   ```

2. Navigate to the project directory:

   ```bash
   cd fastapi-2fa-example
   ```

3. Create a `.env` file from the provided template:

   ```bash
   uv run task make_env
   ```

4. Start the application using docker-compose:

   ```bash
   uv run task up
   ```

5. The application will be accessible at `http://localhost:8000`.

6. To stop the application and remove the containers, run:

   ```bash
   uv run task down
   ```

### Testing

To run the tests, use the following command (**make sure the db and redis services are running**, see [Installation](#installation) section):

```bash
uv run task test
```

### Utility Commands

Some utility commands are available via `uv`:

- `uv run task lint`: Run linter (ruff).
- `uv run task mypy`: Run mypy type checks.
- `uv run task make_migration`: Create a new database migration with alembic.
- `uv run task migrate`: Apply database migrations.
- `uv run task make_env`: Create a .env file from the .env.template.
- `uv run task up`: Start the application with docker-compose in watch mode.
- `uv run task down`: Stop the application and remove containers.
- `uv run task test`: Run tests with pytest.

## API Documentation

Once the application is running, you can access the interactive API documentation at `http://localhost:8000/docs`.

### Register a new user

To register a new user, send a POST request to `api/v1/auth/register` with the following JSON body:

```json
{
  "email": "user@example.com",
  "password": "********",
  "name": "string",
  "surname": "string",
  "requires_2fa": false
}
```

### Login

To log in, send a POST request to `api/v1/auth/login` with the following JSON body:

```json
{
  "email": "user@example.com",
  "password": "********"
}
```

If the user has **2FA disabled**, the response will contain an access token used for authenticated requests.
If the user has **2FA enabled**, the response will indicate that a 2FA code is required and provide a temporary token used to authenticate the 2FA verification request. Moreover, **a 2FA code will be sent to the user's email**.

***NOTE: The email sending functionality is by default simulated by logging the 2FA code to the application logs. More details on how to enable real email sending can be found in the [SendGrid Integration](#sendgrid-integration) section.***

### Verify 2FA

To verify the 2FA code, send a POST request to `api/v1/auth/2fa-verify` with the following JSON body:

```json
{
  "tmp_token": "string",
  "otp": "string"
}
```

The response will contain an access token used for authenticated requests.

### User endpoints

In order to test the correct behavior of the authentication system, the following endpoints are available:

- `GET /api/v1/users/me`: Get the current authenticated user's information. Requires a valid access token.
- `GET /api/v1/users`: Get a list of all users. Requires a valid access token.

### Health check

Since the application is designed to run in a micro-services architecture, a health check endpoint is available at `GET /healthz` to verify that the application is running correctly; this endpoint does not require authentication and will check the connection to both the database and the cache.

## SendGrid Integration

The application integrates with SendGrid to send 2FA codes via email. To enable this functionality, you need to set the following environment variables in your `.env` file:

``` env
ENABLE_SENDGRID=true
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=noreply@example.com
```

- `ENABLE_SENDGRID`: Set to `true` to enable SendGrid email sending.
- `SENDGRID_API_KEY`: Your SendGrid API key.
- `EMAIL_FROM`: The email address used as the sender for 2FA emails.
