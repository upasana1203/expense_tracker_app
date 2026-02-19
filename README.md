# Smart Expense Tracker and Financial Analyzer

Production-ready full-stack personal finance app built with Django + DRF + PostgreSQL and React.

## Features
- JWT authentication (register, login, logout, refresh)
- User-isolated data access for all financial records
- Transaction management: income, expense, saving (CRUD + filter + search)
- Category management (default + custom categories)
- Savings module with goals, contributions, progress %, remaining amount
- Budget planner with monthly usage and alerts at 80%/100%
- Smart financial insights:
  - Highest spending category
  - Month-over-month expense comparison
  - Expense increase/decrease percentage
  - Saving rate and income/expense ratio
  - Budget overuse alerts
  - Unusual spending spike detection
  - Recommended monthly saving target
- Analytics charts:
  - Category distribution (pie)
  - Expense trends (line)
  - Savings growth (line)
  - Income vs expense (bar)
- Report exports: CSV, Excel, PDF
- Responsive dashboard UI with dark/light mode
- Toast notifications and loading states

## Tech Stack
- Backend: Django, Django REST Framework, PostgreSQL, SimpleJWT
- Frontend: React (hooks), Vite, Recharts, Axios

## Folder Structure
```text
smart_expense_tracker/
  backend/
    config/
    users/
    finance/
      services/
      management/commands/seed_data.py
    manage.py
    requirements.txt
    .env.example
  frontend/
    src/
      api/
      components/
      context/
      hooks/
      layout/
      pages/
    package.json
    .env.example
  docs/screenshots/
  README.md
```

## Backend Setup (Django + PostgreSQL)
1. `cd backend`
2. Create env file: copy `.env.example` to `.env`
3. Create virtual environment and activate it
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Create PostgreSQL database named `smart_expense` (or update `.env`)
6. Run migrations:
   - `python manage.py migrate`
7. Seed demo data (optional):
   - `python manage.py seed_data`
8. Run server:
   - `python manage.py runserver`

## Frontend Setup (React)
1. `cd frontend`
2. Copy `.env.example` to `.env`
3. Install dependencies:
   - `npm install`
4. Start dev server:
   - `npm run dev`

Frontend URL: `http://localhost:5173`
Backend URL: `http://127.0.0.1:8000`

## Demo Login (after seed)
- Email: `demo@example.com`
- Password: `DemoPass123!`

## API Documentation (Core)
Base URL: `http://127.0.0.1:8000/api`

### Auth
- `POST /auth/register/`
- `POST /auth/login/` (returns `access`, `refresh`)
- `POST /auth/refresh/`
- `POST /auth/logout/`

### Resources (JWT required)
- `GET/POST /categories/`
- `GET/POST /transactions/`
- `GET/PUT/PATCH/DELETE /transactions/{id}/`
- `GET/POST /saving-goals/`
- `GET/POST /saving-contributions/`
- `GET/POST /budgets/`

### Analytics & Dashboard
- `GET /dashboard/summary/`
- `GET /analytics/insights/`
- `GET /analytics/charts/`

### Reports
- `GET /reports/export/csv/`
- `GET /reports/export/excel/`
- `GET /reports/export/pdf/`

## Security
- Password hashing through Django auth system
- JWT auth + refresh token rotation + blacklist logout
- Per-user queryset isolation in all viewsets/endpoints
- Serializer-level input validation
- DRF throttling/rate limiting enabled
- CSRF middleware active in Django stack

## Notes for Production
- Set `DJANGO_DEBUG=False`
- Use strong `DJANGO_SECRET_KEY`
- Configure secure CORS and allowed hosts
- Add HTTPS, reverse proxy, and static/media serving strategy
- Add unit/integration tests and CI pipeline

## Suggested Screenshots
Add images in `docs/screenshots/`:
- `dashboard.png`
- `transactions.png`
- `savings.png`
- `budget.png`

