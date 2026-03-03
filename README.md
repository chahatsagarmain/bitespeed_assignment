# Bitespeed Assignment Service

Basic FastAPI service implementing `/identify` endpoint with PostgreSQL.

## Structure
```
app/
  database.py        # SQLAlchemy setup (Postgres)
  main.py            # FastAPI application
  models/
    contact.py       # Contact ORM model
  routers/
    identify.py      # identify endpoint logic

contacts.db          # (not used with Postgres)
venv/                # Python virtual environment
```

## Usage

1. Create and activate virtualenv:
   ```powershell
   python -m venv venv
   .\\venv\\Scripts\\Activate.ps1
   pip install fastapi sqlalchemy uvicorn psycopg2-binary
   ```
2. Start PostgreSQL and create a database, then set `DATABASE_URL` environment variable.
   ```powershell
   $env:DATABASE_URL="postgresql://postgres:password@localhost/contacts"
   ```
3. Run the service:
   ```powershell
   uvicorn app.main:app --reload
   ```
4. Send POST requests to `http://localhost:8000/identify` with JSON body.

Example:
```json
{
  "email": "mcfly@hillvalley.edu",
  "phoneNumber": "123456"
}
```

## Notes
- database schema matches problem description.
- logic handles creation of primary/secondary contacts and links.

