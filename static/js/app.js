/*
========================================================
PIKO WEB — GAME CONTROLLER
========================================================

Rôle :
- gérer les interactions de l'interface ;
- communiquer avec Flask ;
- appeler les routes API ;
- afficher les résultats ;
- mettre à jour les statistiques ;
- gérer l'historique ;
- gérer les animations ;
- gérer la musique et les effets sonores.

Architecture :

    Interface Web
         ↓
      app.js
         ↓
       Flask
         ↓
      core.py
         ↓
      résultat
         ↓
      app.js
         ↓
    Interface Web
========================================================
*/


// ========================================================
// 1. CONFIGURATION AUDIO
// ========================================================

// Les fichiers correspondent à l'arborescence :
//
// static/
// └── assets/
//     ├── bg-music.mp3
//     ├── win.mp3
//     ├── lose.mp3
//     ├── click.mp3
//     └── draw.mp3

const AUDIO_PATH = "/static/assets/";


// --------------------------------------------------------
// Musique de fond
// --------------------------------------------------------

const backgroundMusic = new Audio(
    `${AUDIO_PATH}bg-music.mp3`
);

backgroundMusic.loop = true;
backgroundMusic.volume = 0.22;


// --------------------------------------------------------
// Effets sonores
// --------------------------------------------------------

const clickSound = new Audio(
    `${AUDIO_PATH}click.mp3`
);

const winSound = new Audio(
    `${AUDIO_PATH}win.mp3`
);

const loseSound = new Audio(
    `${AUDIO_PATH}lose.mp3`
);

const drawSound = new Audio(
    `${AUDIO_PATH}draw.mp3`
);


// Volume des effets sonores.

clickSound.volume = 0.45;
winSound.volume = 0.60;
loseSound.volume = 0.55;
drawSound.volume = 0.50;


// ========================================================
// 2. RÉFÉRENCES AUX ÉLÉMENTS HTML
// ========================================================

const choiceButtons = document.querySelectorAll(
    ".choice-card"
);

const playerChoiceDisplay =
    document.querySelector(
        "#player-choice-display"
    );

const computerChoiceDisplay =
    document.querySelector(
        "#computer-choice-display"
    );

const gameStatus =
    document.querySelector(
        "#game-status"
    );

const resultCard =
    document.querySelector(
        "#result-card"
    );

const resultIcon =
    document.querySelector(
        "#result-icon"
    );

const resultTitle =
    document.querySelector(
        "#result-title"
    );

const resultMessage =
    document.querySelector(
        "#result-message"
    );

const resultXp =
    document.querySelector(
        "#result-xp"
    );

const playAgainButton =
    document.querySelector(
        "#play-again-button"
    );

const statGames =
    document.querySelector(
        "#stat-games"
    );

const statWins =
    document.querySelector(
        "#stat-wins"
    );

const statLosses =
    document.querySelector(
        "#stat-losses"
    );

const statDraws =
    document.querySelector(
        "#stat-draws"
    );

const currentStreak =
    document.querySelector(
        "#current-streak"
    );

const playerRank =
    document.querySelector(
        "#player-rank"
    );

const playerXp =
    document.querySelector(
        "#player-xp"
    );

const historyList =
    document.querySelector(
        "#history-list"
    );

const clearHistoryButton =
    document.querySelector(
        "#clear-history-button"
    );


// ========================================================
// 3. DONNÉES FIXES DU JEU
// ========================================================

const choiceEmojis = {
    pierre: "✊",
    papier: "📄",
    ciseaux: "✂️"
};

const choiceLabels = {
    pierre: "Pierre",
    papier: "Papier",
    ciseaux: "Ciseaux"
};


// ========================================================
// 4. ÉTAT DE L'APPLICATION
// ========================================================

// Empêche plusieurs parties simultanées.

let isPlaying = false;


// Dernier résultat reçu du serveur.

let lastGameResult = null;


// Historique affiché dans le navigateur.

let localHistory = [];


// État de la musique.

let musicEnabled = true;


// Clé localStorage.

const MUSIC_STORAGE_KEY =
    "piko_music_enabled";


// ========================================================
// 5. UTILITAIRES
// ========================================================

function wait(milliseconds) {
    return new Promise(
        (resolve) => {
            setTimeout(
                resolve,
                milliseconds
            );
        }
    );
}


// ========================================================
// 6. GESTION DE LA MUSIQUE
// ========================================================

function loadMusicPreference() {

    const savedPreference =
        localStorage.getItem(
            MUSIC_STORAGE_KEY
        );

    if (savedPreference === null) {
        musicEnabled = true;
        return;
    }

    musicEnabled =
        savedPreference === "true";
}


function saveMusicPreference() {

    localStorage.setItem(
        MUSIC_STORAGE_KEY,
        String(musicEnabled)
    );
}


function updateMusicButton() {

    const button =
        document.querySelector(
            "#music-toggle"
        );

    if (!button) {
        return;
    }

    button.textContent =
        musicEnabled ? "🔊" : "🔇";

    button.setAttribute(
        "aria-pressed",
        String(musicEnabled)
    );

    button.setAttribute(
        "aria-label",
        musicEnabled
            ? "Désactiver la musique"
            : "Activer la musique"
    );

    button.setAttribute(
        "title",
        musicEnabled
            ? "Désactiver la musique"
            : "Activer la musique"
    );
}


function updateMusicState() {

    if (!musicEnabled) {

        backgroundMusic.pause();

        return;
    }

    backgroundMusic
        .play()
        .catch(() => {
            // Autoplay refusé par le navigateur.
        });
}


function createAudioControl() {

    const topbar =
        document.querySelector(
            ".topbar"
        );

    if (!topbar) {
        return;
    }

    if (
        document.querySelector(
            "#music-toggle"
        )
    ) {
        updateMusicButton();
        return;
    }

    const button =
        document.createElement(
            "button"
        );

    button.type = "button";

    button.id =
        "music-toggle";

    button.className =
        "music-toggle";

    button.addEventListener(
        "click",
        () => {

            musicEnabled =
                !musicEnabled;

            saveMusicPreference();

            updateMusicButton();

            updateMusicState();
        }
    );

    topbar.appendChild(
        button
    );

    updateMusicButton();
}


// ========================================================
// 7. EFFETS SONORES
// ========================================================

function playSound(audio) {

    if (!audio) {
        return;
    }

    audio.currentTime = 0;

    audio
        .play()
        .catch(() => {
            // Le navigateur peut bloquer l'audio.
        });
}


// ========================================================
// 8. COMPTE À REBOURS
// ========================================================

async function countdown() {

    const overlay =
        document.createElement(
            "div"
        );

    overlay.className =
        "countdown-overlay";

    const number =
        document.createElement(
            "div"
        );

    number.className =
        "countdown-number";

    overlay.appendChild(
        number
    );

    document.body.appendChild(
        overlay
    );

    const steps = [
        "3",
        "2",
        "1",
        "GO!"
    ];

    for (const step of steps) {

        number.textContent =
            step;

        number.style.animation =
            "none";

        void number.offsetWidth;

        number.style.animation =
            "countdown-pop 700ms cubic-bezier(0.22, 1, 0.36, 1)";

        if (step !== "GO!") {

            playSound(
                clickSound
            );
        }

        await wait(
            step === "GO!"
                ? 450
                : 700
        );
    }

    overlay.remove();
}


// ========================================================
// 9. RESET VISUEL DE L'ARÈNE
// ========================================================

function resetBattleArena() {

    if (playerChoiceDisplay) {

        playerChoiceDisplay.textContent =
            "?";

        playerChoiceDisplay.classList.remove(
            "is-revealing"
        );
    }

    if (computerChoiceDisplay) {

        computerChoiceDisplay.textContent =
            "?";

        computerChoiceDisplay.classList.remove(
            "is-revealing"
        );
    }

    if (resultCard) {

        resultCard.hidden =
            true;

        resultCard.classList.remove(
            "result-win",
            "result-loss",
            "result-draw"
        );
    }

    if (playAgainButton) {

        playAgainButton.hidden =
            true;
    }

    choiceButtons.forEach(
        (button) => {

            button.classList.remove(
                "selected"
            );

            button.disabled =
                false;
        }
    );
}


// ========================================================
// 10. AFFICHAGE DU CHOIX DU JOUEUR
// ========================================================

function showPlayerChoice(choice) {

    if (!playerChoiceDisplay) {
        return;
    }

    playerChoiceDisplay.textContent =
        choiceEmojis[choice] || "?";

    playerChoiceDisplay.classList.remove(
        "is-revealing"
    );

    void playerChoiceDisplay.offsetWidth;

    playerChoiceDisplay.classList.add(
        "is-revealing"
    );
}


// ========================================================
// 11. AFFICHAGE DU CHOIX DE PIKO
// ========================================================

function showComputerChoice(choice) {

    if (!computerChoiceDisplay) {
        return;
    }

    computerChoiceDisplay.textContent =
        choiceEmojis[choice] || "?";

    computerChoiceDisplay.classList.remove(
        "is-revealing"
    );

    void computerChoiceDisplay.offsetWidth;

    computerChoiceDisplay.classList.add(
        "is-revealing"
    );
}


// ========================================================
// 12. MESSAGE D'ÉTAT
// ========================================================

function setGameStatus(
    message,
    type = ""
) {

    if (!gameStatus) {
        return;
    }

    gameStatus.textContent =
        message;

    gameStatus.classList.remove(
        "is-loading",
        "is-success",
        "is-error"
    );

    if (type) {

        gameStatus.classList.add(
            type
        );
    }
}


// ========================================================
// 13. STATISTIQUES
// ========================================================

function calculateTotalGames(stats) {

    if (!stats) {
        return 0;
    }

    return (
        Number(stats.victoires || 0) +
        Number(stats.defaites || 0) +
        Number(stats.egalites || 0)
    );
}


function updateStatistics(stats, rank = null) {

    if (!stats) {
        return;
    }

    if (statGames) {

        statGames.textContent =
            calculateTotalGames(
                stats
            );
    }

    if (statWins) {

        statWins.textContent =
            stats.victoires || 0;
    }

    if (statLosses) {

        statLosses.textContent =
            stats.defaites || 0;
    }

    if (statDraws) {

        statDraws.textContent =
            stats.egalites || 0;
    }

    if (currentStreak) {

        currentStreak.textContent =
            stats.serie_actuelle || 0;
    }

    /*
    IMPORTANT :

    L'XP et le rang doivent venir du serveur.

    app.js ne recalcule plus ces valeurs.
    Cela évite d'avoir une logique différente
    entre le frontend et core.py.
    */

    if (
        stats.xp !== undefined &&
        playerXp
    ) {

        playerXp.textContent =
            stats.xp;
    }

    if (rank) {

        displayRank(rank);
    }
}


// ========================================================
// 14. AFFICHAGE DU RANG
// ========================================================

function displayRank(rank) {

    if (!playerRank || !rank) {
        return;
    }

    const rankMap = {

        "Débutant":
            "🌱 DÉBUTANT",

        "Joueur confirmé":
            "⭐ CONFIRMÉ",

        "Vétéran":
            "🔥 VÉTÉRAN",

        "Expert":
            "💎 EXPERT",

        "Légende":
            "👑 LÉGENDE"
    };

    playerRank.textContent =
        rankMap[rank] || rank;
}


// ========================================================
// 15. HISTORIQUE
// ========================================================

function addToHistory(historique) {

    if (!Array.isArray(historique)) {
        return;
    }

    localHistory = [
        ...historique
    ];

    renderHistory();
}


function renderHistory() {

    if (!historyList) {
        return;
    }

    if (
        localHistory.length === 0
    ) {

        historyList.innerHTML = `
            <div class="empty-history">
                <span class="empty-history-icon">
                    🎮
                </span>

                <p>
                    Tes parties apparaîtront ici.
                </p>
            </div>
        `;

        return;
    }

    historyList.innerHTML = "";

    [
        ...localHistory
    ]
        .reverse()
        .forEach(
            (game) => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "history-item";

                let resultEmoji =
                    "🤝";

                if (
                    game.resultat ===
                    "victoire"
                ) {

                    resultEmoji =
                        "🏆";
                }

                if (
                    game.resultat ===
                    "defaite"
                ) {

                    resultEmoji =
                        "💥";
                }

                const playerChoice =
                    game.joueur;

                const computerChoice =
                    game.ordinateur;

                const playerLabel =
                    choiceLabels[
                        playerChoice
                    ] || playerChoice;

                const computerLabel =
                    choiceLabels[
                        computerChoice
                    ] || computerChoice;

                const playerEmoji =
                    choiceEmojis[
                        playerChoice
                    ] || "";

                const computerEmoji =
                    choiceEmojis[
                        computerChoice
                    ] || "";

                item.innerHTML = `
                    <div class="history-result">
                        ${resultEmoji}
                    </div>

                    <div class="history-match">
                        <strong>
                            ${playerEmoji}
                            ${playerLabel}
                        </strong>

                        <span>VS</span>

                        <strong>
                            ${computerEmoji}
                            ${computerLabel}
                        </strong>
                    </div>

                    <span class="history-result-text">
                        ${game.resultat}
                    </span>
                `;

                historyList.appendChild(
                    item
                );
            }
        );
}


// ========================================================
// 16. AFFICHAGE DU RÉSULTAT
// ========================================================

function showResult(data) {

    if (!data || !resultCard) {
        return;
    }

    const result =
        data.resultat;

    let icon =
        "🤝";

    let title =
        "Égalité !";

    let message =
        "Même choix. Personne ne prend l'avantage.";

    let xp =
        "XP non spécifiée";

    let resultClass =
        "result-draw";


    // ----------------------------------------------------
    // Victoire
    // ----------------------------------------------------

    if (
        result === "victoire"
    ) {

        icon =
            "🏆";

        title =
            "Victoire !";

        message =
            "Bien joué ! Tu viens de battre PIKO.";

        resultClass =
            "result-win";

        playSound(
            winSound
        );
    }


    // ----------------------------------------------------
    // Défaite
    // ----------------------------------------------------

    else if (
        result === "defaite"
    ) {

        icon =
            "💥";

        title =
            "PIKO gagne !";

        message =
            "Cette manche est pour PIKO. Revanche ?";

        resultClass =
            "result-loss";

        playSound(
            loseSound
        );
    }


    // ----------------------------------------------------
    // Égalité
    // ----------------------------------------------------

    else {

        playSound(
            drawSound
        );
    }


    // ----------------------------------------------------
    // XP
    // ----------------------------------------------------

    /*
    On utilise l'XP renvoyée par Flask/core.py
    si elle existe.

    Plusieurs formats sont acceptés afin de rester
    compatible avec l'évolution de core.py.
    */

    if (
        data.xp_earned !== undefined
    ) {

        xp =
            `+${data.xp_earned} XP`;

    } else if (
        data.xp_gagnee !== undefined
    ) {

        xp =
            `+${data.xp_gagnee} XP`;
    }


    // ----------------------------------------------------
    // Mise à jour du résultat
    // ----------------------------------------------------

    if (resultIcon) {

        resultIcon.textContent =
            icon;
    }

    if (resultTitle) {

        resultTitle.textContent =
            title;
    }

    if (resultMessage) {

        resultMessage.textContent =
            message;
    }

    if (resultXp) {

        resultXp.textContent =
            xp;
    }


    // ----------------------------------------------------
    // Classes CSS
    // ----------------------------------------------------

    resultCard.classList.remove(
        "result-win",
        "result-loss",
        "result-draw"
    );

    resultCard.classList.add(
        resultClass
    );

    resultCard.hidden =
        false;


    if (playAgainButton) {

        playAgainButton.hidden =
            false;
    }


    // ----------------------------------------------------
    // Message d'état
    // ----------------------------------------------------

    if (
        result === "victoire"
    ) {

        setGameStatus(
            "🏆 Magnifique ! Continue ta série.",
            "is-success"
        );

    } else if (
        result === "defaite"
    ) {

        setGameStatus(
            "💥 PIKO prend cette manche.",
            "is-error"
        );

    } else {

        setGameStatus(
            "🤝 Égalité. Nouvelle manche ?"
        );
    }
}


// ========================================================
// 17. JOUER UNE PARTIE
// ========================================================

async function playGame(choice) {

    if (isPlaying) {
        return;
    }

    isPlaying = true;

    // Le clic utilisateur permet généralement
    // au navigateur d'autoriser l'audio.

    updateMusicState();

    resetBattleArena();


    // Sélection visuelle.

    choiceButtons.forEach(
        (button) => {

            const isSelected =
                button.dataset.choice === choice;

            button.classList.toggle(
                "selected",
                isSelected
            );

            button.disabled =
                true;
        }
    );


    // Son du clic.

    playSound(
        clickSound
    );


    setGameStatus(
        "PIKO prépare son coup...",
        "is-loading"
    );


    try {

        // ------------------------------------------------
        // Appel Flask
        // ------------------------------------------------

        const response =
            await fetch(
                "/play",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        choix: choice
                    })
                }
            );


        let payload =
            null;


        try {

            payload =
                await response.json();

        } catch {

            payload =
                null;
        }


        if (!response.ok) {

            throw new Error(
                payload?.error ||
                "Impossible de jouer la partie."
            );
        }


        if (
            !payload ||
            !payload.success ||
            !payload.data
        ) {

            throw new Error(
                payload?.error ||
                "Réponse invalide du serveur."
            );
        }


        const data =
            payload.data;


        lastGameResult =
            data;


        // ------------------------------------------------
        // Affichage du choix du joueur
        // ------------------------------------------------

        showPlayerChoice(
            data.joueur
        );


        // ------------------------------------------------
        // Compte à rebours
        // ------------------------------------------------

        await countdown();


        // ------------------------------------------------
        // Révélation de PIKO
        // ------------------------------------------------

        showComputerChoice(
            data.ordinateur
        );


        await wait(
            500
        );


        // ------------------------------------------------
        // Mise à jour statistiques
        // ------------------------------------------------

        updateStatistics(
            data.statistiques,
            data.rang
        );


        // ------------------------------------------------
        // Historique
        // ------------------------------------------------

        addToHistory(
            data.historique
        );


        // ------------------------------------------------
        // Résultat
        // ------------------------------------------------

        showResult(
            data
        );


    } catch (error) {

        console.error(
            "Erreur PIKO :",
            error
        );


        setGameStatus(
            error.message ||
            "Une erreur est survenue.",
            "is-error"
        );


        if (computerChoiceDisplay) {

            computerChoiceDisplay.textContent =
                "?";
        }

    } finally {

        isPlaying =
            false;

        choiceButtons.forEach(
            (button) => {

                button.disabled =
                    false;
            }
        );
    }
}


// ========================================================
// 18. CHARGER L'ÉTAT DU JOUEUR
// ========================================================

async function loadPlayerState() {

    try {

        const response =
            await fetch(
                "/api/state"
            );


        let payload =
            null;


        try {

            payload =
                await response.json();

        } catch {

            payload =
                null;
        }


        if (
            !response.ok ||
            !payload ||
            !payload.success
        ) {

            throw new Error(
                payload?.error ||
                "Impossible de charger l'état du joueur."
            );
        }


        const data =
            payload.data;


        // Statistiques.

        updateStatistics(
            data.statistiques,
            data.rang
        );


        // Historique.

        addToHistory(
            data.historique
        );


    } catch (error) {

        console.error(
            "Impossible de charger l'état de PIKO :",
            error
        );

        setGameStatus(
            "Impossible de charger tes données.",
            "is-error"
        );
    }
}


// ========================================================
// 19. RÉINITIALISATION
// ========================================================

async function resetGameData() {

    const confirmation =
        window.confirm(
            "Réinitialiser toutes tes statistiques et ton historique ?"
        );


    if (!confirmation) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/reset",
                {
                    method: "POST"
                }
            );


        let payload =
            null;


        try {

            payload =
                await response.json();

        } catch {

            payload =
                null;
        }


        if (
            !response.ok ||
            !payload ||
            !payload.success
        ) {

            throw new Error(
                payload?.error ||
                "Impossible de réinitialiser."
            );
        }


        const data =
            payload.data;


        // Mise à zéro.

        updateStatistics(
            data.statistiques,
            data.rang
        );


        addToHistory(
            data.historique
        );


        resetBattleArena();


        setGameStatus(
            "♻️ Tes données ont été réinitialisées."
        );


    } catch (error) {

        console.error(
            "Erreur réinitialisation :",
            error
        );


        setGameStatus(
            error.message ||
            "Une erreur est survenue.",
            "is-error"
        );
    }
}


// ========================================================
// 20. ÉVÉNEMENTS DES BOUTONS
// ========================================================

choiceButtons.forEach(
    (button) => {

        button.addEventListener(
            "click",
            () => {

                const choice =
                    button.dataset.choice;


                if (!choice) {
                    return;
                }


                playGame(
                    choice
                );
            }
        );
    }
);


// ========================================================
// 21. BOUTON REJOUER
// ========================================================

if (playAgainButton) {

    playAgainButton.addEventListener(
        "click",
        () => {

            resetBattleArena();

            setGameStatus(
                "Choisis ton coup pour continuer."
            );

            document
                .querySelector(
                    ".choices-grid"
                )
                ?.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
        }
    );
}


// ========================================================
// 22. BOUTON EFFACER
// ========================================================

if (clearHistoryButton) {

    clearHistoryButton.addEventListener(
        "click",
        resetGameData
    );
}


// ========================================================
// 23. INITIALISATION
// ========================================================

async function initialiseGame() {

    loadMusicPreference();

    resetBattleArena();

    setGameStatus(
        "Choisis ton coup pour commencer."
    );

    createAudioControl();

    renderHistory();

    await loadPlayerState();

    console.log(
        "🎮 PIKO Web est prêt."
    );
}


// ========================================================
// 24. DÉMARRAGE
// ========================================================

document.addEventListener(
    "DOMContentLoaded",
    initialiseGame
);