#Bookit API

A REST API with user authentication, service management, and review features. Includes PostgreSQL database integration and Alembic migrations.

## Features

* User registration & authentication (JWT)
* Service listing and booking
* Booking status management
* User reviews for services
* PostgreSQL database with SQLAlchemy ORM
* Alembic for database migrations
* Dockerized for easy development
* Admin user management

## Requirements

* Python 3.10+
* PostgreSQL
* Docker (optional, for containerized setup)

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/bookit-api.git
cd bookit-api

2. Configure Environment Variables
Edit the .env file with your database credentials:

env
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/bookitdb
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
LOG_LEVEL=INFO

3. Install Dependencies
bash
pip install -r requirements.txt

4. Run Database Migrations
bash
alembic upgrade head

5. Start the API
bash
uvicorn app.main:app --reload
Visit http://localhost:8000/docs for the interactive API docs.

Creating an Admin User
All users register as regular users by default. To test admin-protected endpoints, you need to create an admin user.

Method 1: Using the Admin Creation Endpoint
Use the /users/create-admin endpoint via Swagger UI (http://localhost:8000/docs):

Find POST /users/create-admin
Click "Try it out"
Fill in the parameters:
name: "Admin User"
email: "admin@bookit.com"
password: "admin123"
Click "Execute"
Via curl:

bash
curl -X POST "http://localhost:8000/users/create-admin?name=Admin%20User&email=admin@bookit.com&password=admin123"
Method 2: Using Python Script
Create a file called create_admin.py in your project root:

python
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "admin@bookit.com").first()
    if admin:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin = User(
        name="Admin User",
        email="admin@bookit.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    
    db.add(admin)
    db.commit()
    print("Admin user created successfully!")
    print("Email: admin@bookit.com")
    print("Password: admin123")
    
    db.close()

if __name__ == "__main__":
    create_admin()
Run it:

bash
python create_admin.py
Login as Admin
After creating the admin user, login using /auth/login:

json
{
  "email": "admin@bookit.com",
  "password": "admin123"
}
This returns an access token that you can use for admin-protected endpoints (creating services, viewing all bookings, etc.).

Docker Usage
To run the API and database with Docker Compose:

bash
docker compose up --build
Project Structure
app/
  ├── main.py
  ├── models/
  ├── routers/
  ├── schemas/
  ├── services/
  ├── repositories/
  ├── utils/
  ├── database.py
  ├── config.py
  ├── dependencies.py
alembic/
  ├── versions/
  ├── env.py
tests/
requirements.txt
.env

API Endpoints
Authentication

POST /auth/register - Register new user
POST /auth/login - Login user
POST /auth/refresh - Refresh access token
POST /auth/logout - Logout user

User Management

GET /me - Get current user profile
PATCH /me - Update current user profile
POST /users/create-admin - Create admin user (for testing)

Services

GET /services - List services (public)
GET /services/{id} - Get service details (public)
POST /services - Create service (admin only)
PATCH /services/{id} - Update service (admin only)
DELETE /services/{id} - Delete service (admin only)

Bookings

POST /bookings - Create booking
GET /bookings - List bookings (user: own, admin: all)
GET /bookings/{id} - Get booking details
PATCH /bookings/{id} - Update booking
DELETE /bookings/{id} - Delete booking

Reviews

POST /reviews - Create review
GET /reviews/{id} - Get review details
GET /services/{id}/reviews - Get service reviews
PATCH /reviews/{id} - Update review (owner only)
DELETE /reviews/{id} - Delete review (owner/admin)

License
MIT

Author
Mary Okpe