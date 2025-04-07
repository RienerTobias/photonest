# Basis-Image
FROM python:3.12

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY ./photonest_server .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run Migrate
RUN python manage.py migrate

# Expose Port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "photonest_server.wsgi:application"]
