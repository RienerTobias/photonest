# Basis-Image
FROM python:3.12

# Install Node.js für Tailwind
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY ./photonest_server .

# Tailwind CSS builden
RUN cd theme/static_src && \
    npm install -D @tailwindcss/cli daisyui postcss autoprefixer && \
    npx @tailwindcss/cli -i ./src/styles.css -o ../static/css/dist/styles.css --minify

RUN mkdir -p /app/staticfiles && \
    chown -R root:root /app/staticfiles

ENV ALLOWED_HOSTS=*
# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Port
EXPOSE 80

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "photonest_server.wsgi:application"]
