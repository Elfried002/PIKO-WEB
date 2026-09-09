# Image de base officielle Python.
FROM python:3.12-slim

# Évite la création de fichiers .pyc.
# Permet aussi d'afficher immédiatement les logs Python.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail de l'application.
WORKDIR /app

# Copie des dépendances.
COPY requirements.txt .

# Installation des dépendances Python.
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'ensemble de l'application.
# Cela inclut notamment :
# - app.py
# - core.py
# - templates/
# - static/
COPY . .

# Port utilisé par Railway.
EXPOSE 8080

# Démarrage de l'application.
CMD ["python", "app.py"]