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

## Product photos

Product cards show a real photo automatically if a matching file exists in
`static/images/products/`, falling back to a category icon otherwise. Save
each photo with the exact filename below (JPG or PNG both work, just keep
the `.jpg` extension in the filename or update `app.py` to match):

| Product | Flavor | Filename |
| --- | --- | --- |
| Whey HD | Chocolate Cookie | `whey-hd-chocolate-cookie.jpg` |
| Whey HD | Strawberry Cake | `whey-hd-strawberry-cake.jpg` |
| Whey HD | Milk and Cookies | `whey-hd-milk-and-cookies.jpg` |
| Whey HD | Blueberry Muffin | `whey-hd-blueberry-muffin.jpg` |
| Whey HD | Salted Caramel | `whey-hd-salted-caramel.jpg` |
| ISO HD | Cookies and Cream | `iso-hd-cookies-and-cream.jpg` |
| ISO HD | Chocolate Brownie | `iso-hd-chocolate-brownie.jpg` |
| Micronized Creatine | Unflavored | `micronized-creatine-unflavored.jpg` |
| Best BCAA | Fruit Punch | `best-bcaa-fruit-punch.jpg` |
| Best BCAA | Watermelon Ice | `best-bcaa-watermelon-ice.jpg` |
| 1.M.R The OG Formula | Fruit Punch | `1mr-og-fruit-punch.jpg` |
| 1.M.R The OG Formula | Sour Gummy | `1mr-og-sour-gummy.jpg` |
| CLA + Carnitine | Snow Cone | `cla-carnitine-snow-cone.jpg` |
| CLA + Carnitine | Rainbow Ice | `cla-carnitine-rainbow-ice.jpg` |
| RoxyLean | Fat Burner & Thermogenic | `roxylean.jpg` |

## Cart, checkout, and orders

Customers can add products to a cart, then check out with a delivery address
and one of these payment methods: Cash on Delivery, Bank Transfer, or
Credit/Debit Card and Mobile Wallet (both marked "coming soon" until a real
payment processor is integrated). Each completed order is appended as a line
of JSON to `orders.jsonl` in the project root — **this file is gitignored on
purpose**, since it contains customer names, phone numbers, and addresses
and must never be committed or pushed to a public repo. Back it up
separately if you need to keep order history.

## Deploy

This app ships with a `Procfile` and `gunicorn`, so it can be deployed as-is
to any host that supports the Procfile convention (Render, Railway, etc.):

1. Create a new Web Service on your host and connect it to this GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT` (already in the Procfile)
4. Set a `SECRET_KEY` environment variable on the host (used to sign cart
   sessions) — without it, the app falls back to an insecure default that's
   fine for local development only.
5. Once deployed, add your custom domain in the host's dashboard and follow
   its instructions for the DNS records to add at your domain registrar.
