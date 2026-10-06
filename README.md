# 🚀 Instagram Reels Organic Drip-Feed Booster

Simulateur et orchestrateur d'engagement organique réaliste pour les Reels Instagram utilisant l'API v2 de **mysmm.co**.

Ce script reproduit fidèlement la dynamique virale de l'algorithme Instagram grâce à une courbe sigmoïde (S-Curve) avec amorçage précoce et jitter naturel (variations temporelles gaussiennes).

---

## ⚡ Caractéristiques

- **Triade algorithmique** :
  - **Vues Reels** (Service `#1785`, cohortes de 100 vues)
  - **Likes naturels** (Service `#1`, tranches de 10 likes, instantanés)
  - **Partages & Reach** (Service `#1581`, tranches de 10 partages, activable avec `--with-shares`)
- **Modèle de courbe sigmoïde (S-Curve)** : Amorçage doux $\to$ Accélération virale $\to$ Plateau de rétention.
- **Jitter anti-détection** : Micro-variations de pauses aléatoires pour supprimer tout comportement robotique prévisible.
- **Mode Simulation (sans frais)** : Génère un aperçu console ASCII, un graphique PNG et un dashboard interactif HTML avec calcul précis des coûts au millième de centime.
- **Mode Live (`--live`)** : Envoie les ordres échelonnés dans le temps via l'API, avec vérification du solde et sécurité Ctrl+C.

---

## 🐧 Installation rapide sur Ubuntu Server

### 1. Mettre à jour et installer les dépendances système
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git tmux
```

### 2. Cloner le dépôt
```bash
git clone https://github.com/YelloWorld5847/boost-ig.git
cd boost-ig
```

### 3. Créer un environnement virtuel Python et installer les dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔑 Configuration de la clé API (Optionnel)

La clé API par défaut est déjà configurée dans le script. Si vous souhaitez utiliser une variable d'environnement :

```bash
export MYSMM_API_KEY="votre_cle_api_ici"
```

---

## 📖 Utilisation

### 1. Vérifier son solde
```bash
python3 boost_simulator.py --balance
```

### 2. Mode Simulation (0 risque, aucun débit)
Génère la courbe, les visualisations et le coût sans envoyer d'ordre :
```bash
# 2 000 vues sur 8 heures (par défaut)
python3 boost_simulator.py --views 2000 --hours 8 --link "https://www.instagram.com/reel/XXXXX/"

# Avec partages activés
python3 boost_simulator.py --views 2000 --hours 8 --with-shares --link "https://www.instagram.com/reel/XXXXX/"
```

### 3. Mode Live (Exécution en direct)
Exécute les ordres réels avec les pauses calculées :
```bash
python3 boost_simulator.py --views 2000 --hours 8 --link "https://www.instagram.com/reel/XXXXX/" --live
```
*(Ajoutez `--yes` ou `-y` si vous souhaitez ignorer la demande de confirmation manuelle).*

---

## 🛡️ Faire tourner en arrière-plan (24/7 sur serveur)

Pour éviter que le script ne s'arrête lorsque vous fermez votre session SSH :

### Option 1 : Avec `tmux` (Recommandé)
```bash
# 1. Ouvrir une session tmux
tmux new -s boost

# 2. Activer le venv et lancer le script
source venv/bin/activate
python3 boost_simulator.py --views 2000 --hours 8 --link "https://www.instagram.com/reel/XXXXX/" --live -y

# 3. Détacher la session en toute sécurité :
# Appuyez sur Ctrl + B, puis relâchez et appuyez sur D

# 4. Pour réafficher la console plus tard :
tmux attach -t boost
```

### Option 2 : Avec `nohup`
```bash
nohup python3 boost_simulator.py --views 2000 --hours 8 --link "https://www.instagram.com/reel/XXXXX/" --live -y > boost.log 2>&1 &

# Pour suivre les logs en direct :
tail -f boost.log
```

---

## 🛠️ Commandes de diagnostic rapide

```bash
# Tester 100 vues immédiates sur un Reel
python3 boost_simulator.py --test-views "https://www.instagram.com/reel/XXXXX/"

# Tester 10 likes immédiats sur un Reel
python3 boost_simulator.py --test-likes "https://www.instagram.com/reel/XXXXX/"

# Tester 10 partages sur un Reel
python3 boost_simulator.py --test-shares "https://www.instagram.com/reel/XXXXX/"

# Consulter le statut d'une commande
python3 boost_simulator.py --status 49656079
```
