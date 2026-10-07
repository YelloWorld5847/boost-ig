# 🚀 Instagram Reels Organic Drip-Feed Booster

Simulateur et orchestrateur d'engagement organique réaliste pour les Reels Instagram utilisant l'API v2 de **mysmm.co**.

Ce script reproduit fidèlement la dynamique virale de l'algorithme Instagram grâce à une courbe sigmoïde (S-Curve) avec amorçage précoce et jitter naturel (variations temporelles gaussiennes).

---

## ⚡ Caractéristiques

- **Quadriptyque algorithmique complet** :
  - **Vues Reels** (Service `#1785`, cohortes de 100 vues, $0.00135/1k)
  - **Likes naturels** (Service `#1`, tranches de 10 likes, instantanés, $0.0902/1k)
  - **Partages & Reach** (Service `#1581`, tranches de 10 partages, activable avec `--with-shares`, $0.1040/1k)
  - **Commentaires naturels en français** (Service `#1637`, tranches de 10 coms, activable avec `--with-comments`, $0.6292/1k)
- **Logique algorithmique crédible** : Les commentaires ne sont **JAMAIS** envoyés à T+0h, mais déclenchés au cœur de la phase d'accélération virale une fois que le Reel a déjà accumulé du volume de vues et de likes !
- **Modèle de courbe sigmoïde (S-Curve)** : Amorçage doux $\to$ Accélération virale $\to$ Plateau de rétention.
- **Jitter anti-détection** : Micro-variations de pauses aléatoires pour supprimer tout comportement robotique prévisible.
- **Mode Simulation (sans frais)** : Génère un aperçu console ASCII, un graphique PNG et un dashboard interactif HTML avec calcul précis des coûts au millième de centime.
- **Mode Live (`--live`)** : Envoie les ordres échelonnés dans le temps via l'API, avec vérification du solde et sécurité Ctrl+C.

---

## 🐧 Installation & Mise à jour sur Ubuntu Server

### 1. Cloner ou mettre à jour le dépôt
```bash
# Si premier clone :
git clone https://github.com/YelloWorld5847/boost-ig.git
cd boost-ig
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Si le projet est déjà sur votre serveur, mettez-le simplement à jour :
cd boost-ig
git pull
```

---

## 🔑 Configuration de la clé API (Optionnel)

La clé API par défaut est déjà configurée dans le script. Si vous souhaitez utiliser une variable d'environnement :

```bash
export MYSMM_API_KEY="votre_cle_api_ici"
```

---

## 💬 Personnaliser son propre dictionnaire de commentaires

Vous pouvez définir vos propres phrases personnalisées de deux manières très simples :

### Méthode 1 : Modifier directement `comments.txt` (Automatique)
Le script lit automatiquement le fichier `comments.txt` à la racine s'il existe (1 commentaire par ligne) :
```bash
nano comments.txt
```
Ajoutez ou modifiez vos phrases (avec emojis, argot, etc.). Le script piochera dedans automatiquement dès que `--with-comments` est activé !

### Méthode 2 : Spécifier un fichier personnalisé avec `--comments-file`
```bash
python3 boost_simulator.py --views 2000 --hours 8 --with-comments --comments-file "mes_commentaires.txt" --link "URL"
```

---

### 1. Vérifier son solde
```bash
python3 boost_simulator.py --balance
```

### 2. Mode Simulation (0 risque, aucun débit)
Génère la courbe, les visualisations et le coût sans envoyer d'ordre :
```bash
# 2 000 vues sur 8 heures (Vues + Likes)
python3 boost_simulator.py --views 2000 --hours 8 --link "https://www.instagram.com/reel/XXXXX/"

# Avec commentaires en français activés (déclenchés après la montée des vues)
python3 boost_simulator.py --views 2000 --hours 8 --with-comments --link "https://www.instagram.com/reel/XXXXX/"

# Boost complet (Vues + Likes + Partages + Commentaires)
python3 boost_simulator.py --views 20000 --hours 36 --with-comments --with-shares --link "https://www.instagram.com/reel/XXXXX/"
```

### 3. Mode Live (Exécution en direct)
Exécute les ordres réels avec les pauses calculées :
```bash
python3 boost_simulator.py --views 2000 --hours 8 --with-comments --link "https://www.instagram.com/reel/XXXXX/" --live -y
```

---

## 🛡️ Faire tourner en arrière-plan (24/7 sur serveur)

Pour éviter que le script ne s'arrête lorsque vous fermez votre session SSH :

### Avec `tmux` (Recommandé)
```bash
# 1. Ouvrir une session tmux
tmux new -s boost

# 2. Activer le venv et lancer le boost réel
source venv/bin/activate
python3 boost_simulator.py --views 20000 --hours 36.0 --with-comments --link "https://www.instagram.com/reel/XXXXX/" --live -y

# 3. Détacher la session en toute sécurité :
# Appuyez sur Ctrl + B, puis relâchez et appuyez sur D

# 4. Pour réafficher la console plus tard :
tmux attach -t boost
```

---

## 🛠️ Commandes de test rapide

```bash
# Tester 100 vues immédiates sur un Reel
python3 boost_simulator.py --test-views "https://www.instagram.com/reel/XXXXX/"

# Tester 10 likes immédiats sur un Reel
python3 boost_simulator.py --test-likes "https://www.instagram.com/reel/XXXXX/"

# Tester 10 commentaires français immédiats sur un Reel
python3 boost_simulator.py --test-comments "https://www.instagram.com/reel/XXXXX/"

# Tester 10 partages sur un Reel
python3 boost_simulator.py --test-shares "https://www.instagram.com/reel/XXXXX/"

# Consulter le statut d'une commande
python3 boost_simulator.py --status 49656079
```
