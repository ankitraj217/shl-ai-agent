# SHL Recruiter Copilot Frontend

React + TypeScript + Vite frontend for the existing FastAPI SHL assessment recommender. In production, FastAPI serves the compiled build from `frontend/dist` so frontend and backend run from one host.

## Run

Start the backend first:

```powershell
uvicorn app.main:app --reload --port 8080
```

Then start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/chat` and `/health` to `http://127.0.0.1:8080`, so the frontend can use the existing FastAPI endpoints without changing backend schemas.

## Build

```powershell
npm run build
```

The build output is written to:

```text
frontend/dist
```

FastAPI serves this directory in production.

## Configuration

For same-origin production deployment, leave `VITE_API_BASE_URL` unset so the app calls relative `/chat`.

For a temporary separate development backend, set:

```text
VITE_API_BASE_URL=https://your-backend-host
```

When unset, the frontend calls relative `/chat`, which is ideal for local Vite proxying and FastAPI-served production.

## Structure

- `src/components`: reusable UI components
- `src/pages`: page-level composition
- `src/services`: API calls
- `src/types`: TypeScript API contracts

The app keeps conversation history in browser state and sends the full message list to `/chat` on every request because the backend is stateless.
