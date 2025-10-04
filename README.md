Bookit API

A m with user authentication, service management, and review features.
Includes PostgreSQL database integration and Alembic migrations.

Features
User registration & authentication (JWT)
Service listing and booking
Booking status management
User reviews for services
PostgreSQL database with SQLAlchemy ORM
Alembic for database migrations
Dockerized for easy development
Requirements
Python 3.10+
PostgreSQL
Docker (optional, for containerized setup)
Setup

1. Clone the repository
git clone https://github.com/yourusername/bookit-api.git
cd bookit-api

2. Configure Environment Variables
Edit the .env file with your database credentials:

DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/bookitdb
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
LOG_LEVEL=INFO

3. Install Dependencies
pip install -r requirements.txt

4. Run Database Migrations
alembic upgrade head

5. Start the API
uvicorn app.main:app --reload
Visit http://localhost:8000/docs for the interactive API docs.

Docker Usage
To run the API and database with Docker Compose:

docker compose up --build
Project Structure
app/
  ├── main.py
  ├── models/
  ├── routers/
  ├── schemas/
  ├── database.py
  ├── config.py
alembic/
  ├── versions/
  ├── env.py
requirements.txt
.env

License
MIT

Author
Mary Okpe