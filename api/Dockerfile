ARG FLASK_ENV=development

FROM python:3.14-slim

ARG FLASK_ENV
ENV FLASK_ENV=${FLASK_ENV}
ENV PORT=5000
ENV DATABASE_PATH=/app/data/db.sqlite
ENV CSV_SEED_FILE=/app/data/coffee-sales-datasets.csv

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 5000

CMD if [ "$FLASK_ENV" = "production" ]; then \
      gunicorn --bind 0.0.0.0:${PORT} --workers 4 --threads 2 app:app; \
    else \
      python app.py; \
    fi
