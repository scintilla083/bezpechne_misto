# ---- BASE PYTHON IMAGE ----
FROM python:3.13-slim

# ---- SYSTEM DEPENDENCIES ----
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- WORKDIR ----
WORKDIR /app

# ---- COPY PROJECT ----
COPY . /app

# ---- INSTALL DEPENDENCIES ----
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ---- DJANGO STATIC DIRECTORY ----
RUN mkdir -p /app/static
RUN mkdir -p /app/media

# ---- RUN AS NON-ROOT USER (security best practice) ----
RUN useradd -ms /bin/bash djangouser
USER djangouser

# ---- DEFAULT COMMAND (overridden in docker-compose) ----
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
