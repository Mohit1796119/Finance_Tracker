FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 7860

CMD ["gunicorn", "-w", "1", "-k", "gthread", "-b", "0.0.0.0:7860", "app:app"]
