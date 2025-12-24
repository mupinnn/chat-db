FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE ${PORT}

CMD if [ "$FLASK_ENV" = "production" ]; then \
      gunicorn --bind 0.0.0.0:${PORT} --workers 4 --threads 2 app:app; \
    else \
      python app.py; \
    fi
