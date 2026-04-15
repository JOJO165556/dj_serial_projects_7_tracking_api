# Tracking API

API REST de suivi de colis en temps réel, construite avec Django et Django REST Framework.

## Description

Système de gestion logistique permettant aux clients de créer et suivre leurs colis, aux livreurs de mettre à jour les statuts en transit, et aux administrateurs de superviser l'ensemble des opérations. Les mises à jour de position se propagent en temps réel via WebSocket.

## Fonctionnalités

- Authentification JWT (accès et rafraîchissement)
- Rôles distincts : client, livreur, administrateur
- Création de colis avec génération automatique d'un code de tracking
- Suivi public d'un colis par son code de tracking
- Assignation automatique du livreur le plus proche (algorithme Haversine)
- Mise à jour du statut par le livreur assigné
- Notifications en temps réel via WebSocket (Django Channels)
- Tableau de bord administrateur (statistiques colis et livreurs)
- Analytiques : KPIs de livraison, temps moyen, activité sur 24h
- Internationalisation : français et anglais (Django i18n)
- Documentation API interactive (Swagger / ReDoc via drf-spectacular)

## Stack technique

- Python 3.12
- Django 6.0
- Django REST Framework 3.17
- Django Channels 4.3 (WebSocket)
- PostgreSQL (production) / SQLite (développement local)
- Redis (channel layer en production)
- drf-spectacular (OpenAPI 3.0)
- Simple JWT

## Structure du projet

```
tracking_api/
├── apps/
│   ├── analytics/       # KPIs et statistiques
│   ├── couriers/        # Profils livreurs, position GPS
│   ├── dashboard/       # Vue d'ensemble administrateur
│   ├── notifications/   # Notifications persistantes et WebSocket
│   ├── parcels/         # Colis, statuts, assignation
│   ├── realtime/        # Consumers WebSocket, middleware JWT
│   ├── tracking/        # Événements de suivi (timeline)
│   └── users/           # Modèle utilisateur, permissions
├── config/
│   ├── settings/
│   │   ├── base.py      # Configuration commune
│   │   ├── dev.py       # Développement
│   │   └── prod.py      # Production
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
│   └── responses/       # Wrappers de réponse standardisés (success/error)
├── locale/              # Traductions (fr, en)
├── .github/workflows/   # Pipeline CI (GitHub Actions)
├── docker-compose.yml   # Base PostgreSQL locale
├── .coveragerc
└── requirements.txt
```

## Installation

### Prérequis

- Python 3.12
- Docker (pour PostgreSQL local)

### Mise en place

```bash
# Cloner le dépôt
git clone <url-du-depot>
cd tracking_api

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer les variables d'environnement
cp .env.example .env
# Renseigner SECRET_KEY et DATABASE_URL dans .env

# Démarrer la base de données
docker compose up -d

# Appliquer les migrations
python manage.py migrate

# Compiler les traductions
python manage.py compilemessages

# Lancer le serveur de développement
python manage.py runserver
```

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django | `change-me-in-production` |
| `DATABASE_URL` | URL de connexion à la base | `postgres://postgres:postgres@localhost:5432/test_db` |
| `DEBUG` | Mode debug | `True` |

## Base de données locale (Docker)

```bash
# Démarrer PostgreSQL
docker compose up -d

# Arrêter
docker compose down
```

Le conteneur expose PostgreSQL sur le port `5433` pour éviter les conflits avec une installation locale sur `5432`.

Pour pointer Django sur ce conteneur :

```bash
DATABASE_URL="postgres://postgres:postgres@localhost:5433/test_db" python manage.py migrate
```

## Tests

La suite de tests couvre les permissions, les endpoints API et la logique métier (21 tests, 93% de couverture).

```bash
# Avec PostgreSQL Docker (port 5433)
DB_PORT=5433 DATABASE_URL="postgres://postgres:postgres@localhost:5433/test_db" coverage run --source='.' manage.py test

# Rapport de couverture
coverage report
```

## Documentation API

Démarrer le serveur, puis ouvrir :

- Swagger UI : `http://localhost:8000/api/docs/`
- ReDoc : `http://localhost:8000/api/redoc/`
- Schéma OpenAPI : `http://localhost:8000/api/schema/`

Valider le schéma :

```bash
python manage.py spectacular --validate --fail-on-warn
```

## Endpoints principaux

| Méthode | URL | Description | Rôle requis |
|---|---|---|---|
| POST | `/api/auth/token/` | Obtenir un token JWT | - |
| POST | `/api/auth/refresh/` | Rafraîchir le token | - |
| POST | `/api/users/create/` | Créer un compte | - |
| POST | `/api/parcels/create/` | Créer un colis | Client |
| GET | `/api/parcels/` | Lister mes colis | Client |
| GET | `/api/parcels/track/<code>/` | Suivre un colis | - |
| PATCH | `/api/parcels/status/<id>/` | Mettre à jour le statut | Livreur assigné |
| POST | `/api/parcels/assign/<id>/` | Assigner un livreur | Admin |
| PATCH | `/api/couriers/me/` | Mettre à jour sa position | Livreur |
| GET | `/api/couriers/available/` | Livreurs disponibles | Authentifié |
| GET | `/api/dashboard/` | Tableau de bord | Admin |
| GET | `/api/analytics/` | KPIs | Admin |
| GET | `/api/notifications/` | Mes notifications | Authentifié |
| PATCH | `/api/notifications/<id>/read/` | Marquer comme lu | Authentifié |

## WebSocket

```
ws://<host>/ws/tracking/<parcel_id>/    # Suivi temps réel d'un colis
ws://<host>/ws/notifications/           # Notifications utilisateur
```

Authentification : passer le token JWT en query string `?token=<access_token>`.

## Format de réponse

Toutes les réponses API suivent le même format :

```json
{
    "status": "success",
    "message": "...",
    "data": { ... }
}
```

En cas d'erreur :

```json
{
    "status": "error",
    "message": "...",
    "data": null
}
```

## Intégration continue

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) s'exécute à chaque push sur `main` :

1. Création d'un conteneur PostgreSQL 15
2. Installation des dépendances
3. Migrations
4. Tests avec coverage (seuil minimum : 70%)
5. Lint avec flake8

## Internationalisation

L'API supporte le français et l'anglais. Pour régénérer les fichiers de traduction :

```bash
python manage.py makemessages -l fr -l en
# Renseigner les traductions dans locale/fr/LC_MESSAGES/django.po
python manage.py compilemessages
```
