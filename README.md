# News Fetcher

Ce projet est une application Python qui récupère des articles de news depuis une API, filtre les articles par thème et génère un résumé pour chacun d'eux en utilisant une API de résumé de texte. Les résumés sont ensuite sauvegardés dans un fichier et une base de données.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Améliorations implémentées](#améliorations-implémentées)

## Fonctionnalités

- **Récupération des actualités** : Utilisation d'une API de news pour obtenir les dernières actualités.
- **Filtrage par thème** : Filtrage des articles pour ne garder que ceux correspondant à des thèmes prédéfinis (par exemple, technologie, santé, finance).
- **Résumé d'articles** : Génération d'un résumé pour chaque article filtré à l'aide d'une API de résumé.
- **Sauvegarde des résultats** : Enregistrement des résumés dans un fichier texte et une base de données.
- **Modes d'exécution multiples** : Support des modes synchrone, asynchrone et en arrière-plan.
- **Interface en ligne de commande** : Contrôle de l'application via des arguments en ligne de commande.

## Prérequis

- Python 3.7 ou plus récent
- Bibliothèques requises (voir `requirements.txt`):
  - `requests`
  - `python-dotenv`
  - `aiohttp` (pour les fonctionnalités asynchrones)
  - `SQLAlchemy` (pour l'intégration de la base de données)

## Installation

1. Clonez le repository dans votre répertoire local :

   ```bash
   git clone https://votre-depot.git
   cd news_fetcher
   ```

2. Créez et activez un environnement virtuel :

   ```bash
   python -m venv venv
   source venv/bin/activate    # Sur Linux/MacOS
   venv\Scripts\activate       # Sur Windows
   ```

3. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Avant d'exécuter l'application, configurez vos clés API et autres paramètres :

1. Copiez le fichier `.env.example` en `.env` :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos propres valeurs :
   - `NEWS_API_KEY` : Votre clé API pour l'API de news.
   - `OPENROUTER_API_KEY` : Votre clé API pour le service de résumé.
   - `OPENROUTER_URL` : L'URL de l'API de résumé.
   - `OPENROUTER_ENGINE_ID` : L'ID du modèle à utiliser pour la génération de résumés.
   - `DB_URL` : L'URL de connexion à la base de données.
   - `OUTPUT_FILE` : Le chemin du fichier de sortie pour les résumés.
   - `THEMES` : Liste des thèmes à filtrer, séparés par des virgules.

L'application utilise `python-dotenv` pour charger automatiquement ces variables d'environnement.

## Utilisation

Pour lancer l'application, exécutez le fichier principal avec les options souhaitées :

```bash
python main.py [options]
```

Options disponibles :
- `--async` : Exécute l'application en mode asynchrone
- `--background` : Exécute l'application en arrière-plan
- `--themes THEMES` : Liste de thèmes séparés par des virgules (remplace la configuration)
- `--output OUTPUT` : Fichier de sortie pour les résumés (remplace la configuration)
- `--country COUNTRY` : Code pays pour les articles (par défaut: us)
- `--debug` : Active les logs de débogage
- `--log-file LOG_FILE` : Chemin du fichier de log

L'application suivra les étapes suivantes :

1. Récupération des articles via l'API de news.
2. Filtrage des articles selon les thèmes définis.
3. Sauvegarde des articles dans la base de données.
4. Génération d'un résumé pour chaque article filtré.
5. Sauvegarde des résumés dans la base de données.
6. Sauvegarde des résumés dans le fichier de sortie configuré.

## Améliorations implémentées

Voici les améliorations qui ont été implémentées dans le projet :

1. **Restructuration du projet** :
   - Organisation en package Python avec structure modulaire
   - Séparation du code en modules logiques (api, models, utils, etc.)
   - Création d'un module de configuration dédié

2. **Gestion de la configuration** :
   - Chargement des variables d'environnement avec `python-dotenv`
   - Création d'un fichier `.env.example` avec configuration d'exemple
   - Classe de configuration pour gérer tous les paramètres

3. **Améliorations de l'intégration API** :
   - Classes client dédiées pour chaque API externe
   - Validation des réponses API
   - Mécanisme de retry pour les requêtes API échouées
   - Limitation du taux de requêtes

4. **Intégration de base de données** :
   - Base de données SQLite/PostgreSQL pour stocker articles et résumés
   - Modèles de données pour articles et résumés
   - Couche de persistance des données

5. **Traitement asynchrone** :
   - Implémentation des appels API asynchrones avec `aiohttp`
   - Traitement des tâches en arrière-plan avec `ThreadPoolExecutor`
   - Gestion des tâches asynchrones avec concurrence limitée

6. **Gestion des erreurs et journalisation** :
   - Système de journalisation centralisé avec niveaux configurables
   - Gestion spécifique des exceptions avec stratégies de récupération
   - Mécanisme de retry pour les opérations sujettes à échec
   - Journalisation dans la console et dans des fichiers

7. **Qualité du code** :
   - Annotations de type (type hints) dans tout le code
   - Documentation détaillée avec docstrings au format standard
   - Validation des entrées pour les fonctions principales

8. **Interface en ligne de commande** :
   - Arguments pour contrôler le mode d'exécution (synchrone, asynchrone, arrière-plan)
   - Options de configuration via la ligne de commande
   - Options de journalisation et de débogage
