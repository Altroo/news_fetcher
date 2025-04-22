# News Fetcher

Ce projet est une application Python qui récupère des articles de news depuis une API, filtre les articles par thème et génère un résumé pour chacun d'eux en utilisant une API de résumé de texte. Les résumés sont ensuite sauvegardés dans un fichier.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Auteurs et Licence](#auteurs-et-licence)

## Fonctionnalités

- **Récupération des actualités** : Utilisation d'une API de news pour obtenir les dernières actualités.
- **Filtrage par thème** : Filtrage des articles pour ne garder que ceux correspondant à des thèmes prédéfinis (par exemple, technologie, santé, finance).
- **Résumé d'articles** : Génération d'un résumé pour chaque article filtré à l'aide d'une API de résumé.
- **Sauvegarde des résultats** : Enregistrement des résumés dans un fichier texte.

## Prérequis

- Python 3.7 ou plus récent
- Bibliothèque `requests`

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
   pip install requests
   ```

## Configuration

Avant d'exécuter l'application, configurez vos clés API et autres paramètres :

- Définissez les variables d'environnement suivantes :
  - `NEWS_API_KEY` : Votre clé API pour l'API de news.
  - `OPENROUTER_API_KEY` : Votre clé API pour le service de résumé.
  - `OPENROUTER_URL` (optionnel) : L'URL de l'API de résumé si différente de la valeur par défaut.

Vous pouvez également modifier directement les valeurs par défaut dans le fichier `main.py`, mais il est recommandé d'utiliser les variables d'environnement pour des raisons de sécurité.

## Utilisation

Pour lancer l'application, exécutez simplement le fichier principal :
L'application suivra les étapes suivantes :

1. Récupération des articles via l'API de news.
2. Filtrage des articles selon les thèmes définis.
3. Génération d'un résumé pour chaque article filtré.
4. Sauvegarde des résumés dans le fichier `news_summaries.txt`.

## Améliorations possibles

Voici quelques suggestions pour améliorer le fichier :
1. **Utiliser des variables d'environnement pour les clés API :**
Plutôt que de coder en dur vos clés API dans le code, il est préférable de les charger depuis des variables d'environnement. Cela renforce la sécurité et facilite la configuration dans différents environnements.
2. **Passer à l'utilisation du module logging :**
Remplacer les appels à print par le module standard logging permet de mieux gérer le niveau de détail des messages (infos, avertissements, erreurs) et de rediriger la sortie vers un fichier si nécessaire.
3. **Utiliser une session HTTP avec requests :**
Lorsque vous effectuez plusieurs appels HTTP (ex. pour la récupération d'articles et la demande de résumé), l'utilisation de requests.Session peut améliorer les performances en réutilisant les connexions.
4. **Gérer davantage d'exceptions spécifiques :**
Pour améliorer la robustesse, vous pouvez capturer des exceptions spécifiques (par exemple, requests.exceptions.HTTPError ou requests.exceptions.ConnectionError) au lieu d'une Exception générale.
5. **Clarifier et documenter certaines sections du code :**
Vous pouvez ajouter des commentaires ou des docstrings plus détaillés pour faciliter la compréhension et la maintenance du code.
6. **Modulariser éventuellement le code pour la testabilité :**
En regroupant des fonctions dans des classes ou en utilisant des modules séparés (par exemple, un module pour l’API News, un autre pour l’API OpenRouter), il sera plus facile d’écrire des tests unitaires et d’évoluer le projet.

## Améliorations possibles v2

1. **Utiliser un backend Django :**  
Associer l'application à un backend Django pour sauvegarder ces articles dans une base de données.

2. **Utiliser un script spécifique pour le scraping :**  
Créer un script dédié pour scraper ces articles et les enregistrer dans la base de données, en le configurant pour s'exécuter via une commande line Django.

3. **Utiliser .filter directement sur la base de données :**  
Appliquer le filtre des thèmes, par exemple, directement sur les articles sauvegardés.

4. **Utiliser Celery :**  
Intégrer Celery avec le backend Django pour exécuter les tâches de résumé de manière asynchrone avec un modèle d'IA.

5. **Définir comment obtenir le résultat :**  
Envoyer automatiquement le résultat du résumé par email ou l'enregistrer dans une table dédiée.