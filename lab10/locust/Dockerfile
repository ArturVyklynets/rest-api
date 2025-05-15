FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["locust", "-f", "locustfile.py", "--host", "http://fastapi_app:8000"]
