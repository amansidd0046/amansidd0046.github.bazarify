# Bazarify — Django Backend

A Django + Django REST Framework backend for the Bazarify storefront.
The original single-file frontend is now served by Django and talks to a
real API for products, a **server-side session cart**, and checkout —
no data is stored in the browser.

## What's included

- **`shop` app**
  - `Product` model (24 seeded demo products across 6 categories)
  - `Order` / `OrderItem` models for placed orders
  - Cart stored in the Django **session** (works across page reloads,
    no localStorage/cookies-holding-data on the client)
- **REST API** (see below)
- **`templates/index.html`** — the original storefront UI, now fetching
  from the API instead of a hardcoded JS array

## Setup

```bash
cd bazarify_backend
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_products    # loads the 24 demo products
python manage.py createsuperuser  # optional, for /admin/

python manage.py runserver
```

Then open **http://127.0.0.1:8000/** — that's the storefront, served
directly by Django. The Django admin is at **http://127.0.0.1:8000/admin/**.

## API endpoints

All endpoints are under `/api/`.

| Method | Path                 | Description                                   |
|--------|----------------------|------------------------------------------------|
| GET    | `/api/products/`     | List products. Optional `?category=` and `?q=` |
| GET    | `/api/cart/`         | Current session's cart                         |
| POST   | `/api/cart/add/`     | `{ "sku": "p01", "qty": 1 }` — add to cart      |
| POST   | `/api/cart/update/`  | `{ "sku": "p01", "qty": 3 }` — set exact qty (≤0 removes) |
| POST   | `/api/cart/remove/`  | `{ "sku": "p01" }` — remove line item          |
| POST   | `/api/checkout/`     | Places the order, see body below               |
| POST   | `/api/auth/register/` | `{ "username", "password", "email"?, "first_name"? }` — creates an account and logs in |
| POST   | `/api/auth/login/`    | `{ "username", "password" }`                  |
| POST   | `/api/auth/logout/`   | Logs the current session out                  |
| GET    | `/api/auth/me/`       | `{ "authenticated": false }` or the current user |
| GET    | `/api/orders/mine/`   | Order history for the logged-in user (401 if not logged in) |

**Checkout body:**

```json
{
  "full_name": "Asha Rao",
  "phone": "9876543210",
  "address_line": "12 Market Row",
  "city": "Lucknow",
  "pincode": "226001",
  "payment_method": "cod"   // "cod" | "upi" | "card"
}
```

The cart must be non-empty or this returns `400`. On success it creates
an `Order` + `OrderItem`s, empties the session cart, and returns the
order (including an `estimated_delivery` date, 5 days out).

## Accounts

- Login/Register is one modal in `templates/index.html` (an "Account" icon
  in the header) — no separate pages, everything is still the single file.
- Registration logs the user in immediately.
- **Checkout still works for guests.** If you're logged in, the order is
  linked to your account (`Order.user`) and shows up in
  `GET /api/orders/mine/`; if not, it's just recorded with the shipping
  details you typed in (same as before).
- Auth uses Django's built-in session auth — no extra tokens to manage,
  it rides on the same session cookie as the cart.

## Notes on the cart

- The cart lives in `request.session`, keyed by product SKU → quantity.
- Because it's server-side, it needs the Django session cookie, which is
  set automatically the first time the frontend calls the API.
- POST requests use Django's CSRF protection. The frontend reads the
  `csrftoken` cookie and sends it back as the `X-CSRFToken` header — this
  works because the frontend is served from the same Django app (no CORS
  needed). If you later split the frontend into its own app/domain,
  you'll need to add `django-cors-headers` and handle CSRF/session
  cookies cross-site.

## Extending this

- Add real user accounts (`django.contrib.auth`) if you want order
  history per customer instead of anonymous sessions.
- Swap SQLite for Postgres in `config/settings.py` for anything beyond
  local development.
- Add pagination to `/api/products/` once the catalog grows.
