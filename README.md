# elgargni-shop

A business landing page built with Flask.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Test

```bash
pytest
```

## Deploy

This app ships with a `Procfile` and `gunicorn`, so it can be deployed as-is
to any host that supports the Procfile convention (Render, Railway, etc.):

1. Create a new Web Service on your host and connect it to this GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT` (already in the Procfile)
4. Once deployed, add your custom domain in the host's dashboard and follow
   its instructions for the DNS records to add at your domain registrar.
