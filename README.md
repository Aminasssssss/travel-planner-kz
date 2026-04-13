# Travel Planner KZ

Smart travel guide for Kazakhstan — build day-by-day itineraries by city, budget, and interests.
552 places across 22 cities. AI-powered recommendations. Genetic route optimization.

## Team

| Name | GitHub |
|------|--------|
| Amina Zhumatayeva | @Aminasssssss |
| Sandugash Kelgenbayeva | @sleepiingatlast |
| Ayana Nauryzbayeva | @Ayanan2022 |

## Tech Stack

- **Frontend:** Angular 17+, TypeScript, Leaflet.js
- **Backend:** Django 5.2, Django REST Framework
- **Auth:** JWT (SimpleJWT)
- **ML:** scikit-learn (KNN, K-means), Genetic Algorithm
- **APIs:** OpenWeatherMap, Unsplash, Claude AI
- **Database:** SQLite

## Features

- Interactive map with day-by-day route visualization and heatmap
- AI chat-guide for place recommendations
- Genetic TSP algorithm for route optimization (up to 44% distance saved)
- Burnout Detector — prevents over-scheduling
- KNN place recommendations based on user preferences
- Weather forecast and real place photos via Unsplash
- City event calendar with sponsored placements
- Share itinerary via public link
- Budget estimation and seasonal match analysis

## Quick Start

### Backend

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver

### Frontend

cd frontend
npm install
ng serve

App: http://localhost:4200
API: http://localhost:8000/api/

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/ | User registration |
| POST | /api/auth/login/ | JWT login |
| GET | /api/destinations/ | List all cities |
| GET | /api/destinations/:id/places/ | Places in city |
| POST | /api/itineraries/generate/ | Generate itinerary |
| POST | /api/itineraries/:id/optimize/ | Genetic TSP optimization |
| GET | /api/itineraries/:id/analysis/ | Burnout analysis + stats |
| GET | /api/cities/:id/events/ | City events |
| POST | /api/ai/chat/ | AI Chat-guide |

## Project Structure

```
travel-planner-kz/
├── backend/
│   ├── config/
│   ├── travel/
│   │   ├── ml/           # TSP, KNN, clustering, AI
│   │   ├── models.py
│   │   └── views.py
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── pages/
│       ├── components/
│       └── services/
└── README.md
```

## Notes

- 552 real places across 22 Kazakhstan cities
- Genetic TSP saves up to 44% travel distance
- Burnout Detector prevents over-scheduling
- Monetization-ready event system

KBTU — Web Development 2026