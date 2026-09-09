# Image de base officielle Python.
FROM python:3.12-slim

# Évite la création de fichiers .pyc.
# Permet aussi d'afficher immédiatement les logs Python.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Tous les fichiers de l'application seront placés ici.
WORKDIR /app

# On copie d'abord les dépendances.
# Cela permet à Docker de réutiliser son cache
# si seul le code source change.
COPY requirements.txt .

# Installation des dépendances Python.
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application.
COPY app.py .
COPY core.py .

# Railway fournit PORT au moment du lancement.
# 8080 sert simplement de valeur indicative.
EXPOSE 8080

# Commande de démarrage du conteneur.
CMD ["python", "app.py"]