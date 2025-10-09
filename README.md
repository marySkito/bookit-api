# BookIt API

A production-ready REST API for a bookings platform.

## Live Demo

- **API Docs**: https://your-vercel-url.vercel.app/docs

## Test Credentials

**Admin User:**
- Email: admin@bookit.com
- Password: admin123

**Regular User:**
- Email: testuser@bookit.com  
- Password: testpass123

## Quick Test

1. Visit the [API Docs](https://your-vercel-url.vercel.app/docs)
2. Login with credentials above
3. Copy access_token
4. Click Authorize button
5. Paste token and test endpoints

## Local Setup
```bash
git clone https://github.com/marySkito/bookit-api.git
cd bookit-api
pip install -r requirements.txt
uvicorn app.main:app --reload
