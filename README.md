
Infra Cost Calculator (Local)

Backend: Flask (port 5001)
Frontend: Next.js + Tailwind (port 3000)

Run backend first, then frontend.

## Backend - Development & Tests 🔧

1. Install runtime dependencies (from project root):

```bash
cd backend
python3 -m pip install -r requirements.txt
```

2. (Optional) Install dev/test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

3. Run the server locally:

```bash
python3 app.py
# or: FLASK_APP=app FLASK_ENV=development flask run --port=5001
```

4. Run tests:

```bash
python3 -m pytest -q
```

Notes:

## Frontend - Development & Local Testing 🖥️

1. Configure the API URL (optional - defaults to http://127.0.0.1:5001):

```bash
# Copy the example and edit if needed
cp frontend/.env.local.example frontend/.env.local
```

2. Install dependencies and run the dev server:

```bash
cd frontend
npm install
npm run dev -p 3000
# open http://localhost:3000
```

3. Manual test (UI):

Screenshot (desktop):

![UI snapshot](frontend/screenshots/overview.png)

## E2E tests (Playwright)

1. Install Playwright dev dependency and browsers:

```bash
cd frontend
npm install
npx playwright install
```

2. Start the dev server (in one terminal):

```bash
npm run dev -p 3000
```

3. Run E2E tests (in another terminal):

```bash
npm run test:e2e
```

The E2E verifies Azure and GCP totals are displayed and non-zero using a headless Chromium instance.


---

## CI status

The project runs unit tests and E2E tests on PRs via GitHub Actions. Add a status badge after you push the repo to GitHub (replace <OWNER> and <REPO>):

![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/backend-ci.yml/badge.svg)

How to update badge for your repo:

1. Replace `<OWNER>` and `<REPO>` in the badge URL above with your GitHub username/organization and repository name.
2. After pushing to GitHub, visit the Actions tab → `backend-ci` to view logs for any failed jobs.

Tip: If you want, tell me your GitHub `owner/repo` and I’ll add the badge for you.




