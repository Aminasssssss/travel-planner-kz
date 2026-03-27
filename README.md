# travel-planner-kz
Travel Planner for Kazakhstan — Angular + Django | KBTU Web Dev 2026
# Travel Planner KZ 🇰🇿

A smart travel guide for Kazakhstan — build personalized day-by-day itineraries based on your city, budget, and interests.

## Features

- 🗺️ Auto-generated itineraries by city, duration, and budget
- 📍 Interactive map with route visualization (Leaflet.js)
- 🔐 JWT authentication (login, logout, protected routes)
- 💾 Save, edit, and delete your personal itineraries
- 🌍 Browse destinations and places across Kazakhstan

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Angular 17+ |
| Backend | Django + Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Map | Leaflet.js |

## Team

| Name | GitHub |
|------|--------|
| Name 1 | @username1 |
| Name 2 | @username2 |
| Name 3 | @username3 |

## Project Structure
```
travel-planner-kz/
├── backend/        # Django project
└── frontend/       # Angular project
```

## Getting Started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
ng serve
```

## API

Backend runs on `http://localhost:8000`  
Frontend runs on `http://localhost:4200`

## Course

KBTU — Web Development | Angular + Django | 2026
