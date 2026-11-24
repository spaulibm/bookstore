# Bookstore Backend

FastAPI + async SQLAlchemy (SQLite) backend for an eCommerce bookstore. See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the design.

## Prerequisites

- Python 3.10–3.13 (3.12 recommended). Python 3.15 preview builds are not supported: some dependencies (e.g. `pyyaml`) have no wheels and need a C++ compiler.
- pip

## Quick start

The run scripts create a virtual environment (`.venv`), install dependencies, create `.env` from `.env.example` if missing, and start the server with auto-reload.

**Windows (PowerShell):**

```powershell
.\run.ps1              # runs on port 8000
.\run.ps1 -Port 9000   # custom port
```

If script execution is blocked, run once: `Set-ExecutionPolicy -Scope Process Bypass`.

**macOS / Linux / Git Bash:**

```bash
chmod +x run.sh
./run.sh               # runs on port 8000
PORT=9000 ./run.sh     # custom port
```

The API is then available at:

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs

## Manual setup

```powershell
# create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate         # macOS / Linux

# install dependencies
pip install -r requirements.txt

# create your env file
Copy-Item .env.example .env         # Windows
# cp .env.example .env              # macOS / Linux

# start the server
uvicorn app.main:app --reload --port 8000
```

## Configuration

Settings are read from `.env` (copy of [`.env.example`](.env.example)):

| Variable                      | Description                                  | Default                                 |
| ----------------------------- | -------------------------------------------- | --------------------------------------- |
| `DATABASE_URL`                | SQLAlchemy async database URL                | `sqlite+aiosqlite:///./bookstore.db`    |
| `SECRET_KEY`                  | JWT signing secret — **change before deploy**| `change-me-to-a-random-256-bit-secret`  |
| `ALGORITHM`                   | JWT algorithm                                | `HS256`                                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime in minutes                      | `60`                                    |
| `MCP_API_KEY`                 | API key for the MCP server (planned)         | `change-me-mcp-secret`                  |
| `MCP_PORT`                    | MCP server port (planned)                    | `3100`                                  |

## Available endpoints

| Method | Path              | Description                  | Auth        |
| ------ | ----------------- | ---------------------------- | ----------- |
| POST   | `/auth/register`  | Register a user              | —           |
| POST   | `/auth/login`     | Log in, returns a JWT        | —           |
| GET    | `/books`          | List books                   | —           |
| GET    | `/books/{id}`     | Get a book                   | —           |
| POST   | `/books`          | Create a book                | Admin       |
| PUT    | `/books/{id}`     | Update a book                | Admin       |
| DELETE | `/books/{id}`     | Delete a book                | Admin       |

Use the **Authorize** button in `/docs` after logging in to call admin endpoints.

## Tests

Test dependencies (`pytest`, `pytest-asyncio`, `anyio`) are included in `requirements.txt`, but no `tests/` directory exists yet. Once tests are added, run:

```bash
pytest
```

## Troubleshooting

- **Port already in use:** pass a different port (`-Port` / `PORT`).
- **Reset the database:** stop the server and delete `bookstore.db`.
- **`ResolutionImpossible` / build errors on install:** make sure the `.venv` was created with a supported Python (see Prerequisites). Delete `.venv` and recreate it, e.g. `py -3.12 -m venv .venv`.
