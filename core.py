"""
============================================================
PIKO WEB — CORE ENGINE
============================================================

Cœur métier de PIKO.

Ce module contient uniquement la logique du jeu :
    - Pierre / Papier / Ciseaux
    - choix aléatoire de PIKO
    - statistiques
    - séries de victoires
    - historique
    - classement
    - défi du jour
    - matchs Meilleur de 5
    - état initial d'un joueur

IMPORTANT :
Ce fichier ne dépend ni de Flask, ni de Telegram,
ni du navigateur, ni du HTML, ni du JavaScript.

Architecture :

    Interface Web
          ↓
        app.py
          ↓
       core.py
          ↓
    règles du jeu
          ↓
       résultat
          ↓
        app.py
          ↓
     JSON → navigateur
============================================================
"""

import random
from datetime import date
from typing import Optional


# ============================================================
# 1. CONSTANTES DU JEU
# ============================================================

# Les trois choix officiellement disponibles.
CHOIX_JEU = (
    "pierre",
    "papier",
    "ciseaux",
)


# Résultats possibles d'une manche.
RESULTATS = (
    "victoire",
    "defaite",
    "egalite",
)


# Nombre maximum de parties conservées dans l'historique.
HISTORIQUE_MAX = 10


# ============================================================
# 2. RÈGLES DE PIERRE-PAPIER-CISEAUX
# ============================================================

# Chaque tuple représente une combinaison gagnante :
#
#   pierre  bat ciseaux
#   papier  bat pierre
#   ciseaux bat papier
#
COMBINAISONS_GAGNANTES = {
    ("pierre", "ciseaux"),
    ("papier", "pierre"),
    ("ciseaux", "papier"),
}


def valider_choix(choix: str) -> None:
    """
    Vérifie qu'un choix appartient aux choix autorisés.

    Paramètres
    ----------
    choix : str
        Choix à vérifier.

    Raises
    ------
    ValueError
        Si le choix n'est pas valide.
    """

    if choix not in CHOIX_JEU:
        raise ValueError(
            "Le choix doit être pierre, papier ou ciseaux."
        )


def determiner_resultat(
    choix_joueur: str,
    choix_ordinateur: str,
) -> str:
    """
    Compare le choix du joueur avec celui de PIKO.

    Retourne
    --------
    str
        "victoire"
        "defaite"
        "egalite"

    Exemple
    -------
    >>> determiner_resultat("pierre", "ciseaux")
    'victoire'
    """

    # Validation des deux choix.
    valider_choix(choix_joueur)
    valider_choix(choix_ordinateur)

    # Même choix = égalité.
    if choix_joueur == choix_ordinateur:
        return "egalite"

    # Vérification d'une combinaison gagnante.
    if (
        choix_joueur,
        choix_ordinateur,
    ) in COMBINAISONS_GAGNANTES:
        return "victoire"

    # Si ce n'est ni une victoire ni une égalité,
    # le joueur a forcément perdu.
    return "defaite"


# ============================================================
# 3. CHOIX ALÉATOIRE DE PIKO
# ============================================================

def choisir_coup_ordinateur() -> str:
    """
    Demande à PIKO de choisir aléatoirement
    Pierre, Papier ou Ciseaux.

    random.choice() sélectionne un élément
    aléatoire dans CHOIX_JEU.

    Retourne
    --------
    str
        Le choix de PIKO.
    """

    return random.choice(CHOIX_JEU)


# ============================================================
# 4. STATISTIQUES
# ============================================================

def creer_statistiques_initiales() -> dict:
    """
    Crée les statistiques initiales d'un joueur.

    Retourne
    --------
    dict
        Dictionnaire contenant tous les compteurs
        nécessaires au jeu.
    """

    return {
        "victoires": 0,
        "defaites": 0,
        "egalites": 0,
        "serie_actuelle": 0,
        "meilleure_serie": 0,
    }


def mettre_a_jour_statistiques(
    statistiques: dict,
    resultat: str,
) -> dict:
    """
    Met à jour les statistiques après une manche.

    Règles
    ------
    Victoire :
        +1 victoire
        +1 série actuelle

    Défaite :
        +1 défaite
        série remise à 0

    Égalité :
        +1 égalité
        série conservée

    Retourne
    --------
    dict
        Les statistiques mises à jour.
    """

    if resultat not in RESULTATS:
        raise ValueError(
            "Le résultat fourni est invalide."
        )

    # --------------------------------------------------------
    # VICTOIRE
    # --------------------------------------------------------

    if resultat == "victoire":

        statistiques["victoires"] += 1

        statistiques["serie_actuelle"] += 1

        # Mise à jour du record.
        if (
            statistiques["serie_actuelle"]
            > statistiques["meilleure_serie"]
        ):
            statistiques["meilleure_serie"] = (
                statistiques["serie_actuelle"]
            )

    # --------------------------------------------------------
    # DÉFAITE
    # --------------------------------------------------------

    elif resultat == "defaite":

        statistiques["defaites"] += 1

        statistiques["serie_actuelle"] = 0

    # --------------------------------------------------------
    # ÉGALITÉ
    # --------------------------------------------------------

    else:

        statistiques["egalites"] += 1

    return statistiques


def calculer_total_parties(
    statistiques: dict,
) -> int:
    """
    Calcule le nombre total de parties jouées.
    """

    return (
        statistiques["victoires"]
        + statistiques["defaites"]
        + statistiques["egalites"]
    )


def calculer_taux_victoire(
    statistiques: dict,
) -> float:
    """
    Calcule le pourcentage de victoires.

    Retourne 0.0 lorsqu'aucune partie n'a encore
    été jouée.

    Exemple :
        3 victoires / 5 parties = 60.0
    """

    total = calculer_total_parties(
        statistiques
    )

    if total == 0:
        return 0.0

    return round(
        (
            statistiques["victoires"]
            / total
        ) * 100,
        1,
    )


# ============================================================
# 5. HISTORIQUE
# ============================================================

def enregistrer_partie(
    historique: list,
    choix_joueur: str,
    choix_ordinateur: str,
    resultat: str,
) -> list:
    """
    Ajoute une partie à l'historique.

    L'historique conserve uniquement les
    HISTORIQUE_MAX dernières parties.
    """

    # Validation.
    valider_choix(choix_joueur)
    valider_choix(choix_ordinateur)

    if resultat not in RESULTATS:
        raise ValueError(
            "Le résultat fourni est invalide."
        )

    # Création de l'entrée historique.
    partie = {
        "joueur": choix_joueur,
        "ordinateur": choix_ordinateur,
        "resultat": resultat,
    }

    historique.append(partie)

    # Limitation de l'historique.
    if len(historique) > HISTORIQUE_MAX:
        historique.pop(0)

    return historique


# ============================================================
# 6. RANG DU JOUEUR
# ============================================================

def obtenir_rang(victoires: int) -> str:
    """
    Détermine le rang selon le nombre de victoires.

    Rangs
    -----
    0–2   : Débutant
    3–4   : Joueur confirmé
    5–9   : Vétéran
    10–19 : Expert
    20+   : Légende
    """

    if victoires < 0:
        raise ValueError(
            "Le nombre de victoires ne peut pas être négatif."
        )

    if victoires >= 20:
        return "Légende"

    if victoires >= 10:
        return "Expert"

    if victoires >= 5:
        return "Vétéran"

    if victoires >= 3:
        return "Joueur confirmé"

    return "Débutant"


# ============================================================
# 7. DÉFI DU JOUR
# ============================================================

def obtenir_defi_du_jour(
    identifiant_joueur,
) -> str:
    """
    Génère le choix du défi du jour.

    Le résultat dépend de :
        - la date actuelle ;
        - l'identifiant du joueur.

    Le même joueur obtient donc le même défi
    pendant toute la journée.

    Un générateur random.Random indépendant est utilisé
    afin de ne pas perturber le hasard des parties normales.
    """

    graine = (
        f"{date.today().isoformat()}"
        f"-{identifiant_joueur}"
    )

    generateur = random.Random(graine)

    return generateur.choice(
        CHOIX_JEU
    )


# ============================================================
# 8. PARTIE COMPLÈTE
# ============================================================

def jouer_une_manche(
    choix_joueur: str,
    statistiques: Optional[dict] = None,
    historique: Optional[list] = None,
) -> dict:
    """
    Joue une manche complète de PIKO.

    Étapes
    ------
    1. Validation du choix du joueur.
    2. Création des statistiques si nécessaire.
    3. Création de l'historique si nécessaire.
    4. Choix aléatoire de PIKO.
    5. Détermination du résultat.
    6. Mise à jour des statistiques.
    7. Enregistrement de la partie.
    8. Retour des données.

    Retourne
    --------
    dict
        Données complètes nécessaires à l'interface.
    """

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    valider_choix(
        choix_joueur
    )

    # --------------------------------------------------------
    # Initialisation
    # --------------------------------------------------------

    if statistiques is None:
        statistiques = (
            creer_statistiques_initiales()
        )

    if historique is None:
        historique = []

    # --------------------------------------------------------
    # Choix de PIKO
    # --------------------------------------------------------

    choix_ordinateur = (
        choisir_coup_ordinateur()
    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    resultat = determiner_resultat(
        choix_joueur,
        choix_ordinateur,
    )

    # --------------------------------------------------------
    # Statistiques
    # --------------------------------------------------------

    mettre_a_jour_statistiques(
        statistiques,
        resultat,
    )

    # --------------------------------------------------------
    # Historique
    # --------------------------------------------------------

    enregistrer_partie(
        historique,
        choix_joueur,
        choix_ordinateur,
        resultat,
    )

    # --------------------------------------------------------
    # Calculs complémentaires
    # --------------------------------------------------------

    total_parties = (
        calculer_total_parties(
            statistiques
        )
    )

    taux_victoire = (
        calculer_taux_victoire(
            statistiques
        )
    )

    rang = obtenir_rang(
        statistiques["victoires"]
    )

    # --------------------------------------------------------
    # Résultat final
    # --------------------------------------------------------

    return {
        "joueur": choix_joueur,
        "ordinateur": choix_ordinateur,
        "resultat": resultat,

        "statistiques": statistiques,

        "historique": historique,

        "total_parties": total_parties,

        "taux_victoire": taux_victoire,

        "rang": rang,
    }


# ============================================================
# 9. MATCH MEILLEUR DE 5
# ============================================================

def creer_match_bo5() -> dict:
    """
    Crée un nouveau match Meilleur de 5.

    Le premier joueur à atteindre 3 victoires
    remporte le match.
    """

    return {
        "joueur": 0,
        "ordinateur": 0,
        "manches": 0,
        "termine": False,
        "vainqueur": None,
    }


def jouer_manche_bo5(
    match: dict,
    choix_joueur: str,
) -> dict:
    """
    Joue une manche d'un match Meilleur de 5.

    Le score du match est conservé dans le dictionnaire
    fourni en paramètre.

    Le match se termine lorsqu'un joueur atteint 3 victoires.
    """

    # --------------------------------------------------------
    # Vérification du statut du match
    # --------------------------------------------------------

    if match.get("termine"):
        raise ValueError(
            "Ce match est déjà terminé."
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    valider_choix(
        choix_joueur
    )

    # --------------------------------------------------------
    # Choix de PIKO
    # --------------------------------------------------------

    choix_ordinateur = (
        choisir_coup_ordinateur()
    )

    # --------------------------------------------------------
    # Résultat de la manche
    # --------------------------------------------------------

    resultat = determiner_resultat(
        choix_joueur,
        choix_ordinateur,
    )

    # Une manche est jouée.
    match["manches"] += 1

    # --------------------------------------------------------
    # Mise à jour du score
    # --------------------------------------------------------

    if resultat == "victoire":

        match["joueur"] += 1

    elif resultat == "defaite":

        match["ordinateur"] += 1

    # --------------------------------------------------------
    # Vérification de la victoire du match
    # --------------------------------------------------------

    if match["joueur"] >= 3:

        match["termine"] = True

        match["vainqueur"] = "joueur"

    elif match["ordinateur"] >= 3:

        match["termine"] = True

        match["vainqueur"] = "ordinateur"

    # --------------------------------------------------------
    # Retour
    # --------------------------------------------------------

    return {
        "joueur": choix_joueur,

        "ordinateur": choix_ordinateur,

        "resultat": resultat,

        "score_joueur": match["joueur"],

        "score_ordinateur": match["ordinateur"],

        "manches": match["manches"],

        "termine": match["termine"],

        "vainqueur": match["vainqueur"],
    }


# ============================================================
# 10. RÉINITIALISATION
# ============================================================

def reinitialiser_donnees_joueur() -> dict:
    """
    Crée un nouvel état propre pour un joueur.

    Cette fonction ne touche pas à une base de données.

    Elle fournit simplement les données initiales
    nécessaires à une nouvelle session.
    """

    return {
        "statistiques":
            creer_statistiques_initiales(),

        "historique": [],
    }


# ============================================================
# 11. INFORMATIONS COMPLÈTES DU JOUEUR
# ============================================================

def obtenir_resume_joueur(
    statistiques: dict,
) -> dict:
    """
    Construit un résumé complet des performances
    d'un joueur.

    Cette fonction est particulièrement utile
    pour app.py afin de construire la réponse JSON.
    """

    total_parties = (
        calculer_total_parties(
            statistiques
        )
    )

    taux_victoire = (
        calculer_taux_victoire(
            statistiques
        )
    )

    victoires = statistiques[
        "victoires"
    ]

    rang = obtenir_rang(
        victoires
    )

    return {
        "victoires": victoires,

        "defaites":
            statistiques["defaites"],

        "egalites":
            statistiques["egalites"],

        "serie_actuelle":
            statistiques["serie_actuelle"],

        "meilleure_serie":
            statistiques["meilleure_serie"],

        "total_parties":
            total_parties,

        "taux_victoire":
            taux_victoire,

        "rang":
            rang,
    }


# ============================================================
# 12. API MÉTIER PRINCIPALE
# ============================================================

def jouer(
    choix_joueur: str,
    statistiques: Optional[dict] = None,
    historique: Optional[list] = None,
) -> dict:
    """
    Point d'entrée principal du moteur PIKO.

    app.py peut appeler directement :

        jouer("pierre")

    ou :

        jouer(
            "pierre",
            statistiques,
            historique
        )

    Cette fonction permet de garder une API métier
    simple et stable pour les différentes interfaces
    de PIKO.
    """

    return jouer_une_manche(
        choix_joueur=choix_joueur,
        statistiques=statistiques,
        historique=historique,
    )


# ============================================================
# 13. TEST MANUEL DU MODULE
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("PIKO — TEST DU CORE")
    print("=" * 50)

    statistiques = (
        creer_statistiques_initiales()
    )

    historique = []

    # Simulation de quelques parties.
    for choix in (
        "pierre",
        "papier",
        "ciseaux",
    ):

        resultat = jouer(
            choix,
            statistiques,
            historique,
        )

        print()
        print(
            "Joueur :",
            resultat["joueur"],
        )

        print(
            "PIKO   :",
            resultat["ordinateur"],
        )

        print(
            "Résultat :",
            resultat["resultat"],
        )

    print()
    print("=" * 50)
    print("RÉSUMÉ")
    print("=" * 50)

    print(
        obtenir_resume_joueur(
            statistiques
        )
    )

    print()
    print("Historique :")

    for partie in historique:
        print(partie)