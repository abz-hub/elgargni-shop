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

## Dietary coaching subscription

The homepage has a pricing section for the "Full Coaching Plan" (120 LYD/month,
defined in `app.py` as `SUBSCRIPTION_PLAN`). Signups go through `/subscribe`,
reuse the same payment method selection as checkout, and are appended to a
gitignored `subscriptions.jsonl` — same PII rules as `orders.jsonl` above.
There's no recurring/automatic billing (no payment processor is integrated);
each month the coach follows up with the customer directly using the contact
info collected at signup.

## Languages (English / Arabic)

The whole site is bilingual. All UI text lives in `translations.py` as a
flat `{key: string}` dict per language, looked up via a `t(key, **kwargs)`
helper (bound to the current session's language and exposed to every
template as `{{ t('some.key') }}`). Product names/flavors are proper nouns
and stay untranslated by design.

- Switch language via the globe toggle in the navbar, or by visiting
  `/set-language/en` or `/set-language/ar` directly — the choice is stored
  in the session and persists across pages.
- Arabic renders right-to-left (`<html dir="rtl">`) with a dedicated Arabic
  web font (Tajawal); English uses Bebas Neue/Inter as before.
- To add a new string: add a key to both the `"en"` and `"ar"` dicts in
  `translations.py`, then reference it with `{{ t('your.key') }}` in a
  template (or `translate('your.key', lang=lang)` in `app.py` for
  server-side text like form validation errors).

## Calculators

`/calculators` has two tools, computed instantly client-side in
`static/js/calculators.js` (no server round-trip, no page reload):

- **Supplement Calculator**: recommends a daily protein target (1.6–2.2 g/kg
  depending on goal) and a 2-product stack per goal — muscle gain (whey +
  creatine), weight loss/cutting (whey isolate + CLA+Carnitine as the
  L-carnitine source), performance (creatine + 1.M.R pre-workout as the
  citrulline source). Each recommended product is a real item from the
  catalog with a working Add to Cart form (server-rendered, not fake).
- **Calorie & Macro Calculator**: BMR via Mifflin-St Jeor, TDEE via activity
  multiplier, calorie adjustment by goal (+300 muscle gain, −500 weight loss,
  −300 cutting, 0 performance), macro split (protein fixed at 2 g/kg, fat 25%
  of calories, carbs the remainder), visualized with a CSS conic-gradient
  donut chart.

Both goal→recommendation mapping (`CALCULATOR_RECOMMENDATION_SETS`,
`CALCULATOR_GOAL_TO_SET`) and the protein-per-kg targets
(`CALCULATOR_PROTEIN_PER_KG`) live in `app.py` — update those to change which
products get recommended or the protein ratios. The BMR/TDEE/macro formulas
themselves live in `calculators.js`.

## Order notifications (Telegram)

When an order or subscription is placed, the app can send the owner an
instant Telegram message with the full details. It is **off by default**
and only activates when both environment variables below are set — if
they are missing, the site works normally and simply sends nothing.
A notification failure never blocks an order (errors are swallowed).

Set these on the host (e.g. Render dashboard → Environment):

- `TELEGRAM_BOT_TOKEN` — from @BotFather after `/newbot`.
- `TELEGRAM_CHAT_ID` — your personal chat id (message @userinfobot to get
  it, or send your bot a message and read it from
  `https://api.telegram.org/bot<token>/getUpdates`).

Implemented with the standard library (`urllib`), no extra dependency.
See `notify_telegram()` in `app.py`.

## Deploy

### Render (one-click blueprint)

The repo has a `render.yaml` blueprint that configures everything
automatically (build, start command, free plan, auto-generated
`SECRET_KEY`). To deploy:

1. Sign up at [render.com](https://render.com) with the GitHub account that
   owns this repo.
2. Click **New → Blueprint**, pick the `elgargni-shop` repo, and click
   **Apply**.
3. Wait for the build — you'll get a live URL like
   `elgargni-shop.onrender.com`.

### Any other Procfile host

This app also ships with a `Procfile` and `gunicorn`, so it works on any
Procfile-convention host (Railway, etc.):

1. Create a new Web Service on your host and connect it to this GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT` (already in the Procfile)
4. Set a `SECRET_KEY` environment variable on the host (used to sign cart
   sessions) — without it, the app falls back to an insecure default that's
   fine for local development only.
5. Once deployed, add your custom domain in the host's dashboard and follow
   its instructions for the DNS records to add at your domain registrar.
