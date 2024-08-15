FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt .

RUN python -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 5000

ENV PATH="/app/venv/bin:$PATH"
ENV FLASK_APP=app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]