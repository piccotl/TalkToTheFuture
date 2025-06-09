# 📨 TalkToTheFuture

**TalkToTheFuture** est une application de messagerie en ligne de commande (CLI) permettant d’envoyer des messages chiffrés à un destinataire, lisibles uniquement à partir d’une date spécifiée dans le futur.  
Le chiffrement de bout en bout et l’authentification cryptographique assurent la confidentialité, l’intégrité, et la non-répudiation des messages.

---

## 📁 Structure du projet

```

talk_to_the_future/
├── main.py                # Point d'entrée principal (lance la CLI)
├── demo.ipynb             # Démonstration interactive des principales fonctionnalités
├── requirements.txt       # Dépendances Python
├── app/                   # Contient la logique CLI (interface utilisateur)
├── crypto/                # Fonctions de chiffrement et cryptographie
├── models/                # Classes métier : Client, Server, Message, etc.
├── utils/                 # Utilitaires divers : logger, encodage de date, etc.

````

---

## 🛠️ Installation & Dépendances

```bash
pip install -r requirements.txt
```

---

## 💻 Utilisation de l'application (CLI)

Lancez l’application en ligne de commande avec :

```bash
python main.py
```

Vous pourrez :

* Créer un compte, vous connecter, changer de mot de passe
* Envoyer un message chiffré à un utilisateur
* Consulter vos messages lorsqu’ils sont déverrouillés

L’interface CLI est construite avec [questionary](https://github.com/tmbo/questionary) pour une navigation fluide et interactive.

---

## 📓 Notebook de démo

Le fichier [`demo.ipynb`](./demo.ipynb) fournit une démonstration pas-à-pas des fonctionnalités principales dans un environnement Jupyter. Il peut être utilisé à des fins de tests, d’explication pédagogique ou de validation.

---

## 📜 Licence

Ce projet est distribué à des fins pédagogiques. Aucun usage en production recommandé sans audit de sécurité.

*Ce README a été généré par intelligence artificielle.*

