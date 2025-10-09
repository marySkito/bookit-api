# BookIt API

A production-ready REST API for a bookings platform.

## Features
- User registration & authentication (JWT)
- Service listing and booking
- Booking status management
- User reviews for services
- PostgreSQL database with SQLAlchemy ORM
- Alembic for database migrations
- Dockerized for easy development
- Admin user management

## Live Demo
- **API Docs:** [https://bookit-api-demo.vercel.app/docs](https://bookit-api-demo.vercel.app/docs)

## Test Credentials

**Admin User:**
- Email: admin@bookit-demo.com
- Password: AdminPass2025

**Regular User:**
- Email: testuser@bookit-demo.com
- Password: TestPass2025

## Quick Test

1. Visit the [API Docs](https://bookit-api-demo.vercel.app/docs)
2. Login with credentials above
3. Copy your `access_token`
4. Click the Authorize button
5. Paste token and test endpoints

## Local Setup

```bash
git clone https://github.com/marySkito/bookit-api.git
cd bookit-api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set up your `.env` file with your database credentials, then run migrations:

```bash
alembic upgrade head
```

## Creating an Admin User

You can create an admin user via the `/users/create-admin` endpoint or use the test credentials above for local development.

## Docker Usage

```bash
docker compose up --build
```

## Project Structure

- app/
  - main.py
  - models/
  - routers/
  - schemas/
  - services/
  - repositories/
  - utils/
  - database.py
  - config.py
  - dependencies.py
- alembic/
  - versions/
  - env.py
- tests/
- requirements.txt
- .env

## API Endpoints

See [API Docs](https://bookit-api-demo.vercel.app/docs) for a full list.

## License

MIT

## Author

Mary Okpe