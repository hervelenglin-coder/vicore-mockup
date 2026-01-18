# DAT - Dossier d'Architecture Technique
## VICORE V2 - VIsualisation COntrole REssorts

| Champ | Valeur |
|-------|--------|
| **Version** | 1.0 |
| **Date** | 2026-01-18 |
| **Statut** | En cours de redaction |
| **Auteur** | Architecte Technique |
| **Validation** | A valider |

---

## Historique des Modifications

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-01-18 | Architecte | Creation initiale |

---

## Table des Matieres

1. [Introduction](#1-introduction)
2. [Contraintes Architecturales](#2-contraintes-architecturales)
3. [Decisions Architecturales](#3-decisions-architecturales)
4. [Architecture Logique](#4-architecture-logique)
5. [Architecture Physique](#5-architecture-physique)
6. [Patterns et Principes](#6-patterns-et-principes)
7. [Vues Architecturales](#7-vues-architecturales)
8. [Qualite et Attributs](#8-qualite-et-attributs)
9. [Risques et Mitigations](#9-risques-et-mitigations)

---

## 1. Introduction

### 1.1 Objectif du Document

Ce document presente l'architecture technique du systeme VICORE V2. Il decrit les choix architecturaux, leur justification, et fournit une vision globale de la structure du systeme.

### 1.2 Audience

| Audience | Utilisation |
|----------|-------------|
| Architectes | Reference pour decisions techniques |
| Developpeurs | Guide d'implementation |
| Ops/DevOps | Comprehension infrastructure |
| Direction | Vision globale du systeme |

### 1.3 Contexte Systeme

```
+------------------------------------------------------------------+
|                    ENVIRONNEMENT EUROTUNNEL                       |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+     +-------------------+                  |
|  |  Systeme Cameras  |     |    Heartbeat      |                  |
|  |  (Detection)      |     |    System         |                  |
|  +--------+----------+     +--------+----------+                  |
|           |                         |                             |
|           |    Donnees ressorts     |    Status cameras           |
|           |                         |                             |
|           v                         v                             |
|  +--------------------------------------------------+            |
|  |                   VICORE V2                       |            |
|  |                                                   |            |
|  |  - Affichage passages trains                     |            |
|  |  - Visualisation wagons et ressorts              |            |
|  |  - Alertes et confirmations                      |            |
|  |  - Monitoring temps reel                         |            |
|  +--------------------------------------------------+            |
|           |                                                       |
|           v                                                       |
|  +-------------------+                                           |
|  |   Operateurs      |                                           |
|  |   (Navigateur)    |                                           |
|  +-------------------+                                           |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 2. Contraintes Architecturales

### 2.1 Contraintes Techniques

| ID | Contrainte | Impact |
|----|------------|--------|
| CT-01 | Deploiement sur infrastructure existante | Architecture conteneurisee |
| CT-02 | Compatibilite navigateurs modernes | Standards web HTML5/CSS3 |
| CT-03 | Performance temps reel | WebSocket/SSE pour updates |
| CT-04 | Integration systemes existants | APIs REST standardisees |
| CT-05 | Base de donnees relationnelle | PostgreSQL impose |

### 2.2 Contraintes Organisationnelles

| ID | Contrainte | Impact |
|----|------------|--------|
| CO-01 | Equipe Python/Flask existante | Maintien stack Python |
| CO-02 | Competences frontend limitees | Vue.js + composants pre-faits |
| CO-03 | Budget infrastructure limite | Solutions open-source |
| CO-04 | Delai de livraison serre | Architecture simple et eprouvee |

### 2.3 Contraintes Reglementaires

| ID | Contrainte | Impact |
|----|------------|--------|
| CR-01 | Tracabilite des operations | Audit logs obligatoires |
| CR-02 | Securite des acces | Authentification forte |
| CR-03 | Protection des donnees | Chiffrement, RGPD |

---

## 3. Decisions Architecturales

### 3.1 ADR-001: Architecture Monolithique Modulaire

**Contexte:** Choix entre microservices et monolithe pour l'architecture globale.

**Decision:** Architecture monolithique modulaire.

**Justification:**
- Equipe reduite (2-3 developpeurs)
- Complexite operationnelle reduite
- Performance optimale sans latence reseau inter-services
- Deploiement et debug simplifies
- Evolution possible vers microservices si necessaire

**Consequences:**
- (+) Developpement plus rapide
- (+) Moins de complexite DevOps
- (-) Scaling vertical uniquement a court terme
- (-) Couplage plus fort entre modules

### 3.2 ADR-002: Framework Flask

**Contexte:** Choix du framework web Python.

**Decision:** Flask avec extensions.

**Alternatives considerees:**
| Framework | Avantages | Inconvenients |
|-----------|-----------|---------------|
| Django | Batteries included, admin | Trop lourd, conventions rigides |
| FastAPI | Async, performance | Moins mature, moins d'extensions |
| Flask | Flexible, leger | Plus de configuration manuelle |

**Justification:**
- Flexibilite maximale
- Ecosysteme mature d'extensions
- Courbe d'apprentissage douce
- Expertise equipe existante

### 3.3 ADR-003: PostgreSQL comme SGBD

**Contexte:** Choix du systeme de base de donnees.

**Decision:** PostgreSQL 16+.

**Justification:**
- Performance excellente
- Types de donnees riches (JSONB, arrays)
- Extensions utiles (pg_stat_statements, pgaudit)
- Fiabilite eprouvee
- Open source, sans cout de licence

### 3.4 ADR-004: Redis pour Cache et Sessions

**Contexte:** Besoin de cache applicatif et gestion des sessions.

**Decision:** Redis comme store de cache et sessions.

**Justification:**
- Performance memoire
- Structures de donnees riches
- TTL natif pour expiration
- Persistence optionnelle
- Support clustering futur

### 3.5 ADR-005: Authentification SSO Eurotunnel

**Contexte:** Mecanisme d'authentification pour l'application.

**Decision:** Integration avec le SSO Eurotunnel via SAML 2.0.

**Alternatives considerees:**
| Methode | Avantages | Inconvenients |
|---------|-----------|---------------|
| Authentification locale | Autonomie complete | Gestion mots de passe, securite |
| JWT propre | Stateless, scalable | Double gestion d'identites |
| SSO Eurotunnel | Centralise, politique securite unifiee | Dependance externe |

**Justification:**
- Politique de securite centralisee Eurotunnel
- Pas de gestion de mots de passe dans VICORE
- Utilisateurs deja familiers avec le portail SSO
- Single Sign-On avec autres applications Eurotunnel
- Conformite avec les standards IT Eurotunnel

**Consequences:**
- (+) Securite geree par le SSO
- (+) Experience utilisateur unifiee
- (+) Pas de mot de passe a stocker
- (-) Dependance au service SSO
- (-) Configuration SAML requise

### 3.6 ADR-006: Architecture Frontend SPA Hybride

**Contexte:** Approche pour l'interface utilisateur.

**Decision:** Templates Jinja2 + Vue.js components.

**Justification:**
- Rendu serveur pour SEO et performance initiale
- Vue.js pour interactivite dynamique
- Element UI pour composants professionnels
- Pas de build complexe (CDN)

---

## 4. Architecture Logique

### 4.1 Decomposition en Modules

```
+------------------------------------------------------------------+
|                         VICORE V2                                 |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |      AUTH        |  |   TRAIN_PASSES   |  |       CARS       | |
|  |                  |  |                  |  |                  | |
|  | - SSO Login      |  | - List passes    |  | - List cars      | |
|  | - Session mgmt   |  | - Pass details   |  | - Car details    | |
|  | - User mgmt      |  | - Confirmations  |  | - Springs view   | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |     SPRINGS      |  |      ALERTS      |  |    MONITORING    | |
|  |                  |  |                  |  |                  | |
|  | - Spring data    |  | - List alerts    |  | - Heartbeat      | |
|  | - Measurements   |  | - Acknowledge    |  | - System health  | |
|  | - Thresholds     |  | - Notifications  |  | - Camera status  | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |      AUDIT       |  |      ADMIN       |  |     REPORTS      | |
|  |                  |  |                  |  |                  | |
|  | - Action logs    |  | - User CRUD      |  | - Export data    | |
|  | - Trail history  |  | - Config mgmt    |  | - Statistics     | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
+------------------------------------------------------------------+
```

### 4.2 Dependances entre Modules

```
                    +------------------+
                    |       AUTH       |
                    +--------+---------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
+------------------+ +------------------+ +------------------+
|  TRAIN_PASSES    | |      ADMIN       | |      AUDIT       |
+--------+---------+ +------------------+ +------------------+
         |                                         ^
         v                                         |
+------------------+                               |
|       CARS       +--------------+----------------+
+--------+---------+              |
         |                        |
         v                        v
+------------------+     +------------------+
|     SPRINGS      |     |      ALERTS      |
+------------------+     +------------------+
         |
         v
+------------------+
|    MONITORING    |
+------------------+
```

### 4.3 Structure des Packages

```
app/
├── __init__.py              # Application factory
├── config.py                # Configuration
├── extensions.py            # Flask extensions
│
├── modules/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py        # Blueprints
│   │   ├── services.py      # Business logic
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Marshmallow schemas
│   │
│   ├── train_passes/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── services.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── cars/
│   │   └── ...
│   │
│   ├── springs/
│   │   └── ...
│   │
│   ├── alerts/
│   │   └── ...
│   │
│   └── monitoring/
│       └── ...
│
├── common/
│   ├── decorators.py        # Auth decorators
│   ├── exceptions.py        # Custom exceptions
│   ├── utils.py             # Utilities
│   └── validators.py        # Input validation
│
└── templates/
    ├── base.html
    ├── auth/
    ├── train_passes/
    └── ...
```

---

## 5. Architecture Physique

### 5.1 Topologie de Deploiement

```
                        INTERNET
                            |
                            | HTTPS (443)
                            v
                   +------------------+
                   |    Firewall      |
                   +--------+---------+
                            |
                            v
+------------------------------------------------------------------+
|                        DMZ                                        |
|  +------------------+                                             |
|  |      Nginx       |  Reverse proxy, SSL termination            |
|  |  (Load Balancer) |  Rate limiting, static files               |
|  +--------+---------+                                             |
+-----------|------------------------------------------------------|
            | HTTP (8000)
            v
+------------------------------------------------------------------+
|                    APPLICATION ZONE                               |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |   App Server 1   |  |   App Server 2   |  |   App Server 3   | |
|  |   (Gunicorn)     |  |   (Gunicorn)     |  |   (Gunicorn)     | |
|  +--------+---------+  +--------+---------+  +--------+---------+ |
|           |                     |                     |           |
|           +----------+----------+----------+----------+           |
|                      |                     |                      |
+----------------------|---------------------|----------------------+
                       v                     v
+------------------------------------------------------------------+
|                      DATA ZONE                                    |
|                                                                   |
|  +------------------+          +------------------+               |
|  |    PostgreSQL    |          |      Redis       |               |
|  |    (Primary)     |          |    (Primary)     |               |
|  +--------+---------+          +------------------+               |
|           |                                                       |
|           v                                                       |
|  +------------------+                                             |
|  |    PostgreSQL    |                                             |
|  |    (Standby)     |                                             |
|  +------------------+                                             |
|                                                                   |
+------------------------------------------------------------------+
```

### 5.2 Specifications Materielles

#### 5.2.1 Environnement Production

| Composant | Specification | Quantite |
|-----------|---------------|----------|
| **App Server** | 4 vCPU, 8 GB RAM, 50 GB SSD | 2-3 |
| **Database** | 4 vCPU, 16 GB RAM, 200 GB SSD | 1 Primary + 1 Standby |
| **Redis** | 2 vCPU, 4 GB RAM | 1 |
| **Load Balancer** | 2 vCPU, 4 GB RAM | 1 |

#### 5.2.2 Environnement Staging

| Composant | Specification | Quantite |
|-----------|---------------|----------|
| **All-in-one** | 4 vCPU, 8 GB RAM, 100 GB SSD | 1 |

### 5.3 Reseau

```
+------------------------------------------------------------------+
|                     VLAN Architecture                             |
+------------------------------------------------------------------+
|                                                                   |
|  VLAN 10 - DMZ (10.0.10.0/24)                                    |
|  +------------------+                                             |
|  | nginx-lb         | 10.0.10.10                                 |
|  +------------------+                                             |
|                                                                   |
|  VLAN 20 - Application (10.0.20.0/24)                            |
|  +------------------+  +------------------+                       |
|  | app-server-1     |  | app-server-2     |                       |
|  | 10.0.20.11       |  | 10.0.20.12       |                       |
|  +------------------+  +------------------+                       |
|                                                                   |
|  VLAN 30 - Data (10.0.30.0/24)                                   |
|  +------------------+  +------------------+                       |
|  | postgres-primary | | redis            |                       |
|  | 10.0.30.11       | | 10.0.30.21       |                       |
|  +------------------+  +------------------+                       |
|  +------------------+                                             |
|  | postgres-standby |                                             |
|  | 10.0.30.12       |                                             |
|  +------------------+                                             |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 6. Patterns et Principes

### 6.1 Patterns Architecturaux

#### 6.1.1 Repository Pattern

```python
# Separation acces donnees / logique metier

class TrainPassRepository:
    """Abstraction de l'acces aux donnees TrainPass."""

    def __init__(self, session):
        self.session = session

    def get_by_id(self, id: int) -> TrainPass:
        return self.session.query(TrainPass).get(id)

    def find_pending(self, limit: int = 20) -> List[TrainPass]:
        return self.session.query(TrainPass)\
            .filter(TrainPass.status == 'pending')\
            .order_by(TrainPass.passage_time.desc())\
            .limit(limit)\
            .all()

    def save(self, train_pass: TrainPass) -> TrainPass:
        self.session.add(train_pass)
        self.session.commit()
        return train_pass
```

#### 6.1.2 Service Layer Pattern

```python
# Orchestration de la logique metier

class TrainPassService:
    """Logique metier pour les passages de trains."""

    def __init__(self, repository: TrainPassRepository,
                 alert_service: AlertService):
        self.repository = repository
        self.alert_service = alert_service

    def confirm_train_pass(self, train_pass_id: int,
                           user_id: int, notes: str) -> TrainPass:
        train_pass = self.repository.get_by_id(train_pass_id)
        if not train_pass:
            raise NotFoundError("Train pass not found")

        # Verifier les alertes non acquittees
        pending_alerts = self.alert_service.get_pending_for_train(train_pass_id)
        if pending_alerts:
            raise BusinessError("Cannot confirm with pending alerts")

        train_pass.status = 'confirmed'
        train_pass.confirmed_by = user_id
        train_pass.confirmed_at = datetime.utcnow()

        return self.repository.save(train_pass)
```

#### 6.1.3 Factory Pattern

```python
# Creation d'objets complexes

def create_app(config_name: str = None) -> Flask:
    """Application factory pattern."""

    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    redis_client.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.modules.auth import auth_bp
    from app.modules.train_passes import train_passes_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(train_passes_bp, url_prefix='/api/v1/train-passes')

    # Register error handlers
    register_error_handlers(app)

    return app
```

### 6.2 Principes SOLID

| Principe | Application |
|----------|-------------|
| **S**ingle Responsibility | Chaque classe/module a une seule raison de changer |
| **O**pen/Closed | Extensions via heritage/composition, pas modification |
| **L**iskov Substitution | Interfaces respectees par implementations |
| **I**nterface Segregation | Interfaces specifiques plutot que generiques |
| **D**ependency Inversion | Injection de dependances via constructeurs |

### 6.3 Principes de Design

#### 6.3.1 Separation of Concerns

```
Request -> Controller -> Service -> Repository -> Database
                |
                v
           Validation
                |
                v
          Business Logic
                |
                v
           Data Access
```

#### 6.3.2 Don't Repeat Yourself (DRY)

```python
# Common decorators
@require_auth
@require_role('operator')
def confirm_action(id):
    ...

# Shared validation
class ConfirmationSchema(Schema):
    notes = fields.String(required=False, validate=Length(max=500))
```

#### 6.3.3 Keep It Simple (KISS)

- Pas d'abstraction prematuree
- Solutions directes preferees
- Code lisible > code "clever"

---

## 7. Vues Architecturales

### 7.1 Vue Cas d'Utilisation

```
+------------------------------------------------------------------+
|                    VUE CAS D'UTILISATION                          |
+------------------------------------------------------------------+
|                                                                   |
|    +-------------+                                                |
|    |  Operateur  |                                                |
|    +------+------+                                                |
|           |                                                       |
|           +---> [UC-01] Se connecter                             |
|           |                                                       |
|           +---> [UC-02] Consulter passages trains                |
|           |         |                                             |
|           |         +---> [UC-03] Voir detail wagon              |
|           |                   |                                   |
|           |                   +---> [UC-04] Analyser ressorts    |
|           |                                                       |
|           +---> [UC-05] Confirmer passage                        |
|           |                                                       |
|           +---> [UC-06] Gerer alertes                            |
|                                                                   |
|    +-------------+                                                |
|    |    Admin    |                                                |
|    +------+------+                                                |
|           |                                                       |
|           +---> [UC-07] Gerer utilisateurs                       |
|           |                                                       |
|           +---> [UC-08] Consulter audit logs                     |
|                                                                   |
+------------------------------------------------------------------+
```

### 7.2 Vue Logique

```
+------------------------------------------------------------------+
|                       VUE LOGIQUE                                 |
+------------------------------------------------------------------+
|                                                                   |
|  +--------------------------+     +--------------------------+   |
|  |    Presentation Layer    |     |    Presentation Layer    |   |
|  |                          |     |                          |   |
|  |  +--------------------+  |     |  +--------------------+  |   |
|  |  |  Web Templates     |  |     |  |   REST API         |  |   |
|  |  |  (Jinja2 + Vue.js) |  |     |  |   (JSON)           |  |   |
|  |  +--------------------+  |     |  +--------------------+  |   |
|  +--------------------------+     +--------------------------+   |
|              |                               |                    |
|              +---------------+---------------+                    |
|                              |                                    |
|                              v                                    |
|                 +--------------------------+                      |
|                 |    Application Layer     |                      |
|                 |                          |                      |
|                 |  +--------------------+  |                      |
|                 |  |  Controllers       |  |                      |
|                 |  |  (Flask Routes)    |  |                      |
|                 |  +--------------------+  |                      |
|                 |            |             |                      |
|                 |            v             |                      |
|                 |  +--------------------+  |                      |
|                 |  |  Services          |  |                      |
|                 |  |  (Business Logic)  |  |                      |
|                 |  +--------------------+  |                      |
|                 +--------------------------+                      |
|                              |                                    |
|                              v                                    |
|                 +--------------------------+                      |
|                 |      Domain Layer        |                      |
|                 |                          |                      |
|                 |  +--------------------+  |                      |
|                 |  |  Entities          |  |                      |
|                 |  |  (Domain Models)   |  |                      |
|                 |  +--------------------+  |                      |
|                 +--------------------------+                      |
|                              |                                    |
|                              v                                    |
|                 +--------------------------+                      |
|                 |   Infrastructure Layer   |                      |
|                 |                          |                      |
|                 |  +--------+ +--------+   |                      |
|                 |  | Repos  | | Cache  |   |                      |
|                 |  +--------+ +--------+   |                      |
|                 +--------------------------+                      |
|                                                                   |
+------------------------------------------------------------------+
```

### 7.3 Vue Processus

```
+------------------------------------------------------------------+
|                      VUE PROCESSUS                                |
+------------------------------------------------------------------+
|                                                                   |
|  Processus Principal: Inspection Train                           |
|  ================================================                 |
|                                                                   |
|  [Start]                                                          |
|     |                                                             |
|     v                                                             |
|  +------------------+                                             |
|  | Reception donnees|  <-- Systeme cameras                        |
|  | ressorts         |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +------------------+     +------------------+                    |
|  | Analyse seuils   |---->| Creation alerte  |                    |
|  | (automatique)    |     | (si hors norme)  |                    |
|  +--------+---------+     +------------------+                    |
|           |                        |                              |
|           v                        v                              |
|  +------------------+     +------------------+                    |
|  | Affichage System |     | Notification     |                    |
|  | View (operateur) |     | temps reel       |                    |
|  +--------+---------+     +------------------+                    |
|           |                                                       |
|           v                                                       |
|  +------------------+                                             |
|  | Selection wagon  |                                             |
|  | par operateur    |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +------------------+                                             |
|  | Affichage Car    |                                             |
|  | View (ressorts)  |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           +--------+--------+                                     |
|           |                 |                                     |
|           v                 v                                     |
|  +------------------+ +------------------+                        |
|  | Ressorts OK      | | Alertes a gerer  |                        |
|  +--------+---------+ +--------+---------+                        |
|           |                    |                                  |
|           |                    v                                  |
|           |           +------------------+                        |
|           |           | Acquittement     |                        |
|           |           | alerte           |                        |
|           |           +--------+---------+                        |
|           |                    |                                  |
|           +--------+-----------+                                  |
|                    |                                              |
|                    v                                              |
|           +------------------+                                    |
|           | Confirmation     |                                    |
|           | passage train    |                                    |
|           +--------+---------+                                    |
|                    |                                              |
|                    v                                              |
|                 [End]                                             |
|                                                                   |
+------------------------------------------------------------------+
```

### 7.4 Vue Developpement

```
+------------------------------------------------------------------+
|                    VUE DEVELOPPEMENT                              |
+------------------------------------------------------------------+
|                                                                   |
|  Repository Structure                                             |
|  ====================                                             |
|                                                                   |
|  vicore-v2/                                                       |
|  |                                                                |
|  +-- app/                      # Code source application          |
|  |   +-- modules/              # Modules fonctionnels            |
|  |   +-- common/               # Code partage                    |
|  |   +-- templates/            # Templates Jinja2                |
|  |   +-- static/               # Assets frontend                 |
|  |                                                                |
|  +-- tests/                    # Tests                           |
|  |   +-- unit/                 # Tests unitaires                 |
|  |   +-- integration/          # Tests integration               |
|  |   +-- e2e/                  # Tests end-to-end                |
|  |                                                                |
|  +-- migrations/               # Migrations Alembic              |
|  |                                                                |
|  +-- scripts/                  # Scripts utilitaires             |
|  |                                                                |
|  +-- docs/                     # Documentation                   |
|  |                                                                |
|  +-- docker/                   # Configuration Docker            |
|  |   +-- Dockerfile                                              |
|  |   +-- docker-compose.yml                                      |
|  |                                                                |
|  +-- .github/                  # CI/CD workflows                 |
|  |                                                                |
|  +-- requirements/             # Dependencies Python             |
|      +-- base.txt                                                 |
|      +-- dev.txt                                                  |
|      +-- prod.txt                                                 |
|                                                                   |
+------------------------------------------------------------------+
```

### 7.5 Vue Physique

```
+------------------------------------------------------------------+
|                      VUE PHYSIQUE                                 |
+------------------------------------------------------------------+
|                                                                   |
|               +-----------------------------------+               |
|               |           CLOUD / DC              |               |
|               +-----------------------------------+               |
|                              |                                    |
|        +---------------------+---------------------+              |
|        |                     |                     |              |
|        v                     v                     v              |
|  +-----------+       +-----------+         +-----------+          |
|  |  Region 1 |       |  Region 2 |         |  Region 3 |          |
|  |  (Primary)|       | (Standby) |         |   (DR)    |          |
|  +-----------+       +-----------+         +-----------+          |
|        |                                                          |
|        v                                                          |
|  +-----------------------------------+                            |
|  |        Kubernetes Cluster         |                            |
|  +-----------------------------------+                            |
|  |                                   |                            |
|  |  +-------------+ +-------------+  |                            |
|  |  |  Namespace  | |  Namespace  |  |                            |
|  |  |   vicore    | |  monitoring |  |                            |
|  |  +-------------+ +-------------+  |                            |
|  |        |               |          |                            |
|  |        v               v          |                            |
|  |  +-----------+   +-----------+    |                            |
|  |  | vicore-api|   | prometheus|    |                            |
|  |  | (x3 pods) |   +-----------+    |                            |
|  |  +-----------+   +-----------+    |                            |
|  |  +-----------+   |  grafana  |    |                            |
|  |  |   nginx   |   +-----------+    |                            |
|  |  |  ingress  |                    |                            |
|  |  +-----------+                    |                            |
|  |                                   |                            |
|  +-----------------------------------+                            |
|                                                                   |
|  +-----------------------------------+                            |
|  |        Managed Services           |                            |
|  +-----------------------------------+                            |
|  |                                   |                            |
|  |  +-----------+   +-----------+    |                            |
|  |  | PostgreSQL|   |   Redis   |    |                            |
|  |  | (managed) |   | (managed) |    |                            |
|  |  +-----------+   +-----------+    |                            |
|  |                                   |                            |
|  +-----------------------------------+                            |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 8. Qualite et Attributs

### 8.1 Attributs de Qualite

| Attribut | Exigence | Mesure |
|----------|----------|--------|
| **Performance** | < 200ms P95 | Monitoring APM |
| **Disponibilite** | 99.9% | Uptime monitoring |
| **Scalabilite** | 100 users simultanes | Load testing |
| **Securite** | OWASP Top 10 | Security audit |
| **Maintenabilite** | Code coverage > 80% | CI/CD metrics |
| **Testabilite** | Tests automatises | Test reports |

### 8.2 Strategies de Qualite

#### 8.2.1 Performance

```
Strategies:
1. Cache Redis pour donnees frequentes
2. Indexes base de donnees optimises
3. Pagination systematique des listes
4. Lazy loading frontend
5. CDN pour assets statiques
```

#### 8.2.2 Disponibilite

```
Strategies:
1. Load balancing multi-instances
2. Health checks automatiques
3. Auto-restart containers
4. Database replication
5. Monitoring et alerting
```

#### 8.2.3 Securite

```
Strategies:
1. Authentification SSO Eurotunnel
2. Autorisation RBAC
3. Chiffrement TLS
4. Audit logging
5. Rate limiting
6. Input validation
```

### 8.3 Metriques Architecturales

| Metrique | Cible | Alerte |
|----------|-------|--------|
| Latence API P50 | < 50ms | > 100ms |
| Latence API P95 | < 200ms | > 500ms |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 85% |
| Memory Usage | < 80% | > 90% |
| DB Connections | < 80% pool | > 90% pool |
| Cache Hit Rate | > 90% | < 70% |

---

## 9. Risques et Mitigations

### 9.1 Risques Techniques

| ID | Risque | Probabilite | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RT-01 | Surcharge base de donnees | Moyenne | Eleve | Read replicas, cache |
| RT-02 | Perte de donnees | Faible | Critique | Backups, replication |
| RT-03 | Faille de securite | Moyenne | Critique | Audits, WAF, pentests |
| RT-04 | Indisponibilite service | Moyenne | Eleve | HA, monitoring |
| RT-05 | Performance degradee | Moyenne | Moyen | Profiling, optimisation |

### 9.2 Risques Projet

| ID | Risque | Probabilite | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| RP-01 | Depart ressource cle | Moyenne | Eleve | Documentation, pair programming |
| RP-02 | Changement requirements | Elevee | Moyen | Architecture flexible |
| RP-03 | Retard integration externe | Moyenne | Moyen | Mocks, contrats API |
| RP-04 | Dette technique | Elevee | Moyen | Code reviews, refactoring planifie |

### 9.3 Plan de Continuite

```
Scenario: Panne complete data center
==========================================

RTO (Recovery Time Objective): 4 heures
RPO (Recovery Point Objective): 15 minutes

Etapes:
1. Detection automatique (monitoring)
2. Basculement DNS vers site DR
3. Activation standby database
4. Verification integrite donnees
5. Restauration services
6. Validation fonctionnelle
7. Communication utilisateurs
```

---

## Annexes

### A. Glossaire Architecture

| Terme | Definition |
|-------|------------|
| **ADR** | Architecture Decision Record |
| **HA** | High Availability |
| **DR** | Disaster Recovery |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |
| **RBAC** | Role-Based Access Control |
| **APM** | Application Performance Monitoring |

### B. References

| Document | Description |
|----------|-------------|
| SRS-VICORE-V2 | Specification des Exigences |
| SFG-VICORE-V2 | Specification Fonctionnelle |
| STB-VICORE-V2 | Specification Technique |
| The Twelve-Factor App | Methodologie applications cloud |
| OWASP Top 10 | Standards securite web |

---

*Document genere le 2026-01-18*
*Version: 1.0*
*Statut: En attente de validation*
