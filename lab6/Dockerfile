FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python utils/init_db.py && flask run --host=0.0.0.0 --port=5002
