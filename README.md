# hood_algo2

Python/Jupyter workspace for HoodAlgo research, Robinhood market data collection, sentiment/news scraping, and a Flask control UI.

## Project Map

- `functions.py` - main scraping, Robinhood data, news, sentiment, portfolio, and trade helper functions.
- `app/app.py` - Flask app entry point. Runs on port `5009`.
- `app/endpoints/` - Flask routes and API endpoints for the UI and algo controls.
- `app/templates/` - Jinja templates for the web app.
- `app/static/` - frontend assets, screenshots, fonts, icons, and media.
- `cookbook/` - reusable local helper modules for MySQL, Selenium, text helpers, and git notes.
- `*.ipynb` - research notebooks and manual workflow notebooks.
- `robinhood_universe.csv` and `robinhood_universe_filtered.csv` - local market/universe datasets.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment Variables

The app expects local secrets/config through environment variables. Do not commit real values.

```bash
export MYSQL_HOST="127.0.0.1"
export MYSQL_USER="root"
export MYSQL_PASSWORD="your_mysql_password"
export FLASK_SECRET_KEY="your_local_flask_secret"
export STRIPE_BACK_END_KEY="your_stripe_secret_key"
export STRIPE_FRONT_END_KEY="your_stripe_publishable_key"
```

## Run The Flask App

From the app directory:

```bash
cd app
python app.py
```

Then open:

```text
http://127.0.0.1:5009
```

## Git Basics

Check local changes:

```bash
git status
git diff
```

Commit changes:

```bash
git add .
git commit -m "Describe the change"
git push
```

Revert uncommitted changes to a file:

```bash
git restore path/to/file
```

## Notes

- Private key files, `.env` files, notebook checkpoints, cache folders, and local system artifacts are ignored by git.
- The app currently depends on a local MySQL database named `new_algo_db`.
- Selenium helpers assume Chrome and a local Chrome profile path under `/Users/deanemarks/`.
