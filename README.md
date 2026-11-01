# crumb — good food, good mood

A neighborhood food ordering project with a React storefront, Express REST API, MongoDB persistence, and a Streamlit edition. The storefront includes kitchen search, cuisine filters, menu cards, cart controls, a checkout confirmation, and order history. The API includes registration and login, restaurant listing/details, order placement/history, and admin order/restaurant endpoints.

## Run locally

Requirements: Node.js 20+, npm, and Python 3.10+ for the Streamlit edition. MongoDB is optional for a local demo; without `MONGODB_URI`, the API uses seeded sample kitchens and in-memory demo accounts/orders.

```bash
cp .env.example .env
npm install
npm run dev
```

React runs at `http://localhost:5173`; the API runs at `http://localhost:4000`. To start Streamlit instead, create a Python environment, run `pip install -r requirements.txt`, then `streamlit run app.py`. Set `API_URL` to the reachable Express API URL to enable API-backed account and order operations. Without the API, Streamlit displays sample kitchens.

## REST API

- `GET /api/health`
- `GET /api/restaurants?q=&category=` and `GET /api/restaurants/:id`
- `POST /api/auth/register`, `POST /api/auth/login`
- `POST /api/orders`, `GET /api/orders/mine` (Bearer token)
- `GET /api/admin/orders`, `PATCH /api/admin/orders/:id`, `POST /api/admin/restaurants` (admin Bearer token)

New accounts are customers. For a production admin, promote a user’s `role` to `admin` in MongoDB. Configure `MONGODB_URI`, a strong `JWT_SECRET`, and allowed `CLIENT_ORIGIN` before deployment. Demo-memory data is ephemeral and the default JWT secret is for local development only.

## Deploy

### GitHub Pages + Render

Push this repository to GitHub. The included Pages workflow builds and deploys the React storefront when `main` is updated (enable GitHub Pages with **GitHub Actions** as the build source). The Express API and static frontend can be deployed through the included `render.yaml`; configure the database and origin variables in Render. Update the React API base URL if hosting the API on a separate domain.

### Streamlit Community Cloud

Create a Streamlit Community Cloud app from this repository with `app.py` as the entry point. Add `API_URL` as an app secret/environment variable pointing to a publicly reachable Express API. Streamlit is a Python host, so it runs the included Streamlit client; the React/Express/Mongo stack remains available through the GitHub Pages/Render setup above. The Express service must be deployed separately for persistent accounts and orders.

## Notes

This is a demo ordering experience, not a payment integration. Sample imagery uses food emoji illustrations; connect a payment provider and production account protections before taking real orders.
