Voici le contenu complet de **`README.md`** pour **PIKO WEB**, prêt à copier-coller.

```markdown
# 🎮 PIKO WEB

> **Pierre • Papier • Ciseaux — version Web**

PIKO WEB est une version web moderne du jeu **Pierre-Papier-Ciseaux**, développée avec **Python, Flask, JavaScript, HTML et CSS**.

Le projet reprend le concept du bot Telegram PIKO et le transpose dans une interface web interactive, responsive et orientée gaming.

---

## 🎯 Présentation

PIKO est un adversaire virtuel permettant au joueur de jouer à Pierre-Papier-Ciseaux directement depuis son navigateur.

Le joueur peut :

- ✊ jouer Pierre ;
- 📄 jouer Papier ;
- ✂️ jouer Ciseaux ;
- 📊 consulter ses statistiques ;
- 🔥 suivre sa série de victoires ;
- 🏆 consulter son rang ;
- 📜 consulter l'historique de ses parties ;
- 🔄 réinitialiser sa progression ;
- 🎵 activer ou désactiver la musique ;
- 🔊 profiter d'effets sonores ;
- ⚔️ jouer des parties rapides ;
- 🏅 participer au système de progression ;
- 🎯 accéder au défi du jour ;
- 🥇 jouer en mode Meilleur de 5.

---

# 🧠 Architecture

PIKO WEB utilise une architecture simple séparant clairement :

- l'interface utilisateur ;
- le serveur web ;
- la logique métier.

```text
                    ┌─────────────────────┐
                    │      Navigateur     │
                    │                     │
                    │ HTML + CSS + JS     │
                    └──────────┬──────────┘
                               │
                               │ HTTP / JSON
                               ▼
                    ┌─────────────────────┐
                    │       Flask         │
                    │      app.py         │
                    │                     │
                    │ Routes API          │
                    │ Sessions            │
                    │ Réponses JSON       │
                    └──────────┬──────────┘
                               │
                               │ appels Python
                               ▼
                    ┌─────────────────────┐
                    │       core.py       │
                    │                     │
                    │ Logique du jeu      │
                    │ Résultats           │
                    │ Statistiques        │
                    │ Rang                │
                    │ Historique          │
                    └─────────────────────┘
```

### Principe important

`core.py` constitue le **cerveau du jeu**.

`app.py` constitue la **couche web**.

`app.js` constitue le **contrôleur de l'interface**.

Le frontend ne doit pas devenir la source de vérité pour les règles métier.

---

# 📁 Structure du projet

```text
PIKO-WEB/
│
├── app.py
├── core.py
├── railway.json
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   └── index.html
│
└── static/
    │
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── app.js
    │
    └── assets/
        ├── piko-logo.png
        ├── bg-music.mp3
        ├── win.mp3
        ├── lose.mp3
        ├── click.mp3
        └── draw.mp3
```

---

# 🧩 Rôle des fichiers

## `app.py`

Serveur Flask de l'application.

Responsabilités :

- servir la page principale ;
- recevoir les requêtes HTTP ;
- appeler `core.py` ;
- gérer la session du joueur ;
- retourner les données JSON ;
- gérer le healthcheck ;
- gérer les erreurs HTTP.

---

## `core.py`

Cœur métier de PIKO.

Responsabilités :

- déterminer le gagnant ;
- générer le coup de PIKO ;
- gérer les statistiques ;
- gérer les séries ;
- gérer l'historique ;
- déterminer le rang ;
- gérer le défi du jour ;
- gérer le mode Meilleur de 5 ;
- réinitialiser les données.

`core.py` ne dépend pas de Flask.

---

## `templates/index.html`

Interface HTML principale.

Elle contient notamment :

- header PIKO ;
- profil du joueur ;
- arène ;
- choix Pierre/Papier/Ciseaux ;
- affichage du résultat ;
- statistiques ;
- historique ;
- boutons d'action.

---

## `static/css/style.css`

Feuille de style de PIKO WEB.

Elle gère :

- thème sombre ;
- interface gaming ;
- effets néon ;
- responsive design ;
- animations ;
- cartes ;
- boutons ;
- arène ;
- résultats ;
- historique.

---

## `static/js/app.js`

Contrôleur frontend.

Responsabilités :

- détecter les clics ;
- communiquer avec Flask ;
- afficher les résultats ;
- mettre à jour les statistiques ;
- afficher l'historique ;
- gérer les animations ;
- gérer la musique ;
- gérer les effets sonores ;
- gérer le compte à rebours.

---

# 🎮 Fonctionnement d'une partie

Lorsqu'un joueur sélectionne un coup :

```text
1. Le joueur clique sur Pierre/Papier/Ciseaux
                    ↓
2. app.js détecte le choix
                    ↓
3. app.js envoie une requête POST /play
                    ↓
4. Flask reçoit le choix
                    ↓
5. Flask appelle core.py
                    ↓
6. core.py génère le coup de PIKO
                    ↓
7. core.py détermine le résultat
                    ↓
8. Les statistiques sont mises à jour
                    ↓
9. Flask retourne une réponse JSON
                    ↓
10. app.js affiche le résultat
```

---

# 🔌 API

PIKO WEB expose plusieurs routes.

## Page principale

```http
GET /
```

Retourne l'interface web.

---

## État du joueur

```http
GET /api/state
```

Retourne :

- statistiques ;
- historique ;
- rang.

Exemple :

```json
{
  "success": true,
  "data": {
    "statistiques": {},
    "historique": [],
    "rang": "Débutant"
  }
}
```

---

## Partie rapide

```http
POST /play
```

Reçoit :

```json
{
  "choix": "pierre"
}
```

Les choix valides sont :

```text
pierre
papier
ciseaux
```

---

## Défi du jour

```http
GET /api/daily-challenge
```

Retourne le défi quotidien associé au joueur.

---

## Démarrer un Meilleur de 5

```http
POST /api/bo5/start
```

Crée un nouveau match Meilleur de 5.

---

## Jouer une manche du Meilleur de 5

```http
POST /api/bo5/play
```

Reçoit :

```json
{
  "choix": "pierre"
}
```

---

## Réinitialiser les données

```http
POST /api/reset
```

Réinitialise :

- statistiques ;
- historique ;
- match Meilleur de 5 en cours.

---

## Healthcheck

```http
GET /healthz
```

Réponse :

```json
{
  "status": "ok",
  "service": "piko-web"
}
```

Cette route est utilisée pour vérifier que l'application Flask fonctionne correctement.

---

# 📊 Système de statistiques

PIKO conserve notamment :

- nombre de victoires ;
- nombre de défaites ;
- nombre d'égalités ;
- série actuelle ;
- meilleure série.

Le nombre total de parties est calculé à partir de :

```text
Victoires + Défaites + Égalités
```

---

# 🏆 Système de rang

Le rang dépend du nombre de victoires.

| Victoires | Rang |
|---:|---|
| 0 – 2 | 🌱 Débutant |
| 3 – 4 | ⭐ Joueur confirmé |
| 5 – 9 | 🔥 Vétéran |
| 10 – 19 | 💎 Expert |
| 20+ | 👑 Légende |

Le calcul du rang est effectué côté serveur.

---

# 🔥 Séries

PIKO conserve une série de victoires consécutives.

Une victoire :

```text
série actuelle + 1
```

Une défaite :

```text
série actuelle → 0
```

La meilleure série est conservée séparément.

---

# 📜 Historique

PIKO conserve les dernières parties du joueur.

Chaque entrée peut contenir :

- choix du joueur ;
- choix de PIKO ;
- résultat.

L'interface affiche la partie la plus récente en premier.

---

# 🎵 Audio

PIKO WEB utilise :

```text
bg-music.mp3
win.mp3
lose.mp3
click.mp3
draw.mp3
```

La musique de fond est :

- activée par défaut ;
- jouée en boucle ;
- contrôlable depuis l'interface.

La préférence musicale est sauvegardée dans `localStorage`.

La lecture automatique peut être bloquée par le navigateur avant la première interaction utilisateur. Le jeu reste fonctionnel même lorsque l'audio est bloqué.

---

# 🔐 Sécurité

Le projet utilise actuellement une session Flask pour conserver les données du joueur.

La clé secrète est fournie par :

```env
PIKO_SECRET_KEY=...
```

Elle ne doit jamais être publiée dans Git.

Le fichier `.env` est donc exclu du dépôt grâce au `.gitignore`.

---

# ⚠️ Limitation actuelle

La session Flask constitue une solution adaptée au **prototype**.

Elle n'est pas encore notre architecture de persistance définitive.

Une version de production pourra utiliser une base de données afin de permettre :

- comptes utilisateurs ;
- authentification ;
- sauvegarde permanente ;
- statistiques persistantes ;
- classement global ;
- profils ;
- badges ;
- progression XP ;
- système de défis ;
- administration ;
- analytics.

---

# 🛠️ Technologies utilisées

## Backend

- Python
- Flask
- Gunicorn

## Frontend

- HTML5
- CSS3
- JavaScript

## Déploiement

- GitHub
- Railway

---

# 📦 Installation locale

## 1. Cloner le projet

```bash
git clone <URL_DU_REPOSITORY>
```

Puis :

```bash
cd PIKO-WEB
```

---

## 2. Créer l'environnement virtuel

### Windows

```bash
python -m venv .venv
```

Activation :

```bash
.venv\Scripts\activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 4. Configurer `.env`

Créer un fichier :

```text
.env
```

avec :

```env
PIKO_SECRET_KEY=TA_CLE_SECRETE
PORT=5000
```

---

## 5. Lancer PIKO

```bash
python app.py
```

L'application sera disponible sur :

```text
http://127.0.0.1:5000
```

---

# 🧪 Vérification

Une fois Flask lancé, vérifier :

```text
http://127.0.0.1:5000/
```

Puis :

```text
http://127.0.0.1:5000/healthz
```

Le healthcheck doit retourner :

```json
{
  "status": "ok",
  "service": "piko-web"
}
```

---

# 🚀 Déploiement Railway

Le projet contient :

```text
railway.json
```

La configuration indique notamment à Railway de démarrer :

```bash
python app.py
```

et d'utiliser :

```text
/healthz
```

comme endpoint de vérification.

Railway doit également recevoir la variable :

```text
PIKO_SECRET_KEY
```

dans les variables d'environnement du service.

Le fichier `.env` local ne doit pas être envoyé sur GitHub.

---

# 🔄 Déploiement

Architecture prévue :

```text
Développement local
        ↓
      Git
        ↓
     GitHub
        ↓
     Railway
        ↓
    PIKO WEB
```

---

# 📌 Principes du projet

PIKO WEB suit plusieurs principes :

### 1. Séparation des responsabilités

```text
Frontend
   ↓
app.py
   ↓
core.py
```

### 2. Source de vérité côté serveur

Les règles métier ne doivent pas être reproduites uniquement dans JavaScript.

### 3. Code modulaire

Chaque couche possède une responsabilité précise.

### 4. Sécurité des secrets

Les secrets sont stockés dans les variables d'environnement.

### 5. Responsive design

L'application doit fonctionner sur :

- ordinateur ;
- tablette ;
- smartphone.

---

# 🔮 Évolutions prévues

## Phase 1 — Prototype

- [x] Interface web
- [x] Flask
- [x] logique métier
- [x] partie rapide
- [x] statistiques
- [x] historique
- [x] rang
- [x] musique
- [x] effets sonores
- [x] session Flask
- [x] healthcheck

## Phase 2 — Fonctionnalités avancées

- [ ] Meilleur de 5 complet côté interface
- [ ] défi du jour complet côté interface
- [ ] système XP
- [ ] badges
- [ ] progression
- [ ] classement

## Phase 3 — Comptes utilisateurs

- [ ] inscription
- [ ] connexion
- [ ] profil
- [ ] persistance en base de données
- [ ] statistiques permanentes

## Phase 4 — Plateforme PIKO

- [ ] classement global
- [ ] compétitions
- [ ] profils publics
- [ ] système social
- [ ] administration
- [ ] analytics
- [ ] notifications

---

# 👨‍💻 Auteur

**Elfried YOBOUET**

Projet personnel d'apprentissage et de développement autour de :

- Python ;
- développement web ;
- architecture logicielle ;
- API REST ;
- cybersécurité ;
- déploiement cloud.
