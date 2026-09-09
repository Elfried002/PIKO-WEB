"""
PIKO WEB - APPLICATION FLASK
============================

Cette application relie :

    Navigateur → Flask → core.py → Navigateur

Le fichier app.py est la couche web de PIKO.

Responsabilités :
- servir l'interface HTML ;
- recevoir les requêtes du navigateur ;
- appeler les fonctions métier de core.py ;
- gérer la session du joueur ;
- retourner les réponses JSON à JavaScript ;
- fournir un endpoint de santé pour Railway.

IMPORTANT :
- Pas de Telegram ici.
- Le cerveau du jeu reste dans core.py.
- La session Flask est provisoire et adaptée au prototype.
- Une future version de production pourra utiliser une base de données.
"""

import os
import secrets

from flask import Flask, jsonify, render_template, request, session

from core import (
    creer_match_bo5,
    creer_statistiques_initiales,
    obtenir_defi_du_jour,
    obtenir_rang,
    jouer_manche_bo5,
    jouer_une_manche,
    reinitialiser_donnees_joueur,
)


# ============================================================
# 1. CRÉATION ET CONFIGURATION DE FLASK
# ============================================================

app = Flask(__name__)


# La clé secrète sert à signer la session Flask.
#
# En développement, si PIKO_SECRET_KEY n'existe pas,
# une clé aléatoire est générée à chaque démarrage.
#
# En production, il faut définir PIKO_SECRET_KEY dans Railway
# afin d'utiliser une clé stable.

app.config["SECRET_KEY"] = os.getenv(
    "PIKO_SECRET_KEY",
    secrets.token_hex(32),
)


# Limite simple de sécurité pour les requêtes HTTP.

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


# ============================================================
# 2. OUTILS DE SESSION
# ============================================================

def obtenir_statistiques_session():
    """
    Récupère les statistiques du joueur dans la session.

    Si elles n'existent pas encore, elles sont créées.
    """

    if "statistiques" not in session:
        session["statistiques"] = creer_statistiques_initiales()

    return session["statistiques"]


def obtenir_historique_session():
    """
    Récupère l'historique du joueur dans la session.

    Si aucun historique n'existe encore,
    une liste vide est créée.
    """

    if "historique" not in session:
        session["historique"] = []

    return session["historique"]


def sauvegarder_etat(statistiques, historique):
    """
    Replace les données modifiées dans la session Flask.

    session.modified indique clairement à Flask que
    les données de session ont changé.
    """

    session["statistiques"] = statistiques
    session["historique"] = historique
    session.modified = True


# ============================================================
# 3. PAGE PRINCIPALE
# ============================================================

@app.route("/", methods=["GET"])
def accueil():
    """
    Affiche l'interface principale de PIKO.
    """

    return render_template("index.html")


# ============================================================
# 4. ÉTAT INITIAL DU JOUEUR
# ============================================================

@app.route("/api/state", methods=["GET"])
def obtenir_etat():
    """
    Retourne l'état actuel du joueur au navigateur.

    Cette route est utilisée au chargement de la page.
    """

    statistiques = obtenir_statistiques_session()
    historique = obtenir_historique_session()

    return jsonify({
        "success": True,
        "data": {
            "statistiques": statistiques,
            "historique": historique,
            "rang": obtenir_rang(statistiques["victoires"]),
        },
    })


# ============================================================
# 5. JOUER UNE PARTIE RAPIDE
# ============================================================

@app.route("/play", methods=["POST"])
def jouer():
    """
    Reçoit le choix du joueur et joue une manche.

    Format attendu :

        {
            "choix": "pierre"
        }

    Le vrai calcul est effectué par core.py.
    """

    donnees = request.get_json(silent=True)

    if not isinstance(donnees, dict):
        return jsonify({
            "success": False,
            "error": "Les données envoyées sont invalides.",
        }), 400

    choix = donnees.get("choix")

    # Vérification du type.

    if not isinstance(choix, str):
        return jsonify({
            "success": False,
            "error": "Le choix doit être une chaîne de caractères.",
        }), 400

    # Normalisation.

    choix = choix.strip().lower()

    if not choix:
        return jsonify({
            "success": False,
            "error": "Le choix du joueur est obligatoire.",
        }), 400

    try:
        statistiques = obtenir_statistiques_session()
        historique = obtenir_historique_session()

        # Le cerveau du jeu reçoit les données existantes.

        resultat = jouer_une_manche(
            choix_joueur=choix,
            statistiques=statistiques,
            historique=historique,
        )

        # Sauvegarde de la nouvelle progression.

        sauvegarder_etat(
            resultat["statistiques"],
            resultat["historique"],
        )

        return jsonify({
            "success": True,
            "data": {
                **resultat,
                "rang": obtenir_rang(
                    resultat["statistiques"]["victoires"]
                ),
            },
        }), 200

    except ValueError as erreur:

        return jsonify({
            "success": False,
            "error": str(erreur),
        }), 400

    except Exception:
        app.logger.exception(
            "Erreur inattendue pendant une partie."
        )

        return jsonify({
            "success": False,
            "error": "Une erreur interne est survenue.",
        }), 500


# ============================================================
# 6. DÉFI DU JOUR
# ============================================================

@app.route("/api/daily-challenge", methods=["GET"])
def defi_du_jour():
    """
    Retourne le défi du jour.

    Comme nous n'avons pas encore de système
    d'authentification, nous utilisons un identifiant
    provisoire stocké dans la session Flask.
    """

    # Création d'un identifiant stable dans la session.

    if "player_id" not in session:
        session["player_id"] = secrets.token_hex(12)
        session.modified = True

    choix = obtenir_defi_du_jour(
        session["player_id"]
    )

    return jsonify({
        "success": True,
        "data": {
            "choix": choix,
        },
    })


# ============================================================
# 7. MEILLEUR DE 5 - CRÉATION
# ============================================================

@app.route("/api/bo5/start", methods=["POST"])
def commencer_bo5():
    """
    Crée un nouveau match Meilleur de 5.
    """

    session["match_bo5"] = creer_match_bo5()
    session.modified = True

    return jsonify({
        "success": True,
        "data": session["match_bo5"],
    })


# ============================================================
# 8. MEILLEUR DE 5 - JOUER UNE MANCHE
# ============================================================

@app.route("/api/bo5/play", methods=["POST"])
def jouer_bo5():
    """
    Joue une manche du match Meilleur de 5.
    """

    donnees = request.get_json(silent=True)

    if not isinstance(donnees, dict):
        return jsonify({
            "success": False,
            "error": "Les données envoyées sont invalides.",
        }), 400

    choix = donnees.get("choix")

    if not isinstance(choix, str):
        return jsonify({
            "success": False,
            "error": "Le choix doit être une chaîne de caractères.",
        }), 400

    choix = choix.strip().lower()

    if not choix:
        return jsonify({
            "success": False,
            "error": "Le choix du joueur est obligatoire.",
        }), 400

    match = session.get("match_bo5")

    if not match:
        return jsonify({
            "success": False,
            "error": "Aucun match Meilleur de 5 n'est en cours.",
        }), 400

    try:
        resultat = jouer_manche_bo5(
            match,
            choix,
        )

        # Sauvegarde de l'état du match.

        session["match_bo5"] = match
        session.modified = True

        return jsonify({
            "success": True,
            "data": resultat,
        }), 200

    except ValueError as erreur:

        return jsonify({
            "success": False,
            "error": str(erreur),
        }), 400

    except Exception:
        app.logger.exception(
            "Erreur inattendue pendant le match BO5."
        )

        return jsonify({
            "success": False,
            "error": "Une erreur interne est survenue.",
        }), 500


# ============================================================
# 9. RÉINITIALISATION
# ============================================================

@app.route("/api/reset", methods=["POST"])
def reinitialiser():
    """
    Réinitialise les données du joueur.
    """

    etat = reinitialiser_donnees_joueur()

    session["statistiques"] = etat["statistiques"]
    session["historique"] = etat["historique"]

    session.pop("match_bo5", None)

    session.modified = True

    return jsonify({
        "success": True,
        "data": etat,
    })


# ============================================================
# 10. HEALTHCHECK
# ============================================================

@app.route("/healthz", methods=["GET"])
def healthz():
    """
    Endpoint simple permettant de vérifier que Flask fonctionne.

    Railway pourra utiliser cette route pour vérifier
    l'état du service.
    """

    return jsonify({
        "status": "ok",
        "service": "piko-web",
    }), 200


# ============================================================
# 11. GESTION DES ERREURS HTTP
# ============================================================

@app.errorhandler(404)
def page_non_trouvee(erreur):
    """
    Route ou ressource inconnue.
    """

    return jsonify({
        "success": False,
        "error": "La ressource demandée n'existe pas.",
    }), 404


@app.errorhandler(405)
def methode_non_autorisee(erreur):
    """
    Méthode HTTP non autorisée.
    """

    return jsonify({
        "success": False,
        "error": "La méthode HTTP utilisée n'est pas autorisée.",
    }), 405


@app.errorhandler(413)
def requete_trop_volumineuse(erreur):
    """
    Requête trop volumineuse.
    """

    return jsonify({
        "success": False,
        "error": "La requête est trop volumineuse.",
    }), 413


@app.errorhandler(500)
def erreur_interne(erreur):
    """
    Erreur interne non gérée.
    """

    app.logger.exception(
        "Erreur interne Flask.",
        exc_info=erreur,
    )

    return jsonify({
        "success": False,
        "error": "Une erreur interne est survenue.",
    }), 500


# ============================================================
# 12. LANCEMENT LOCAL
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv("PORT", "5000")
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )