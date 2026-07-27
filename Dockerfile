# Deliberately simple, single-stage for Week 0 - just needs to run locally.
# In Week 8 (Project 1 / CI-CD) you'll rebuild this as a proper multi-stage
# Dockerfile and measure the image size difference - don't optimize this yet.

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
