# eCommerce Bookstore Backend — Architecture

## Overview

A RESTful **Python / FastAPI** backend for an online bookstore, extended with an
IBM Bob–compatible **MCP (Model Context Protocol) server** so that Bob agents can
query stock, place orders, and retrieve recommendations programmatically.

---

## Technology Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Runtime | Python 3.11+ | Async-first, type hints, rich ecosystem |
| Framework | FastAPI | Async, auto OpenAPI docs, Pydantic validation |
| Database | SQLite (via `aiosqlite` + `SQLAlchemy` async) | Zero-config, file-based, easy to swap to Postgres |
| Auth | JWT (`python-jose`) + bcrypt (`passlib`) | Stateless, portable |
| MCP Server | `mcp` Python SDK (official) | IBM Bob–compatible agentic tool exposure |
| Testing | `pytest` + `httpx` (AsyncClient) | Async-native, clean fixtures |

---

## Domain Model

```
User
 ├── id, email, hashed_password, role (customer|admin), created_at
 └── orders: List[Order]

Book
 ├── id, isbn, title, author, genre, price, stock, cover_url
 └── order_items: List[OrderItem]

Order
 ├── id, user_id, status (pending|paid|shipped|cancelled), total, created_at
 └── items: List[OrderItem]

OrderItem
 └── order_id, book_id, quantity, unit_price
```

---

## API Surface (REST)

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Register new customer |
| POST | /auth/login | Login → JWT access token |

### Books
| Method | Path | Description |
|--------|------|-------------|
| GET | /books | List / search books (query params: q, genre, limit, offset) |
| GET | /books/{id} | Book detail |
| POST | /books | Add book (admin only) |
| PUT | /books/{id} | Update book (admin only) |
| DELETE | /books/{id} | Delete book (admin only) |

### Cart  (JWT-scoped, in-memory per user session)
| Method | Path | Description |
|--------|------|-------------|
| GET | /cart | View cart |
| POST | /cart | Add item |
| DELETE | /cart/{book_id} | Remove item |

### Orders
| Method | Path | Description |
|--------|------|-------------|
| POST | /orders | Checkout cart → Order |
| GET | /orders | My orders |
| GET | /orders/{id} | Order detail |
| PATCH | /orders/{id}/status | Update status (admin only) |

---

## MCP Agentic Layer (IBM Bob Integration)

The MCP server runs on a separate HTTP port (default **3100**) using the
`mcp` Python SDK with **Streamable HTTP transport**.  IBM Bob connects to it
and gains access to the following tools:

| Tool Name | Description |
|-----------|-------------|
| `search_books` | Full-text search across title / author / genre |
| `get_book` | Fetch single book by id |
| `check_stock` | Return available stock for a book |
| `create_order` | Checkout cart for a given user (by token) |
| `get_order_status` | Retrieve status + items of an order |
| `list_genres` | List all available genres |

Bob's agent can compose these tools to answer questions such as:
- *"Do you have any sci-fi books under $15?"*
- *"Place an order for books 3 and 7 for user 42"*
- *"What is the status of order #18?"*

---

## Security

- Passwords hashed with **bcrypt** (passlib, 12 rounds)
- All write endpoints protected by **OAuth2 Bearer JWT** dependency
- Admin-only routes protected by a `require_admin` dependency
- MCP server validates a **Bearer API key** via the `Authorization` header
- Rate-limiting on `/auth/*` via `slowapi`

---

## Project Layout

```
bookstore-backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app factory + router registration
│   ├── database.py        # SQLAlchemy async engine + session factory
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── deps.py            # Shared FastAPI dependencies (auth, db session)
│   ├── routers/
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── cart.py
│   │   └── orders.py
│   └── services/
│       ├── book_service.py
│       ├── order_service.py
│       └── user_service.py
├── mcp_server/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point (registerTool wrappers)
│   └── tools.py           # Tool implementations calling DB services
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_books.py
│   ├── test_cart.py
│   └── test_orders.py
├── .env.example
├── requirements.txt
└── ARCHITECTURE.md
```

---

## IBM Bob MCP Config Snippet

Add this block to your Bob MCP settings JSON to connect the agent:

```json
{
  "mcpServers": {
    "bookstore": {
      "type": "streamable-http",
      "url": "http://localhost:3100/mcp",
      "headers": {
        "Authorization": "Bearer <MCP_API_KEY>"
      },
      "alwaysAllow": ["search_books", "get_book", "check_stock", "list_genres"]
    }
  }
}
```
