# Chat DB - A simple app to chat with your database using Gemini

Chat with your database in most human way possible and get the human-friendly response about your question
without the need to understand SQL at all. This app can helps stakeholders to get business insights from their data really fast.

I made this for Hacktiv8 Maju Bareng AI - AI for Data Scientist program's final project.

## Stacks

- Flask
- Gemini 2.5 Flash
- SQLite
- React
- Tanstack Query
- shadcn/ui + Tailwind CSS
- Nginx
- Docker + Docker Compose

## Run locally

### Prepare the Gemini API key and other environment variables

0. Visit https://aistudio.google.com/api-keys and create new API key
1. Copy the `web/.env.example` to `web/.env.local` and `api/.env.example` to `.env`

```sh
cp web/.env.example web/.env.local
cp api/.env.example web/.env
```

2. Fill the environment variables

```sh
# web/.env.local
VITE_API_URL=http://localhost:5000/api

# api/.env
GOOGLE_API_KEY=<place your gemini API key here>
ALLOWED_CORS_ORIGIN=http://localhost:5174
FLASK_ENV=development
PORT=5000
```

Next follow each services setup below.

### Frontend (`web`)

0. Make sure you have Bun installed, because the `Dockerfile` and the compose config for the `web` is only for production purpose; at least for right now
1. Install dependencies

```sh
cd web && bun install
```

2. Run

```sh
cd web && bun dev
```

3. You can access the frontend at http://localhost:5174

### Backend (`api`)

0. Make sure you have Docker and `docker-compose` installed
1. Run

```sh
docker compose up -d
```

2. Seed the data to the database first before accessing the backend

```sh
# this will seed the `api/data/coffee-sales-datasets.csv` to the SQLite database
docker compose exec api python seed.py
```

3. You can access the backend at http://localhost:5000 and try to access http://localhost:5000/api/health in your browser, `curl`, or any API tools to make sure it works.

## Acknowledgement and resources

- https://github.com/ardyadipta/gemini_chatbot_sql/
- https://github.com/leodeveloper/google-gemini-chat-with-sqlserver/
- https://github.com/ardyadipta/gemini_chatbot_qna
- https://blog.laozhang.ai/api-guides/gemini-api-free-tier/
- https://photokheecher.medium.com/building-a-smart-text-to-sql-system-with-rag-and-langchain-1958c041d4f4

## Gallery

![main page](./screenshots/dashboard2.png)

![chat sheet opened](./screenshots/chat%20opened2.png)
