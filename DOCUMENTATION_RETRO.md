# VICORE Web - Rétro-Documentation Fonctionnelle et Technique

## Table des Matières

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Documentation Fonctionnelle](#2-documentation-fonctionnelle)
3. [Documentation Technique](#3-documentation-technique)
4. [Architecture du Code](#4-architecture-du-code)
5. [Analyse de Sécurité](#5-analyse-de-sécurité)
6. [API Reference](#6-api-reference)
7. [Modèle de Données](#7-modèle-de-données)
8. [Guide de Déploiement](#8-guide-de-déploiement)

---

## 1. Vue d'Ensemble

### 1.1 Description du Projet

**VICORE** (Virtual Core Inspection System) est une application web de visualisation pour l'inspection des ressorts de trains ferroviaires. Elle est déployée pour Eurotunnel et permet aux opérateurs de visualiser, analyser et confirmer l'état des ressorts des wagons passant par le système d'inspection automatisé.

### 1.2 Objectifs Métier

| Objectif | Description |
|----------|-------------|
| **Visualisation** | Afficher les résultats d'inspection des trains en temps réel |
| **Analyse** | Permettre l'examen détaillé des images de ressorts |
| **Confirmation** | Permettre la validation humaine des détections automatiques |
| **Monitoring** | Surveiller la santé des systèmes d'inspection |

### 1.3 Stack Technologique

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                                │
│  Vue.js 2.6 │ Element-UI │ Bootstrap 5 │ Axios             │
├─────────────────────────────────────────────────────────────┤
│                      BACKEND                                 │
│  Flask 3.x │ SQLAlchemy 2.0 │ Pydantic │ Gunicorn          │
├─────────────────────────────────────────────────────────────┤
│                    DATA LAYER                                │
│  PostgreSQL │ Redis (Cache) │ eurotunnel_datamodel          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Documentation Fonctionnelle

### 2.1 Cas d'Utilisation Principaux

#### UC-01: Authentification Utilisateur
```
Acteur: Opérateur
Précondition: L'utilisateur possède un compte valide
Flux principal:
  1. L'utilisateur accède à l'application
  2. Le système affiche la page de connexion
  3. L'utilisateur saisit ses identifiants
  4. Le système valide et crée une session
  5. L'utilisateur est redirigé vers la vue système
Flux alternatif:
  4a. Identifiants invalides → Message d'erreur
```

#### UC-02: Visualisation des Passages de Trains
```
Acteur: Opérateur
Précondition: Utilisateur authentifié
Flux principal:
  1. Le système affiche la liste des passages par installation
  2. L'utilisateur sélectionne un passage
  3. Le système affiche les wagons du train avec indicateurs de confiance
  4. L'utilisateur peut charger plus de passages (lazy loading)
```

#### UC-03: Inspection d'un Wagon
```
Acteur: Opérateur
Précondition: Passage de train sélectionné
Flux principal:
  1. L'utilisateur clique sur un wagon
  2. Le système affiche la vue détaillée du wagon
  3. Le schéma SVG du bogie s'affiche avec les indicateurs de ressorts
  4. L'utilisateur navigue entre les ressorts (Previous/Next)
  5. L'image du ressort sélectionné s'affiche
```

#### UC-04: Confirmation de Ressort Manquant
```
Acteur: Opérateur
Précondition: Ressort détecté comme potentiellement absent
Flux principal:
  1. Le système signale un ressort avec faible niveau de confiance (code > 2)
  2. L'utilisateur clique sur "Confirm spring missing"
  3. Le système affiche toutes les images disponibles du ressort
  4. L'utilisateur confirme: "Spring Present" ou "Spring Missing"
  5. Le système enregistre la confirmation et met à jour l'affichage
```

### 2.2 Rôles Utilisateurs

| Rôle | Permissions |
|------|-------------|
| **Opérateur** | Visualisation, confirmation des ressorts, navigation |

*Note: Un seul rôle utilisateur est implémenté actuellement. Le système crée un utilisateur par défaut (`eurotunnel/Spr1ngs`) si aucun n'existe.*

### 2.3 Workflow Fonctionnel

```
                    ┌──────────────┐
                    │    LOGIN     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ SYSTEM VIEW  │◄────────────┐
                    │ (Liste des   │             │
                    │  passages)   │             │
                    └──────┬───────┘             │
                           │                     │
            ┌──────────────┼──────────────┐      │
            ▼              ▼              ▼      │
    ┌───────────┐  ┌───────────┐  ┌───────────┐ │
    │Installation│  │Installation│  │Installation│ │
    │     1      │  │     2      │  │     N      │ │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘ │
          │              │              │        │
          └──────────────┼──────────────┘        │
                         ▼                       │
                  ┌─────────────┐                │
                  │  CAR VIEW   │────────────────┘
                  │ (Détail     │    [Retour]
                  │  wagon)     │
                  └──────┬──────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ Ressort │ │ Ressort │ │ Ressort │
        │    1    │ │    2    │ │    N    │
        └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │
             └───────────┼───────────┘
                         ▼
                 ┌───────────────┐
                 │ CONFIRMATION  │ (si ressort AWOL)
                 │    MODAL      │
                 └───────────────┘
```

### 2.4 Niveaux de Confiance

Le système utilise des codes de confiance pour indiquer la fiabilité de la détection:

| Code | Signification | Couleur | Action Requise |
|------|---------------|---------|----------------|
| 0 | Confirmé présent (humain) | Bleu | Aucune |
| 1 | Détection haute confiance (GREEN) | Vert | Aucune |
| 2 | Confiance moyenne (AMBER) | Orange | Vérification recommandée |
| 3 | Faible confiance (RED) | Rouge | Confirmation requise |
| 5 | Non vérifié | Gris | N/A |

### 2.5 Types de Bogies Supportés

Le système supporte plusieurs configurations de bogies:

| Type | Essieux | SVG |
|------|---------|-----|
| Y25 | 2 essieux (4 roues) | `y25_include.html` |
| 4-axle | 4 essieux (8 roues) | `allotherbogies.html` |
| 6-axle | 6 essieux (12 roues) | `allotherbogies.html` |
| Coach | Variable | Dédié |

---

## 3. Documentation Technique

### 3.1 Architecture Applicative

```
eurotunnel_web/
├── app.py                      # Point d'entrée Flask
├── db_iface.py                 # Interface base de données
├── user_management.py          # Gestion utilisateurs/auth
├── system_endpoints.py         # Endpoints monitoring
├── train_pass_endpoints.py     # Endpoints passages trains
├── missing_spring_endpoints.py # Endpoints confirmation ressorts
├── confidence_levels.py        # Calcul niveaux confiance
├── display_name_iface.py       # Génération noms affichage
├── redis_web.py                # Interface cache Redis
├── common_consts.py            # Constantes partagées
├── version.py                  # Gestion version
├── models/
│   ├── user.py                 # Modèle utilisateur Pydantic
│   └── display_names_model.py  # Modèle noms affichage
├── templates/                  # Templates Jinja2
│   ├── base.html
│   ├── login.html
│   ├── systemview.html
│   ├── carview.html
│   └── includes/
└── static/                     # Assets statiques
    ├── css/
    ├── img/
    ├── scripts/
    └── train/
```

### 3.2 Flux de Données

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│    Flask    │────▶│ PostgreSQL  │
│  (Vue.js)   │◀────│   Backend   │◀────│  Database   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │    Redis    │
                    │   (Cache)   │
                    └─────────────┘
```

### 3.3 Composants Backend

#### 3.3.1 Application Flask (`app.py`)

**Responsabilités:**
- Configuration de l'application Flask
- Enregistrement des routes
- Gestion des sessions
- Middleware de cache HTTP
- Serveur de fichiers images

**Routes principales:**
```python
# Authentification
GET/POST /login          # Page et traitement login
GET      /logout         # Déconnexion

# Navigation principale
GET      /               # Vue système (alias listpasses)
GET      /listpasses/    # Liste des passages
GET      /get_train_passes/  # API: données passages

# Détail wagon
GET      /cars/<tpid>/<car_num>  # Vue détaillée wagon
POST     /getCar/<tpid>/<car_num>  # API: données wagon

# Lazy loading
POST     /loadTrainPasses/<last>/<n>/<install>  # Chargement progressif

# Confirmation ressorts
GET      /get_all_images_for_spring/<spring_id>  # Images ressort
PUT      /put_confirmation_status/<spring_id>/<status>  # Confirmation

# Monitoring
GET      /heartbeat/<system>     # Heartbeat système
GET      /hb_time/<system>       # Timestamp heartbeat
GET      /get_worst_system_status  # Statut global

# Images
GET      /wheelimg/<path>        # Serveur images roues
```

**Configuration:**
```python
# Clé secrète session (ATTENTION: hardcodée)
app.secret_key = 'slkfjaslkfdjlsadflknisdf64s6d4f56asf'

# Cache fichiers statiques: 1 heure
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

# Variables d'environnement
WEB_HOST      # Adresse d'écoute (défaut: 127.0.0.1)
WEB_PORT      # Port (défaut: 5000)
WEB_DEBUG     # Mode debug (défaut: False)
WHEEL_IMG_DIR # Répertoire images roues
```

#### 3.3.2 Interface Base de Données (`db_iface.py`)

**Fonctions principales:**

| Fonction | Description |
|----------|-------------|
| `get_train_pass_info()` | Récupère info basique d'un passage |
| `get_train_pass_cars()` | Liste des wagons d'un passage |
| `get_car_info_with_wheels()` | Détail wagon avec ressorts |
| `get_n_train_passes()` | N derniers passages |
| `get_n_train_passes_before()` | N passages avant une date |
| `get_n_train_passes_before_by_system()` | Idem filtré par installation |
| `get_all_image_paths_for_spring()` | Chemins images d'un ressort |

**Requêtes SQL personnalisées:**
```sql
-- Récupération passages avec fonction PostgreSQL
SELECT * FROM get_train_passes('{before}'::timestamp, {n}::int);
SELECT * FROM get_train_passes('{before}'::timestamp, {n}::int, {install}::int);

-- Récupération wagons et confirmations
SELECT * FROM get_pass_human_confirms_by_car_and_train_pass(:tpid, :car)
JOIN car_types ON car_types.car_type_id = cthc.car_type_id
JOIN bogie_type ON car_types.bogie_type = bogie_type.bogie_type_id
ORDER BY train_pass_order;
```

**Configuration confiance:**
```python
car_conf_method = 'min'        # Méthode calcul confiance wagon
train_conf_method = 'min'      # Méthode calcul confiance train
exclude_locos_conf = True      # Exclure locos du calcul
exclude_coaches_conf = True    # Exclure coaches du calcul
```

#### 3.3.3 Gestion Utilisateurs (`user_management.py`)

**Sécurité:**
- Hashage bcrypt des mots de passe
- Salt unique par utilisateur
- Validation via SQLAlchemy

**Fonctions:**
```python
authenticate_user(username, password) -> User | None
create_users_if_none()  # Crée utilisateur par défaut
create_user(user_name, password, display_name)
```

**Utilisateur par défaut:**
```python
# Créé si aucun utilisateur n'existe
username: "eurotunnel"
password: "Spr1ngs"
display_name: "Euro Tunnel"
```

#### 3.3.4 Endpoints Système (`system_endpoints.py`)

**Cache installations:**
```python
systems: Sequence[Installation] = []  # Cache global
# Rechargement requis au redémarrage pour nouvelles installations
```

**Monitoring heartbeat:**
```python
max_age_seconds  # Âge max heartbeat avant alerte
# Stocké dans Redis avec timestamp
```

#### 3.3.5 Niveaux de Confiance (`confidence_levels.py`)

**Pattern Singleton:**
```python
class confidence_interface:
    instance = None

    @staticmethod
    def GetConfidenceInterface():
        if instance is None:
            instance = confidence_interface()
        return instance
```

**Mapping codes:**
```python
# Ressorts/Wagons
confirmed_present → '0'  # Bleu
confidence_range  → '1' (GREEN), '2' (AMBER), '3' (RED)

# Trains
RED   → '5'
AMBER → '3'
GREEN → '1'
```

#### 3.3.6 Cache Redis (`redis_web.py`)

**Clés et TTL:**
```python
LABEL_PREFIX = "l:"           # Préfixe noms affichage
LABEL_RECALCULATE = 259200    # 3 jours TTL
INSTALLS_KEY = "INSTALLS"     # Clé installations
INSTALLS_EXPIRE = 3600        # 1 heure TTL
```

**Données cachées:**
- Noms d'affichage des passages (long_name, short_name)
- Heartbeats systèmes
- Liste des installations

### 3.4 Composants Frontend

#### 3.4.1 Structure Templates

```
templates/
├── base.html                    # Template de base
│   └── CDN: Bootstrap, Vue, Axios, Element-UI, jQuery
├── authorised_users_base.html   # Base authentifiée
│   └── Header, clock, système status, logout
├── login.html                   # Page connexion
│   └── Vue app: formulaire login
├── systemview.html              # Vue principale
│   └── Vue app: liste passages, sélection wagon
├── carview.html                 # Vue détail wagon
│   └── Vue app: image ressort, schéma bogie, confirmation
└── includes/
    ├── y25_include.html         # SVG bogie Y25
    ├── allotherbogies.html      # SVG autres bogies
    └── vue_error_alert.html     # Composant alerte erreur
```

#### 3.4.2 Application Vue - SystemView

**État (data):**
```javascript
{
    error_text: '',
    current_train_pass: {},
    installations: []  // Pré-peuplé via Jinja2
}
```

**Méthodes clés:**
| Méthode | Description |
|---------|-------------|
| `get_train_passes()` | Charge liste initiale |
| `fetchMoreTrainPasses(n, install)` | Lazy loading |
| `show_train_pass(id)` | Sélectionne un passage |
| `show_car(tpid, car_num)` | Navigue vers vue wagon |
| `get_car_confidence_class(car)` | CSS classe confiance |

#### 3.4.3 Application Vue - CarView

**État (data):**
```javascript
{
    train_pass: {},
    current_car: {},
    current_spring: 1,
    current_spring_obj: {},
    wheel_img: '',
    current_spring_awol: false,
    possible_spring_images: [],
    brightness: 100,
    contrast: 100
}
```

**Méthodes clés:**
| Méthode | Description |
|---------|-------------|
| `load_car(n)` | Charge données wagon |
| `show_spring(axle, camera)` | Affiche ressort spécifique |
| `goNext() / goPrev()` | Navigation ressorts |
| `send_status_confirmation(present)` | Envoie confirmation |
| `get_missing_spring_images(id)` | Charge images alternatives |
| `update_contrast/brightness()` | Ajuste image |

#### 3.4.4 Schémas SVG Bogies

Les bogies sont représentés par des SVG interactifs:

```html
<svg viewBox="0 0 100 137">
    <use href="#y25_bogie"
         data-bogie-offset="0"
         data-bogie-id="1" />
</svg>
```

**Variables CSS dynamiques:**
```css
--spring1col à --spring8col    /* Couleur ressort */
--extra-sel-1-opacity à -8     /* Sélection ressort */
--confirmed-okay-col           /* Bleu confirmé */
--okay-col                     /* Vert OK */
--unsure-col                   /* Orange incertain */
--bad-col                      /* Rouge problème */
```

### 3.5 Dépendances

#### Backend (pyproject.toml)
```toml
python = ">=3.10,<3.13"
Flask = ">3"
SQLAlchemy = "^2.0.29"
psycopg-binary = "^3.1.18"
redis = "*"
pydantic = "*"
bcrypt = "^4.1.2"
gunicorn = "*"
loguru = "*"
eurotunnel_datamodel = {path = "../eurotunnel_datamodel", optional = true}
```

#### Frontend (CDN)
```
Vue.js 2.6.14
Axios 0.21.4
Bootstrap 5.3.3
Element-UI 2.15.14
jQuery 3.7.1
```

---

## 4. Architecture du Code

### 4.1 Diagramme de Classes

```
┌─────────────────────────┐
│         Flask           │
│    Application (app)    │
└───────────┬─────────────┘
            │
    ┌───────┴───────┬───────────────┬───────────────┐
    ▼               ▼               ▼               ▼
┌─────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│ db_iface│  │train_pass_  │  │missing_     │  │system_       │
│         │  │endpoints    │  │spring_endpts│  │endpoints     │
└────┬────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
     │              │                │                │
     │       ┌──────┴──────┐         │                │
     │       ▼             ▼         │                │
     │  ┌─────────┐  ┌──────────┐    │          ┌─────▼─────┐
     │  │display_ │  │confidence│    │          │redis_web  │
     │  │name_iface│ │_levels   │    │          │           │
     │  └────┬────┘  └──────────┘    │          └─────┬─────┘
     │       │                       │                │
     └───────┼───────────────────────┼────────────────┘
             ▼                       ▼
      ┌─────────────────────────────────────┐
      │       eurotunnel_datamodel          │
      │  (DataModel, DatabaseHelpers,       │
      │   ConfigManager, redis_models)      │
      └─────────────────────────────────────┘
```

### 4.2 Séquence: Affichage Passage Train

```
Browser          Flask           db_iface        PostgreSQL      Redis
   │                │                │                │            │
   │ GET /          │                │                │            │
   │───────────────▶│                │                │            │
   │                │ get_n_train_   │                │            │
   │                │ passes(50)     │                │            │
   │                │───────────────▶│                │            │
   │                │                │ SELECT FROM    │            │
   │                │                │ get_train_     │            │
   │                │                │ passes()       │            │
   │                │                │───────────────▶│            │
   │                │                │◀───────────────│            │
   │                │                │                │            │
   │                │                │ get_displayname│            │
   │                │                │────────────────┼───────────▶│
   │                │                │◀───────────────┼────────────│
   │                │◀───────────────│                │            │
   │                │                │                │            │
   │ HTML + JSON    │                │                │            │
   │◀───────────────│                │                │            │
   │                │                │                │            │
```

### 4.3 Séquence: Confirmation Ressort

```
Browser          Flask           missing_spring   PostgreSQL
   │                │                │                │
   │ PUT /put_      │                │                │
   │ confirmation   │                │                │
   │───────────────▶│                │                │
   │                │ put_confirma-  │                │
   │                │ tion_status()  │                │
   │                │───────────────▶│                │
   │                │                │ Check exists   │
   │                │                │───────────────▶│
   │                │                │◀───────────────│
   │                │                │                │
   │                │                │ mark_human_    │
   │                │                │ confirmed()    │
   │                │                │───────────────▶│
   │                │                │◀───────────────│
   │                │                │ (n_remaining)  │
   │                │◀───────────────│                │
   │                │                │                │
   │ {n_remaining}  │                │                │
   │◀───────────────│                │                │
```

---

## 5. Analyse de Sécurité

### 5.1 Points Forts

| Aspect | Implémentation |
|--------|----------------|
| **Authentification** | Bcrypt avec salt unique |
| **Sessions** | Flask secure sessions |
| **Autorisation** | Vérification session sur chaque endpoint protégé |
| **SQL Injection** | SQLAlchemy ORM + paramètres préparés |
| **Cache Control** | Headers no-store sur API endpoints |

### 5.2 Points d'Attention

| Risque | Niveau | Description | Recommandation |
|--------|--------|-------------|----------------|
| **Secret Key hardcodée** | ÉLEVÉ | `app.secret_key` en dur dans le code | Utiliser variable d'environnement |
| **Credentials par défaut** | MOYEN | User/password par défaut créés auto | Forcer changement au 1er login |
| **HTTPS non forcé** | MOYEN | Pas de redirection HTTP→HTTPS | Configurer au niveau reverse proxy |
| **Pas de rate limiting** | FAIBLE | Pas de protection brute force | Ajouter Flask-Limiter |
| **Pas de CSRF token** | FAIBLE | Forms sans protection CSRF | Ajouter Flask-WTF |

### 5.3 Vérification d'Autorisation

Chaque endpoint protégé vérifie la session:
```python
user_json = session.get(USER_DETAILS_SESSION_VAR)
if not user_json:
    return redirect('/login')  # ou abort(403)
```

### 5.4 Recommandations Prioritaires

1. **Critique**: Externaliser `app.secret_key` vers variable d'environnement
2. **Important**: Ajouter politique de mot de passe fort
3. **Important**: Implémenter audit log des confirmations
4. **Recommandé**: Ajouter rate limiting sur `/login`
5. **Recommandé**: Activer HTTPS obligatoire

---

## 6. API Reference

### 6.1 Authentification

#### POST /login
**Description:** Authentifie un utilisateur

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Responses:**
| Code | Body | Description |
|------|------|-------------|
| 200 | `"1"` | Succès, session créée |
| 200 | `"01"` | Identifiants invalides |
| 200 | `"0"` | Erreur serveur |

### 6.2 Passages de Trains

#### GET /get_train_passes/
**Description:** Récupère les 50 derniers passages

**Response:**
```json
[
    {
        "installation_id": 1,
        "location": "Coquelles",
        "train_passes": [
            {
                "train_pass_id": 12345,
                "time_start": "2024-01-15T10:30:00",
                "conf_code": "1",
                "disp_name": "2024 01 15 - 10:30:00 1234",
                "disp_name_short": "24 01 15 - 10:30 1234"
            }
        ]
    }
]
```

#### POST /getTrainPass/{tpid}
**Description:** Récupère détails d'un passage avec ses wagons

**Response:**
```json
{
    "train_pass_id": 12345,
    "time_start": "2024-01-15T10:30:00",
    "disp_name": "...",
    "cars": [
        {
            "car_num": 1,
            "disp_name": "1234",
            "idtype": "RFID: ETMR-1234-5",
            "min_conf": 0.95,
            "conf_code": "1",
            "car_icon": "frt-carrier",
            "nbg": 2,
            "nax": 2,
            "bogie_svg": "y25"
        }
    ]
}
```

#### POST /loadTrainPasses/{last_shown}/{n_to_fetch}/{installation_id?}
**Description:** Lazy loading de passages supplémentaires

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| last_shown | ISO datetime | Date du dernier passage affiché |
| n_to_fetch | int | Nombre à charger (défaut: 25) |
| installation_id | int? | Filtrer par installation |

### 6.3 Détail Wagon

#### POST /getCar/{train_pass_id}/{car_num}
**Description:** Récupère détails wagon avec ressorts

**Response:**
```json
{
    "car_num": 1,
    "disp_name": "1234",
    "nbg": 2,
    "nax": 2,
    "bogie_svg": "y25",
    "springs": [
        {
            "ax": 1,
            "conf_code": "1",
            "conf": 0.95,
            "img": "2024/01/15/pass_12345/wheel_001.jpg",
            "pos": "L",
            "spring_id": 56789,
            "human_confirm": null,
            "has_human_confirm": false
        }
    ]
}
```

### 6.4 Confirmation Ressorts

#### GET /get_all_images_for_spring/{spring_location}
**Description:** Récupère toutes les images disponibles d'un ressort

**Response:**
```json
[
    "/mnt/outgoing/2024/01/15/img1.jpg",
    "/mnt/outgoing/2024/01/15/img2.jpg"
]
```

#### PUT /put_confirmation_status/{spring_location}/{human_says}
**Description:** Enregistre confirmation humaine

**Parameters:**
| Param | Values | Description |
|-------|--------|-------------|
| spring_location | int | ID du ressort |
| human_says | "true"/"false" | Ressort présent ou absent |

**Responses:**
| Code | Body | Description |
|------|------|-------------|
| 200 | `{"n_remaining": 5}` | Succès |
| 409 | - | Déjà confirmé |
| 403 | - | Non authentifié |

### 6.5 Monitoring

#### GET /heartbeat/{system}
**Description:** Récupère heartbeat complet d'un système

**Response:** JSON heartbeat complet ou status 412 si absent

#### GET /hb_time/{system}
**Description:** Récupère timestamp dernier heartbeat

**Response:** ISO datetime string

#### GET /get_worst_system_status
**Description:** Statut global de tous les systèmes

**Response:**
| Value | Description |
|-------|-------------|
| `true` | Tous systèmes OK |
| `false` | Au moins un système en erreur |

---

## 7. Modèle de Données

### 7.1 Entités Principales

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  TrainPass    │     │ TrainPassCars │     │   CarTypes    │
├───────────────┤     ├───────────────┤     ├───────────────┤
│ train_pass_id │◀───┐│ train_pass_id │     │ car_type_id   │
│ time_start    │    ││ car_type_id   │────▶│ icon_head     │
│ time_end      │    ││ train_pass_   │     │ icon_tail     │
│ installation  │    ││ order         │     │ bogie_type    │
│ train_service │    ││ car_num       │     │ num_bogies    │
│ _code         │    ││ rfid_tag_code │     │ axles_per_    │
└───────────────┘    │└───────────────┘     │ bogie         │
                     │                      └───────┬───────┘
                     │                              │
                     │                      ┌───────▼───────┐
                     │                      │  BogieType    │
                     │                      ├───────────────┤
                     │                      │ bogie_type_id │
                     │                      │ svgname       │
                     │                      └───────────────┘

┌───────────────┐     ┌───────────────────┐
│SpringLocation │     │HumanConfirmations │
├───────────────┤     ├───────────────────┤
│spring_location│────▶│spring_location_id │
│_id            │     │present_not_absent │
│train_pass_id  │     │confirmed_by       │
│train_axle_    │     │confirmed_at       │
│number         │     └───────────────────┘
│cam_pos        │
│confidence     │     ┌───────────────────┐
│best_image_path│     │SpringImageLocation│
└───────────────┘────▶├───────────────────┤
                      │spring_location_id │
                      │image_path         │
                      └───────────────────┘
```

### 7.2 Tables Système

```
┌───────────────┐     ┌───────────────┐
│ Installation  │     │    Users      │
├───────────────┤     ├───────────────┤
│installation_id│     │ user_id       │
│ location      │     │ user_name     │
│ description   │     │ display_name  │
└───────────────┘     │ password_hash │
                      │ password_salt │
┌───────────────┐     └───────────────┘
│ConfidenceLvls │
├───────────────┤
│confidence_lvl │
│conf_range     │
│level_name_en  │
└───────────────┘
```

### 7.3 Fonctions PostgreSQL

Le système utilise des fonctions stockées PostgreSQL:

| Fonction | Description |
|----------|-------------|
| `get_train_passes(timestamp, int, int?)` | Récupère N passages avant date |
| `get_pass_human_confirms_by_car_and_train_pass(int, int)` | Wagons avec confirmations |
| `mark_human_confirmed(int, bool, str)` | Enregistre confirmation |
| `get_first_tag(int)` | Premier tag RFID d'un passage |

---

## 8. Guide de Déploiement

### 8.1 Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `WEB_HOST` | Adresse d'écoute | `127.0.0.1` |
| `WEB_PORT` | Port d'écoute | `5000` |
| `WEB_DEBUG` | Mode debug | `False` |
| `WHEEL_IMG_DIR` | Répertoire images roues | `/mnt/c/.../wheelimg` |
| `DB_HOST` | Hôte PostgreSQL | `localhost` |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `DB` | Nom base de données | `euro_tunnel_dev` |
| `DB_USER` | Utilisateur DB | - |
| `DB_PASSWORD` | Mot de passe DB | - |

### 8.2 Docker

**Configuration typique:**
```yaml
services:
  web:
    image: eurotunnel_web
    ports:
      - "1234:5000"
    environment:
      - WEB_HOST=0.0.0.0
      - WEB_PORT=5000
      - WHEEL_IMG_DIR=/mnt/wheelimg
    volumes:
      - /path/to/images:/mnt/wheelimg:ro
```

### 8.3 Production avec Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 eurotunnel_web.app:app
```

### 8.4 Prérequis

- Python 3.10-3.12
- PostgreSQL avec schéma eurotunnel_datamodel
- Redis server
- Accès au répertoire images

### 8.5 Installation Locale

```bash
# Cloner le repo
git clone <repo_url>
cd eurotunnel_web

# Installer dépendances
poetry install --with datamodel

# Configurer environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Lancer
poetry run python -m eurotunnel_web.app
```

---

## Annexes

### A. Glossaire

| Terme | Définition |
|-------|------------|
| **Train Pass** | Enregistrement d'un passage de train par le système d'inspection |
| **Car** | Wagon individuel d'un train |
| **Spring** | Ressort de suspension d'un bogie |
| **Bogie** | Châssis porteur des essieux d'un wagon |
| **AWOL** | Absent Without Leave - ressort potentiellement manquant |
| **Confidence** | Niveau de certitude de la détection automatique |
| **RFID Tag** | Identifiant radio-fréquence du wagon |

### B. Codes d'Erreur HTTP

| Code | Contexte | Signification |
|------|----------|---------------|
| 200 | Global | Succès |
| 204 | get_train_passes | Aucune donnée |
| 400 | getTrainPass | ID manquant |
| 403 | Endpoints protégés | Non authentifié |
| 409 | put_confirmation | Déjà confirmé |
| 412 | heartbeat | Heartbeat absent |
| 500 | loadTrainPasses | Paramètre last_shown invalide |

### C. Conventions de Code

- **Backend**: Python PEP 8, type hints
- **Frontend**: Vue.js 2 Options API
- **Templates**: Jinja2 avec délimiteurs Vue `[[ ]]`
- **SQL**: Fonctions PostgreSQL pour logique complexe

---

*Document généré le 2026-01-16*
*Version: 1.0.0.12*
