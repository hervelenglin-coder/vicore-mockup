# STB - Specification Technique de Besoins
## VICORE V2 - VIsualisation COntrole REssorts

| Champ | Valeur |
|-------|--------|
| **Version** | 1.0 |
| **Date** | 2026-01-18 |
| **Statut** | En cours de redaction |
| **Auteur** | Equipe Technique |
| **Validation** | A valider |

---

## Historique des Modifications

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-01-18 | Equipe Technique | Creation initiale |

---

## Table des Matieres

1. [Introduction](#1-introduction)
2. [Architecture Technique](#2-architecture-technique)
3. [Stack Technologique](#3-stack-technologique)
4. [Modele de Donnees](#4-modele-de-donnees)
5. [Specification des APIs](#5-specification-des-apis)
6. [Securite](#6-securite)
7. [Performance et Scalabilite](#7-performance-et-scalabilite)
8. [Infrastructure et Deploiement](#8-infrastructure-et-deploiement)
9. [Interfaces Externes](#9-interfaces-externes)
10. [Annexes](#10-annexes)

---

## 1. Introduction

### 1.1 Objet du Document

Ce document decrit les specifications techniques du systeme VICORE V2. Il definit l'architecture, les choix technologiques, le modele de donnees et les specifications detaillees des interfaces.

### 1.2 Portee

Ce document couvre:
- L'architecture logicielle et materielle
- Les technologies selectionnees
- Le modele de donnees complet
- Les specifications des APIs REST
- Les exigences de securite et performance

### 1.3 Documents de Reference

| Reference | Document |
|-----------|----------|
| SRS-VICORE-V2 | Specification des Exigences |
| SFG-VICORE-V2 | Specification Fonctionnelle |
| DAT-VICORE-V2 | Dossier d'Architecture Technique |

### 1.4 Glossaire Technique

| Terme | Definition |
|-------|------------|
| **API** | Application Programming Interface |
| **REST** | Representational State Transfer |
| **SSO** | Single Sign-On |
| **SAML** | Security Assertion Markup Language |
| **OAuth2** | Open Authorization 2.0 |
| **ORM** | Object-Relational Mapping |
| **WSGI** | Web Server Gateway Interface |
| **SSE** | Server-Sent Events |
| **Redis** | Remote Dictionary Server (cache en memoire) |

---

## 2. Architecture Technique

### 2.1 Vue d'Ensemble

```
+------------------------------------------------------------------+
|                        NAVIGATEUR WEB                              |
|                    (Chrome, Firefox, Edge)                         |
+------------------------------------------------------------------+
                              |
                              | HTTPS (Port 443)
                              v
+------------------------------------------------------------------+
|                      REVERSE PROXY                                 |
|                        (Nginx)                                     |
|  - SSL Termination                                                 |
|  - Load Balancing                                                  |
|  - Static Files Serving                                            |
|  - Rate Limiting                                                   |
+------------------------------------------------------------------+
                              |
                              | HTTP (Port 8000)
                              v
+------------------------------------------------------------------+
|                    SERVEUR WSGI                                    |
|                      (Gunicorn)                                    |
|  - Workers: 4 (2 * CPU + 1)                                        |
|  - Worker Class: sync                                              |
|  - Timeout: 30s                                                    |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                  APPLICATION FLASK                                 |
|                                                                    |
|  +------------------+  +------------------+  +------------------+  |
|  |   Controllers    |  |    Services      |  |   Repositories   |  |
|  |   (Routes)       |  |   (Business)     |  |   (Data Access)  |  |
|  +------------------+  +------------------+  +------------------+  |
|                                                                    |
|  +------------------+  +------------------+  +------------------+  |
|  |     Models       |  |    Utilities     |  |   Middlewares    |  |
|  |   (SQLAlchemy)   |  |   (Helpers)      |  |   (Auth, CORS)   |  |
|  +------------------+  +------------------+  +------------------+  |
+------------------------------------------------------------------+
           |                      |                      |
           v                      v                      v
+------------------+  +------------------+  +------------------+
|    PostgreSQL    |  |      Redis       |  |   File System    |
|    (Database)    |  |     (Cache)      |  |    (Logs)        |
+------------------+  +------------------+  +------------------+
```

### 2.2 Architecture en Couches

```
+------------------------------------------------------------------+
|                    COUCHE PRESENTATION                             |
|-------------------------------------------------------------------|
|  - Templates Jinja2                                                |
|  - CSS (Dark Tech Theme)                                           |
|  - JavaScript (Vue.js + Element UI)                                |
|  - Assets statiques                                                |
+------------------------------------------------------------------+
                              |
+------------------------------------------------------------------+
|                    COUCHE CONTROLEUR                               |
|-------------------------------------------------------------------|
|  - Routes Flask (Blueprints)                                       |
|  - Validation des entrees                                          |
|  - Gestion des sessions                                            |
|  - Serialisation JSON                                              |
+------------------------------------------------------------------+
                              |
+------------------------------------------------------------------+
|                    COUCHE SERVICE                                  |
|-------------------------------------------------------------------|
|  - Logique metier                                                  |
|  - Orchestration des operations                                    |
|  - Regles de gestion                                               |
|  - Transactions                                                    |
+------------------------------------------------------------------+
                              |
+------------------------------------------------------------------+
|                    COUCHE ACCES DONNEES                            |
|-------------------------------------------------------------------|
|  - Repositories (Pattern Repository)                               |
|  - ORM SQLAlchemy                                                  |
|  - Queries optimisees                                              |
|  - Connection pooling                                              |
+------------------------------------------------------------------+
                              |
+------------------------------------------------------------------+
|                    COUCHE DONNEES                                  |
|-------------------------------------------------------------------|
|  - PostgreSQL (donnees persistantes)                               |
|  - Redis (cache, sessions)                                         |
|  - File System (logs, exports)                                     |
+------------------------------------------------------------------+
```

### 2.3 Composants Principaux

| Composant | Responsabilite | Technologie |
|-----------|---------------|-------------|
| **Web Server** | Reverse proxy, SSL, load balancing | Nginx 1.24+ |
| **App Server** | Execution Python WSGI | Gunicorn 21+ |
| **Application** | Logique applicative | Flask 3.0+ |
| **ORM** | Mapping objet-relationnel | SQLAlchemy 2.0+ |
| **Database** | Persistance des donnees | PostgreSQL 16+ |
| **Cache** | Cache applicatif, sessions | Redis 7+ |
| **Frontend** | Interface utilisateur | Vue.js 2.7 + Element UI |

---

## 3. Stack Technologique

### 3.1 Backend

#### 3.1.1 Langage et Framework

| Element | Choix | Version | Justification |
|---------|-------|---------|---------------|
| **Langage** | Python | 3.11+ | Performance, ecosysteme riche, maintenabilite |
| **Framework Web** | Flask | 3.0+ | Legerete, flexibilite, maturite |
| **WSGI Server** | Gunicorn | 21+ | Production-ready, stable |
| **ORM** | SQLAlchemy | 2.0+ | Puissance, flexibilite, async support |

#### 3.1.2 Dependances Backend

```txt
# Framework
Flask==3.0.0
Flask-Login==0.6.3
Flask-SAML2==0.4.0
Flask-WTF==1.2.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-CORS==4.0.0

# Base de donnees
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1

# Securite
python-dotenv==1.0.0
bcrypt==4.1.1
python3-saml==1.16.0
cryptography==41.0.7

# Validation
marshmallow==3.20.1
email-validator==2.1.0

# Internationalisation
Flask-Babel==4.0.0
Babel==2.14.0

# Utilitaires
requests==2.31.0
python-dateutil==2.8.2

# Monitoring
prometheus-flask-exporter==0.23.0

# Tests
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0
```

### 3.2 Frontend

#### 3.2.1 Technologies UI

| Element | Choix | Version | Justification |
|---------|-------|---------|---------------|
| **Framework JS** | Vue.js | 2.7.x | Integration simple avec Flask |
| **UI Components** | Element UI | 2.15.x | Composants professionnels |
| **CSS** | CSS3 Custom | - | Theme Dark Tech personnalise |
| **Icons** | Font Awesome | 6.x | Iconographie complete |
| **Fonts** | Inter | - | Lisibilite, modernite |

#### 3.2.2 Structure CSS

```
static/
├── css/
│   ├── design-system.css      # Variables et base
│   ├── dark-tech-theme.css    # Theme principal
│   ├── components/
│   │   ├── buttons.css
│   │   ├── cards.css
│   │   ├── forms.css
│   │   ├── modals.css
│   │   └── tables.css
│   └── pages/
│       ├── login.css
│       ├── system-view.css
│       └── car-view.css
├── js/
│   ├── app.js
│   ├── api.js
│   └── components/
└── fonts/
    └── inter/
```

#### 3.2.3 Internationalisation Frontend

```javascript
// Configuration i18n (Vue I18n)
const i18n = {
    locale: getBrowserLanguage(),  // Langue detectee depuis le navigateur
    fallbackLocale: 'en',          // Langue de repli
    messages: {
        fr: { /* traductions francaises */ },
        en: { /* traductions anglaises */ }
    }
}

// Detection de la langue du navigateur
function getBrowserLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    // Si la langue du navigateur est francaise, utiliser FR, sinon EN
    return lang.toLowerCase().startsWith('fr') ? 'fr' : 'en';
}

// Persistance de la preference utilisateur
function setLanguage(lang) {
    i18n.locale = lang;
    localStorage.setItem('vicore-lang', lang);
    // Si utilisateur connecte, sauvegarder en base
    if (currentUser) {
        api.updateUserPreferences({ locale: lang });
    }
}
```

**Structure des fichiers de traduction:**
```
static/
├── locales/
│   ├── fr.json    # Traductions francaises
│   └── en.json    # Traductions anglaises
```

**Detection de langue:**
1. Verifier `localStorage` pour une preference sauvegardee
2. Sinon, detecter `navigator.language`
3. Si langue FR -> francais par defaut
4. Sinon -> anglais par defaut

### 3.3 Base de Donnees

#### 3.3.1 PostgreSQL Configuration

```ini
# postgresql.conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 768MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 7864kB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

#### 3.3.2 Redis Configuration

```ini
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
```

### 3.4 Infrastructure

| Element | Choix | Specification |
|---------|-------|---------------|
| **OS** | Linux | Ubuntu 22.04 LTS |
| **Container** | Docker | 24.0+ |
| **Orchestration** | Docker Compose | 2.23+ |
| **Reverse Proxy** | Nginx | 1.24+ |
| **SSL** | Let's Encrypt | Auto-renew |

---

## 4. Modele de Donnees

### 4.1 Modele Conceptuel de Donnees (MCD)

```
+------------------+       +------------------+       +------------------+
|      USER        |       |   TRAIN_PASS     |       |       CAR        |
+------------------+       +------------------+       +------------------+
| PK: id           |       | PK: id           |       | PK: id           |
| username         |       | passage_time     |       | FK: train_pass_id|
| password_hash    |       | direction        |       | position         |
| role             |       | train_number     |       | car_type         |
| is_active        |       | status           |       | status           |
| created_at       |       | created_at       |       | created_at       |
| last_login       |       | updated_at       |       | updated_at       |
+------------------+       +------------------+       +------------------+
        |                         |                         |
        |                         | 1                       | 1
        |                         |                         |
        v                    +----+----+                    |
+------------------+         |         |                    |
|  CONFIRMATION    |---------+         +--------------------+
+------------------+                   |
| PK: id           |                   | n
| FK: user_id      |                   v
| FK: train_pass_id|         +------------------+
| FK: car_id       |         |      SPRING      |
| confirmation_type|         +------------------+
| confirmed_at     |         | PK: id           |
| notes            |         | FK: car_id       |
+------------------+         | position         |
                             | side             |
                             | height_mm        |
                             | status           |
                             | created_at       |
                             +------------------+
                                      |
                                      | n
                                      v
                             +------------------+
                             |   SPRING_ALERT   |
                             +------------------+
                             | PK: id           |
                             | FK: spring_id    |
                             | alert_type       |
                             | severity         |
                             | message          |
                             | is_acknowledged  |
                             | created_at       |
                             +------------------+
```

### 4.2 Modele Logique de Donnees (MLD)

#### 4.2.1 Table `users`

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    sso_id          VARCHAR(100) NOT NULL UNIQUE,  -- Identifiant SSO Eurotunnel
    username        VARCHAR(50) NOT NULL UNIQUE,
    email           VARCHAR(100),
    display_name    VARCHAR(100),
    role            VARCHAR(20) NOT NULL DEFAULT 'operator',
    locale          VARCHAR(5) NOT NULL DEFAULT 'fr',  -- Preference de langue (fr, en)
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP,

    CONSTRAINT chk_role CHECK (role IN ('admin', 'operator', 'viewer')),
    CONSTRAINT chk_locale CHECK (locale IN ('fr', 'en'))
);

CREATE INDEX idx_users_sso_id ON users(sso_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**Note:** Les utilisateurs sont crees automatiquement lors de leur premiere connexion SSO. Le role est determine par le mapping des groupes SSO Eurotunnel.

#### 4.2.2 Table `installations`

```sql
-- Note: Table pour la configuration dynamique des equipements
-- Les noms des equipements (Voie D, Voie E, etc.) sont configurables sans modification du code
CREATE TABLE installations (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(20) NOT NULL UNIQUE,     -- Code technique (ex: 'VOIE_D')
    name            VARCHAR(50) NOT NULL,            -- Nom affiche (ex: 'Voie D')
    description     VARCHAR(255),
    location        VARCHAR(50),                     -- Localisation geographique
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    display_order   INTEGER NOT NULL DEFAULT 0,
    color_code      VARCHAR(7),                      -- Code couleur hex pour l'UI
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Donnees initiales
INSERT INTO installations (code, name, location, display_order, color_code) VALUES
    ('VOIE_D', 'Voie D', 'Folkestone', 1, '#06b6d4'),
    ('VOIE_E', 'Voie E', 'Coquelles', 2, '#8b5cf6');

CREATE INDEX idx_installations_is_active ON installations(is_active);
```

#### 4.2.3 Table `train_passes`

```sql
CREATE TABLE train_passes (
    id                SERIAL PRIMARY KEY,
    installation_id   INTEGER REFERENCES installations(id),
    passage_time      TIMESTAMP NOT NULL,
    direction         VARCHAR(20) NOT NULL,          -- Direction geographique
    train_direction   VARCHAR(10) NOT NULL DEFAULT 'normal', -- Sens de circulation: 'normal' (Sens normal, sortie tunnel vers quais) ou 'tiroir' (En tiroir, quais vers tunnel)
    train_number      VARCHAR(20),
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_direction CHECK (direction IN ('france_uk', 'uk_france')),
    CONSTRAINT chk_train_direction CHECK (train_direction IN ('normal', 'tiroir')),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'in_progress', 'confirmed', 'alert'))
);

CREATE INDEX idx_train_passes_passage_time ON train_passes(passage_time DESC);
CREATE INDEX idx_train_passes_status ON train_passes(status);
CREATE INDEX idx_train_passes_direction ON train_passes(direction);
CREATE INDEX idx_train_passes_installation ON train_passes(installation_id);
```

#### 4.2.3 Table `cars`

```sql
CREATE TABLE cars (
    id              SERIAL PRIMARY KEY,
    train_pass_id   INTEGER NOT NULL REFERENCES train_passes(id) ON DELETE CASCADE,
    position        INTEGER NOT NULL,
    car_type        VARCHAR(20) NOT NULL DEFAULT 'porteur',
    rfid            VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Note: Types de wagon: locomotive (Loco), chargeur, porteur
    CONSTRAINT chk_car_type CHECK (car_type IN ('locomotive', 'chargeur', 'porteur')),
    CONSTRAINT chk_car_status CHECK (status IN ('pending', 'ok', 'warning', 'alert')),
    CONSTRAINT uq_train_position UNIQUE (train_pass_id, position)
);

CREATE INDEX idx_cars_train_pass_id ON cars(train_pass_id);
CREATE INDEX idx_cars_status ON cars(status);
CREATE INDEX idx_cars_rfid ON cars(rfid);
```

#### 4.2.4 Table `springs`

```sql
CREATE TABLE springs (
    id              SERIAL PRIMARY KEY,
    car_id          INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE,
    bogie           INTEGER NOT NULL,          -- 1 (Avant/Leading) ou 2 (Arriere/Trailing)
    axle            INTEGER NOT NULL,          -- 1 ou 2 (essieu dans le bogie)
    side            VARCHAR(10) NOT NULL,      -- 'left' (Gauche) ou 'right' (Droit)
    position        VARCHAR(10) NOT NULL,      -- 'leading' (Menant) ou 'trailing' (Mene)
    conf_code       INTEGER NOT NULL DEFAULT 1,-- 0=confirme, 1=OK, 2=incertain, 3=anomalie
    height_mm       DECIMAL(6,2),
    status          VARCHAR(20) NOT NULL DEFAULT 'unknown',
    image_path      VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Note: Nomenclature ressorts
    -- Menant (Leading): Ressort avant la roue dans le sens de marche
    -- Mene (Trailing): Ressort apres la roue dans le sens de marche
    -- Total: 16 ressorts par wagon (2 bogies x 2 essieux x 2 cotes x 2 positions)
    CONSTRAINT chk_bogie CHECK (bogie IN (1, 2)),
    CONSTRAINT chk_axle CHECK (axle IN (1, 2)),
    CONSTRAINT chk_side CHECK (side IN ('left', 'right')),
    CONSTRAINT chk_position CHECK (position IN ('leading', 'trailing')),
    CONSTRAINT chk_spring_status CHECK (status IN ('ok', 'warning', 'critical', 'unknown', 'confirmed')),
    CONSTRAINT uq_car_spring_position UNIQUE (car_id, bogie, axle, side, position)
);

CREATE INDEX idx_springs_car_id ON springs(car_id);
CREATE INDEX idx_springs_status ON springs(status);
CREATE INDEX idx_springs_conf_code ON springs(conf_code);
```

#### 4.2.5 Table `spring_alerts`

```sql
CREATE TABLE spring_alerts (
    id              SERIAL PRIMARY KEY,
    spring_id       INTEGER NOT NULL REFERENCES springs(id) ON DELETE CASCADE,
    alert_type      VARCHAR(50) NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    message         TEXT,
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_severity CHECK (severity IN ('info', 'warning', 'critical'))
);

CREATE INDEX idx_spring_alerts_spring_id ON spring_alerts(spring_id);
CREATE INDEX idx_spring_alerts_is_acknowledged ON spring_alerts(is_acknowledged);
CREATE INDEX idx_spring_alerts_severity ON spring_alerts(severity);
```

#### 4.2.6 Table `confirmations`

```sql
CREATE TABLE confirmations (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id),
    train_pass_id       INTEGER REFERENCES train_passes(id),
    car_id              INTEGER REFERENCES cars(id),
    spring_id           INTEGER REFERENCES springs(id),
    confirmation_type   VARCHAR(30) NOT NULL,
    confirmation_value  VARCHAR(20) NOT NULL,  -- 'present', 'missing', 'ok'
    confirmed_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_cancelled        BOOLEAN NOT NULL DEFAULT FALSE,
    notes               TEXT,

    CONSTRAINT chk_confirmation_type CHECK (
        confirmation_type IN ('train_pass_ok', 'car_ok', 'spring_present', 'spring_missing', 'alert_acknowledged')
    ),
    CONSTRAINT chk_confirmation_value CHECK (
        confirmation_value IN ('present', 'missing', 'ok', 'acknowledged')
    )
);

CREATE INDEX idx_confirmations_user_id ON confirmations(user_id);
CREATE INDEX idx_confirmations_train_pass_id ON confirmations(train_pass_id);
CREATE INDEX idx_confirmations_spring_id ON confirmations(spring_id);
CREATE INDEX idx_confirmations_confirmed_at ON confirmations(confirmed_at DESC);
CREATE INDEX idx_confirmations_not_cancelled ON confirmations(is_cancelled) WHERE is_cancelled = FALSE;
```

#### 4.2.7 Table `audit_logs`

```sql
CREATE TABLE audit_logs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    action          VARCHAR(50) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       INTEGER,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      VARCHAR(255),
    session_id      VARCHAR(64),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action CHECK (
        action IN ('login', 'logout', 'confirmation', 'cancellation', 'view', 'export', 'report_generated')
    )
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
-- Index pour les requetes de reporting par periode
CREATE INDEX idx_audit_logs_date_action ON audit_logs(created_at, action);
```

#### 4.2.8 Table `confirmation_cancellations`

```sql
CREATE TABLE confirmation_cancellations (
    id                  SERIAL PRIMARY KEY,
    confirmation_id     INTEGER NOT NULL REFERENCES confirmations(id),
    cancelled_by        INTEGER NOT NULL REFERENCES users(id),
    cancelled_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason              TEXT NOT NULL,
    notified_supervisor BOOLEAN NOT NULL DEFAULT FALSE,
    notification_sent_at TIMESTAMP,

    CONSTRAINT chk_reason_length CHECK (LENGTH(reason) >= 10)
);

CREATE INDEX idx_cancellations_confirmation_id ON confirmation_cancellations(confirmation_id);
CREATE INDEX idx_cancellations_cancelled_by ON confirmation_cancellations(cancelled_by);
CREATE INDEX idx_cancellations_cancelled_at ON confirmation_cancellations(cancelled_at DESC);
```

#### 4.2.9 Table `reports`

```sql
CREATE TABLE reports (
    id              VARCHAR(20) PRIMARY KEY,  -- Format: rpt_xxxxx
    created_by      INTEGER NOT NULL REFERENCES users(id),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    report_type     VARCHAR(20) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    filters         JSONB,
    summary_data    JSONB,
    file_path_pdf   VARCHAR(255),
    file_path_csv   VARCHAR(255),
    file_path_xlsx  VARCHAR(255),
    completed_at    TIMESTAMP,
    expires_at      TIMESTAMP,
    error_message   TEXT,

    CONSTRAINT chk_report_type CHECK (report_type IN ('summary', 'detailed')),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT chk_date_range CHECK (end_date >= start_date),
    CONSTRAINT chk_max_period CHECK (end_date - start_date <= 90)
);

CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_expires_at ON reports(expires_at);
```

### 4.3 Diagramme Entite-Relation

```
                                    +------------------+
                                    |      users       |
                                    +------------------+
                                    | id (PK)          |
                                    | username         |
                                    | password_hash    |
                                    | role             |
                                    | is_active        |
                                    +--------+---------+
                                             |
                         +-------------------+-------------------+
                         |                                       |
                         v                                       v
              +------------------+                     +------------------+
              |  confirmations   |                     |   audit_logs     |
              +------------------+                     +------------------+
              | id (PK)          |                     | id (PK)          |
              | user_id (FK)     |                     | user_id (FK)     |
              | train_pass_id(FK)|                     | action           |
              | car_id (FK)      |                     | entity_type      |
              | confirmation_type|                     | old_values       |
              +--------+---------+                     +------------------+
                       |
          +------------+------------+
          |                         |
          v                         v
+------------------+      +------------------+
|   train_passes   |      |       cars       |
+------------------+      +------------------+
| id (PK)          |<---->| id (PK)          |
| passage_time     |  1:n | train_pass_id(FK)|
| direction        |      | position         |
| train_number     |      | car_type         |
| status           |      | status           |
+------------------+      +--------+---------+
                                   |
                                   | 1:n
                                   v
                         +------------------+
                         |     springs      |
                         +------------------+
                         | id (PK)          |
                         | car_id (FK)      |
                         | position         |
                         | side             |
                         | height_mm        |
                         | status           |
                         +--------+---------+
                                  |
                                  | 1:n
                                  v
                         +------------------+
                         |  spring_alerts   |
                         +------------------+
                         | id (PK)          |
                         | spring_id (FK)   |
                         | alert_type       |
                         | severity         |
                         | message          |
                         +------------------+
```

---

## 5. Specification des APIs

### 5.1 Conventions Generales

#### 5.1.1 Format des URLs

```
Base URL: /api/v1

Conventions:
- Ressources au pluriel: /users, /train-passes, /cars
- Identifiants dans l'URL: /train-passes/{id}
- Actions via verbes HTTP: GET, POST, PUT, DELETE
- Filtrage via query params: /train-passes?status=pending&direction=france_uk
```

#### 5.1.2 Format des Reponses

**Succes (200, 201)**
```json
{
    "success": true,
    "data": { ... },
    "meta": {
        "timestamp": "2026-01-18T10:30:00Z",
        "request_id": "uuid"
    }
}
```

**Liste avec pagination**
```json
{
    "success": true,
    "data": [ ... ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "total_pages": 8
    }
}
```

**Erreur (4xx, 5xx)**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": [
            {
                "field": "username",
                "message": "Username is required"
            }
        ]
    }
}
```

### 5.2 Endpoints d'Authentification SSO

L'authentification est deleguee au SSO Eurotunnel. VICORE agit comme Service Provider (SP) SAML.

#### 5.2.1 GET /api/v1/auth/sso/login

**Description:** Initie le flux SSO en redirigeant vers le portail Eurotunnel.

**Response 302:**
Redirection vers `https://sso.eurotunnel.com/saml/login?SAMLRequest=...`

#### 5.2.2 POST /api/v1/auth/sso/callback

**Description:** Endpoint de callback appele par le SSO Eurotunnel apres authentification.

**Request:**
```
SAMLResponse={base64_encoded_response}
RelayState={original_url}
```

**Response 302 (Success):**
Redirection vers la page d'accueil VICORE avec session creee.

**Response 401 (Failure):**
```json
{
    "success": false,
    "error": {
        "code": "SSO_AUTH_FAILED",
        "message": "SSO authentication failed"
    }
}
```

#### 5.2.3 POST /api/v1/auth/logout

**Description:** Deconnecte l'utilisateur et initie le Single Logout SSO.

**Response 302:**
Redirection vers le SSO Eurotunnel pour Single Logout, puis retour a la page de login.

#### 5.2.4 GET /api/v1/auth/me

**Description:** Retourne les informations de l'utilisateur connecte.

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "sso_id": "john.doe@eurotunnel.com",
        "username": "jdoe",
        "display_name": "John Doe",
        "role": "operator",
        "last_login": "2026-01-18T08:00:00Z"
    }
}
```

#### 5.2.5 Configuration SSO

```python
SSO_CONFIG = {
    'strict': True,
    'debug': False,
    'sp': {
        'entityId': 'https://vicore.eurotunnel.com/saml/metadata',
        'assertionConsumerService': {
            'url': 'https://vicore.eurotunnel.com/api/v1/auth/sso/callback',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
        },
        'singleLogoutService': {
            'url': 'https://vicore.eurotunnel.com/api/v1/auth/sso/sls',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        }
    },
    'idp': {
        'entityId': 'https://sso.eurotunnel.com/saml/metadata',
        'singleSignOnService': {
            'url': 'https://sso.eurotunnel.com/saml/login',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        },
        'singleLogoutService': {
            'url': 'https://sso.eurotunnel.com/saml/logout',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
        }
    }
}

# Mapping des groupes SSO vers les roles VICORE
SSO_ROLE_MAPPING = {
    'VICORE_ADMINS': 'admin',
    'VICORE_OPERATORS': 'operator',
    'VICORE_VIEWERS': 'viewer'
}
```

#### 5.2.6 PUT /api/v1/auth/preferences

**Description:** Met a jour les preferences utilisateur (langue, etc.).

**Request:**
```json
{
    "locale": "en"
}
```

**Response 200:**
```json
{
    "success": true,
    "data": {
        "locale": "en",
        "message": "Preferences updated"
    }
}
```

**Regles:**
- `locale` doit etre "fr" ou "en"
- La preference est persistee en base de donnees
- Le changement est applique immediatement

### 5.3 Endpoints Train Passes

#### 5.3.1 GET /api/v1/train-passes

**Description:** Liste les passages de trains avec filtrage et pagination.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| page | int | Numero de page (defaut: 1) |
| per_page | int | Elements par page (defaut: 20, max: 100) |
| status | string | Filtre par statut |
| direction | string | Filtre par direction |
| date_from | datetime | Date de debut |
| date_to | datetime | Date de fin |

**Response 200:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "passage_time": "2026-01-18T10:30:00Z",
            "direction": "france_uk",
            "train_number": "ET-2024-001",
            "status": "pending",
            "cars_count": 12,
            "alerts_count": 0
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 45,
        "total_pages": 3
    }
}
```

#### 5.3.2 GET /api/v1/train-passes/{id}

**Description:** Retourne les details d'un passage de train.

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "passage_time": "2026-01-18T10:30:00Z",
        "direction": "france_uk",
        "train_number": "ET-2024-001",
        "status": "pending",
        "cars": [
            {
                "id": 1,
                "position": 1,
                "car_type": "locomotive",
                "status": "ok",
                "springs_status": "ok"
            },
            {
                "id": 2,
                "position": 2,
                "car_type": "passenger",
                "status": "warning",
                "springs_status": "warning"
            }
        ],
        "created_at": "2026-01-18T10:30:00Z",
        "updated_at": "2026-01-18T10:35:00Z"
    }
}
```

#### 5.3.3 POST /api/v1/train-passes/{id}/confirm

**Description:** Confirme un passage de train.

**Request:**
```json
{
    "notes": "All inspections completed successfully"
}
```

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "status": "confirmed",
        "confirmed_by": "operator1",
        "confirmed_at": "2026-01-18T11:00:00Z"
    }
}
```

### 5.4 Endpoints Cars

#### 5.4.1 GET /api/v1/train-passes/{train_pass_id}/cars

**Description:** Liste les wagons d'un passage de train.

**Response 200:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "position": 1,
            "car_type": "locomotive",
            "status": "ok",
            "springs": [
                {
                    "id": 1,
                    "position": 1,
                    "side": "left",
                    "height_mm": 145.5,
                    "status": "ok"
                }
            ]
        }
    ]
}
```

#### 5.4.2 GET /api/v1/cars/{id}

**Description:** Retourne les details d'un wagon avec ses ressorts.

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "train_pass_id": 1,
        "position": 2,
        "car_type": "passenger",
        "status": "warning",
        "springs": [
            {
                "id": 1,
                "position": 1,
                "side": "left",
                "height_mm": 145.5,
                "status": "ok",
                "alerts": []
            },
            {
                "id": 2,
                "position": 1,
                "side": "right",
                "height_mm": 132.0,
                "status": "warning",
                "alerts": [
                    {
                        "id": 1,
                        "type": "height_low",
                        "severity": "warning",
                        "message": "Spring height below threshold"
                    }
                ]
            }
        ]
    }
}
```

#### 5.4.3 POST /api/v1/cars/{id}/confirm

**Description:** Confirme l'inspection d'un wagon.

**Request:**
```json
{
    "notes": "Visual inspection completed"
}
```

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "status": "ok",
        "confirmed_by": "operator1",
        "confirmed_at": "2026-01-18T11:00:00Z"
    }
}
```

### 5.5 Endpoints Alerts

#### 5.5.1 GET /api/v1/alerts

**Description:** Liste les alertes avec filtrage.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| severity | string | Filtre par severite |
| is_acknowledged | bool | Filtre par statut |
| train_pass_id | int | Filtre par passage |

**Response 200:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "spring_id": 2,
            "car_id": 1,
            "train_pass_id": 1,
            "alert_type": "height_critical",
            "severity": "critical",
            "message": "Spring height critically low: 98mm",
            "is_acknowledged": false,
            "created_at": "2026-01-18T10:30:00Z"
        }
    ]
}
```

#### 5.5.2 POST /api/v1/alerts/{id}/acknowledge

**Description:** Acquitte une alerte.

**Request:**
```json
{
    "notes": "Reviewed and maintenance scheduled"
}
```

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "is_acknowledged": true,
        "acknowledged_by": "operator1",
        "acknowledged_at": "2026-01-18T11:00:00Z"
    }
}
```

### 5.6 Endpoints Systeme

#### 5.6.1 GET /api/v1/system/health

**Description:** Verifie l'etat de sante du systeme.

**Response 200:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "heartbeat": "healthy"
        },
        "uptime_seconds": 86400,
        "version": "2.0.0"
    }
}
```

#### 5.6.2 GET /api/v1/system/heartbeat

**Description:** Retourne l'etat du heartbeat avec les cameras.

**Response 200:**
```json
{
    "success": true,
    "data": {
        "heartbeat_status": "ok",
        "last_heartbeat": "2026-01-18T11:00:00Z",
        "cameras": [
            {
                "id": "CAM-01",
                "name": "Camera Tunnel Entry",
                "status": "online",
                "last_seen": "2026-01-18T11:00:00Z"
            }
        ]
    }
}
```

---

### 5.7 Endpoints Historique Ressorts

#### 5.7.1 GET /api/v1/springs/{spring_id}/history

**Description:** Retourne l'historique des photos d'un ressort sur plusieurs passages.

**Parametres Path:**
| Nom | Type | Description |
|-----|------|-------------|
| spring_id | string | Identifiant unique du ressort (format: wagon_bogie_axle_position) |

**Parametres Query:**
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| days | integer | Non | Nombre de jours (defaut: 30, max: 90) |
| limit | integer | Non | Nombre max de passages (defaut: 20, max: 50) |

**Response 200:**
```json
{
    "success": true,
    "data": {
        "spring_id": "W1234_B1_A1_L",
        "wagon_rfid": "1234",
        "bogie": 1,
        "axle": 1,
        "position": "L",
        "history": [
            {
                "train_pass_id": 5678,
                "train_code": "9N57",
                "passage_date": "2026-01-17T14:32:00Z",
                "conf_code": 1,
                "status": "ok",
                "image_url": "/api/v1/images/spring_5678_W1234_B1_A1_L.jpg",
                "confirmed_by": null
            },
            {
                "train_pass_id": 5650,
                "train_code": "2K18",
                "passage_date": "2026-01-15T09:15:00Z",
                "conf_code": 3,
                "status": "anomaly",
                "image_url": "/api/v1/images/spring_5650_W1234_B1_A1_L.jpg",
                "confirmed_by": "Jean Dupont",
                "confirmed_at": "2026-01-15T09:20:00Z",
                "confirmation": "present"
            }
        ],
        "total_passages": 12
    }
}
```

**Response 404:** Ressort non trouve.

---

### 5.8 Endpoints Annulation Confirmation

#### 5.8.1 POST /api/v1/springs/{spring_id}/cancel-confirmation

**Description:** Annule une confirmation de ressort manquant.

**Autorisation:** Operateur, Superviseur

**Parametres Path:**
| Nom | Type | Description |
|-----|------|-------------|
| spring_id | string | Identifiant unique du ressort |

**Request Body:**
```json
{
    "train_pass_id": 5678,
    "reason": "Le ressort a ete mal identifie, il est present sur les images alternatives."
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| train_pass_id | integer | Oui | ID du passage concerne |
| reason | string | Oui | Motif d'annulation (min 10 caracteres) |

**Response 200:**
```json
{
    "success": true,
    "data": {
        "spring_id": "W1234_B1_A1_L",
        "previous_status": "missing",
        "new_status": "pending",
        "cancelled_by": "Jean Dupont",
        "cancelled_at": "2026-01-17T15:00:00Z",
        "reason": "Le ressort a ete mal identifie, il est present sur les images alternatives.",
        "notification_sent": true
    }
}
```

**Response 400:**
- Passage trop ancien (> 24h)
- Motif trop court (< 10 caracteres)
- Ressort non confirme comme manquant

**Response 404:** Ressort ou passage non trouve.

---

### 5.9 Endpoints Audit Trail

#### 5.9.1 GET /api/v1/audit/operations

**Description:** Retourne l'historique des operations (audit trail).

**Autorisation:** Superviseur, Administrateur

**Parametres Query:**
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| start_date | date | Non | Date debut (defaut: 7 jours) |
| end_date | date | Non | Date fin (defaut: aujourd'hui) |
| user_id | integer | Non | Filtrer par utilisateur |
| operation_type | string | Non | Type: login, logout, confirmation, cancellation |
| page | integer | Non | Page (defaut: 1) |
| per_page | integer | Non | Elements par page (defaut: 50, max: 100) |

**Response 200:**
```json
{
    "success": true,
    "data": {
        "operations": [
            {
                "id": 12345,
                "timestamp": "2026-01-17T14:35:00Z",
                "user_id": 42,
                "username": "jdupont",
                "display_name": "Jean Dupont",
                "operation_type": "confirmation",
                "target_type": "spring",
                "target_id": "W1234_B1_A1_L",
                "details": {
                    "train_pass_id": 5678,
                    "action": "confirmed_missing"
                },
                "ip_address": "10.0.1.45",
                "user_agent": "Mozilla/5.0..."
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 50,
            "total": 245,
            "total_pages": 5
        }
    }
}
```

#### 5.9.2 GET /api/v1/audit/operations/{id}

**Description:** Retourne les details d'une operation specifique.

**Autorisation:** Superviseur, Administrateur

**Response 200:**
```json
{
    "success": true,
    "data": {
        "id": 12345,
        "timestamp": "2026-01-17T14:35:00Z",
        "user": {
            "id": 42,
            "username": "jdupont",
            "display_name": "Jean Dupont",
            "role": "operator"
        },
        "operation_type": "confirmation",
        "target": {
            "type": "spring",
            "id": "W1234_B1_A1_L",
            "wagon_rfid": "1234",
            "train_pass_id": 5678
        },
        "details": {
            "action": "confirmed_missing",
            "previous_conf_code": 3,
            "new_conf_code": 5
        },
        "metadata": {
            "ip_address": "10.0.1.45",
            "user_agent": "Mozilla/5.0...",
            "session_id": "abc123"
        }
    }
}
```

#### 5.9.3 GET /api/v1/audit/export

**Description:** Exporte l'historique des operations.

**Autorisation:** Superviseur, Administrateur

**Parametres Query:**
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| start_date | date | Oui | Date debut |
| end_date | date | Oui | Date fin |
| format | string | Non | Format: csv, pdf (defaut: csv) |
| user_id | integer | Non | Filtrer par utilisateur |
| operation_type | string | Non | Filtrer par type |

**Response 200:** Fichier CSV ou PDF telecharge.

---

### 5.10 Endpoints Rapports

#### 5.10.1 POST /api/v1/reports

**Description:** Genere un nouveau rapport d'operations.

**Autorisation:** Superviseur, Administrateur

**Request Body:**
```json
{
    "start_date": "2026-01-01",
    "end_date": "2026-01-17",
    "report_type": "summary",
    "filters": {
        "user_id": null,
        "operation_types": ["confirmation", "cancellation"]
    }
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| start_date | date | Oui | Date debut |
| end_date | date | Oui | Date fin (max 90 jours apres start) |
| report_type | string | Oui | "summary" ou "detailed" |
| filters | object | Non | Filtres optionnels |

**Response 202 (generation asynchrone si > 30 jours):**
```json
{
    "success": true,
    "data": {
        "report_id": "rpt_abc123",
        "status": "processing",
        "estimated_completion": "2026-01-17T15:30:00Z",
        "notification_email": "jdupont@eurotunnel.com"
    }
}
```

**Response 200 (generation immediate):**
```json
{
    "success": true,
    "data": {
        "report_id": "rpt_abc123",
        "status": "completed",
        "created_at": "2026-01-17T15:00:00Z",
        "summary": {
            "period": "2026-01-01 - 2026-01-17",
            "total_operations": 245,
            "operations_by_type": {
                "login": 89,
                "logout": 85,
                "confirmation": 65,
                "cancellation": 6
            },
            "active_users": 12
        },
        "download_urls": {
            "pdf": "/api/v1/reports/rpt_abc123/download?format=pdf",
            "csv": "/api/v1/reports/rpt_abc123/download?format=csv",
            "xlsx": "/api/v1/reports/rpt_abc123/download?format=xlsx"
        }
    }
}
```

#### 5.10.2 GET /api/v1/reports

**Description:** Liste les rapports generes par l'utilisateur.

**Autorisation:** Superviseur, Administrateur

**Response 200:**
```json
{
    "success": true,
    "data": {
        "reports": [
            {
                "report_id": "rpt_abc123",
                "created_at": "2026-01-17T15:00:00Z",
                "period": "2026-01-01 - 2026-01-17",
                "report_type": "summary",
                "status": "completed",
                "expires_at": "2026-04-17T15:00:00Z"
            }
        ]
    }
}
```

#### 5.10.3 GET /api/v1/reports/{report_id}

**Description:** Retourne les details et le statut d'un rapport.

#### 5.10.4 GET /api/v1/reports/{report_id}/download

**Description:** Telecharge un rapport dans le format specifie.

**Parametres Query:**
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| format | string | Oui | pdf, csv, xlsx |

**Response 200:** Fichier telecharge.

---

## 6. Securite

### 6.1 Authentification SSO Eurotunnel

#### 6.1.1 Integration SAML 2.0

L'authentification est deleguee au SSO Eurotunnel via le protocole SAML 2.0.

```python
SAML_CONFIG = {
    'strict': True,
    'debug': False,
    'security': {
        'authnRequestsSigned': True,
        'logoutRequestSigned': True,
        'logoutResponseSigned': True,
        'wantAssertionsSigned': True,
        'wantAssertionsEncrypted': False,
        'signatureAlgorithm': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
        'digestAlgorithm': 'http://www.w3.org/2001/04/xmlenc#sha256'
    }
}
```

#### 6.1.2 Flux d'Authentification

```
1. Utilisateur accede a VICORE
2. VICORE detecte absence de session
3. Redirection vers SSO Eurotunnel (SAML AuthnRequest)
4. Utilisateur s'authentifie sur le portail Eurotunnel
5. SSO renvoie SAML Response vers VICORE
6. VICORE valide la signature et les assertions
7. VICORE cree/met a jour l'utilisateur local
8. Session creee, redirection vers la page demandee
```

#### 6.1.3 Mapping des Attributs SAML

| Attribut SAML | Champ VICORE | Obligatoire |
|---------------|--------------|-------------|
| `NameID` | sso_id | Oui |
| `displayName` | display_name | Non |
| `mail` | email | Non |
| `sAMAccountName` | username | Oui |
| `memberOf` | role (via mapping) | Oui |

#### 6.1.4 Gestion des Sessions

```python
SESSION_CONFIG = {
    'session_lifetime': timedelta(hours=8),
    'session_refresh_each_request': True,
    'session_cookie_secure': True,
    'session_cookie_httponly': True,
    'session_cookie_samesite': 'Lax'
}
```

### 6.2 Autorisation

#### 6.2.1 Matrice des Roles

| Endpoint | Admin | Supervisor | Operator | Viewer |
|----------|-------|------------|----------|--------|
| GET /train-passes | X | X | X | X |
| POST /train-passes/{id}/confirm | X | X | X | - |
| GET /cars | X | X | X | X |
| POST /cars/{id}/confirm | X | X | X | - |
| GET /alerts | X | X | X | X |
| POST /alerts/{id}/acknowledge | X | X | X | - |
| GET /springs/{id}/history | X | X | X | X |
| POST /springs/{id}/cancel-confirmation | X | X | X | - |
| GET /audit/operations | X | X | - | - |
| GET /audit/export | X | X | - | - |
| POST /reports | X | X | - | - |
| GET /reports | X | X | - | - |
| GET /reports/{id}/download | X | X | - | - |
| GET /users | X | - | - | - |
| POST /users | X | - | - | - |
| DELETE /users/{id} | X | - | - |

### 6.3 Protection des Donnees

#### 6.3.1 Chiffrement

| Donnee | Methode |
|--------|---------|
| Assertions SAML | Signature RSA-SHA256 |
| Connexion HTTPS | TLS 1.3 |
| Sessions | Cookie securise + Redis |
| Donnees sensibles | AES-256-GCM |

#### 6.3.2 Variables d'Environnement

```bash
# .env.example
FLASK_SECRET_KEY=<random-64-chars>
DATABASE_URL=postgresql://user:pass@host:5432/vicore
REDIS_URL=redis://host:6379/0

# SSO Eurotunnel Configuration
SSO_ENTITY_ID=https://vicore.eurotunnel.com/saml/metadata
SSO_IDP_METADATA_URL=https://sso.eurotunnel.com/saml/metadata
SSO_SP_CERT_FILE=/etc/vicore/saml/sp.crt
SSO_SP_KEY_FILE=/etc/vicore/saml/sp.key

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### 6.4 Protection OWASP

#### 6.4.1 Mesures Implementees

| Vulnerabilite | Protection |
|---------------|------------|
| **SQL Injection** | ORM SQLAlchemy, requetes parametrees |
| **XSS** | Echappement Jinja2, CSP headers |
| **CSRF** | Tokens Flask-WTF |
| **Broken Auth** | SSO Eurotunnel, validation SAML, session securisee |
| **Sensitive Data** | HTTPS, chiffrement, masquage |
| **XXE** | Desactivation XML parsing externe |
| **Broken Access** | RBAC, verification systematique |
| **Security Misconfig** | Headers securises, audit regulier |
| **Insecure Deserialization** | Validation stricte JSON |
| **Logging** | Audit trail complet |

#### 6.4.2 Headers de Securite

```python
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.bootcdn.net; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}
```

### 6.5 Rate Limiting

```python
RATE_LIMITS = {
    'sso_callback': '10/minute',     # Callbacks SSO
    'api_global': '100/minute',       # Toutes requetes API
    'api_per_user': '60/minute'       # Par utilisateur authentifie
}
```

**Note:** L'authentification etant deleguee au SSO Eurotunnel, le rate limiting des tentatives de connexion est gere par le portail SSO.

---

## 7. Performance et Scalabilite

### 7.1 Objectifs de Performance

| Metrique | Objectif | Critique |
|----------|----------|----------|
| Temps de reponse P50 | < 100ms | < 200ms |
| Temps de reponse P95 | < 300ms | < 500ms |
| Temps de reponse P99 | < 500ms | < 1000ms |
| Disponibilite | 99.9% | 99.5% |
| Utilisateurs simultanes | 50 | 100 |
| Requetes/seconde | 100 | 200 |

### 7.2 Strategies de Cache

#### 7.2.1 Niveaux de Cache

```
+------------------+     +------------------+     +------------------+
|  Browser Cache   | --> |   Redis Cache    | --> |   PostgreSQL     |
|   (statiques)    |     |  (donnees freq)  |     |  (persistance)   |
+------------------+     +------------------+     +------------------+
     TTL: 1 jour           TTL: 5-60 min          Source de verite
```

#### 7.2.2 Politique de Cache Redis

```python
CACHE_CONFIG = {
    # Donnees frequemment accedees
    'train_passes_list': {
        'ttl': 60,  # 1 minute
        'invalidation': ['train_pass_created', 'train_pass_updated']
    },
    'car_details': {
        'ttl': 120,  # 2 minutes
        'invalidation': ['car_updated', 'spring_updated']
    },
    'system_health': {
        'ttl': 30,  # 30 secondes
        'invalidation': []
    },
    # Sessions utilisateur
    'user_session': {
        'ttl': 28800,  # 8 heures
        'invalidation': ['logout']
    }
}
```

### 7.3 Optimisations Base de Donnees

#### 7.3.1 Index Strategiques

```sql
-- Requetes les plus frequentes
CREATE INDEX idx_train_passes_recent ON train_passes(passage_time DESC)
    WHERE status IN ('pending', 'in_progress');

CREATE INDEX idx_alerts_active ON spring_alerts(created_at DESC)
    WHERE is_acknowledged = FALSE;

CREATE INDEX idx_cars_with_alerts ON cars(train_pass_id)
    WHERE status IN ('warning', 'alert');
```

#### 7.3.2 Connection Pooling

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### 7.4 Scalabilite Horizontale

```
                    +------------------+
                    |   Load Balancer  |
                    |     (Nginx)      |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+------------------+ +------------------+ +------------------+
|   App Server 1   | |   App Server 2   | |   App Server 3   |
|   (Gunicorn)     | |   (Gunicorn)     | |   (Gunicorn)     |
+------------------+ +------------------+ +------------------+
         |                   |                   |
         +-------------------+-------------------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +------------------+          +------------------+
     |    PostgreSQL    |          |      Redis       |
     |    (Primary)     |          |    (Cluster)     |
     +------------------+          +------------------+
              |
              v
     +------------------+
     |    PostgreSQL    |
     |    (Replica)     |
     +------------------+
```

---

## 8. Infrastructure et Deploiement

### 8.1 Environnements

| Environnement | Utilisation | Configuration |
|---------------|-------------|---------------|
| **Development** | Developpement local | SQLite, debug mode |
| **Testing** | Tests automatises | PostgreSQL test, fixtures |
| **Staging** | Validation pre-prod | Replique production |
| **Production** | Exploitation | HA, monitoring complet |

### 8.2 Docker Configuration

#### 8.2.1 Dockerfile Application

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:create_app()"]
```

#### 8.2.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://vicore:${DB_PASSWORD}@db:5432/vicore
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - vicore-network

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=vicore
      - POSTGRES_USER=vicore
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vicore"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - vicore-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - vicore-network

  nginx:
    image: nginx:1.24-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - vicore-network

volumes:
  postgres_data:
  redis_data:

networks:
  vicore-network:
    driver: bridge
```

### 8.3 CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit safety
      - run: bandit -r app/
      - run: safety check

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: vicore:${{ github.sha }}

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment scripts
```

### 8.4 Monitoring

#### 8.4.1 Stack de Monitoring

```
+------------------+     +------------------+     +------------------+
|   Application    | --> |    Prometheus    | --> |     Grafana      |
|   (metrics)      |     |   (collection)   |     | (visualisation)  |
+------------------+     +------------------+     +------------------+
         |
         v
+------------------+     +------------------+
|      Logs        | --> |       ELK        |
|  (structured)    |     |   (aggregation)  |
+------------------+     +------------------+
```

#### 8.4.2 Metriques Collectees

| Categorie | Metriques |
|-----------|-----------|
| **Application** | request_count, request_latency, error_rate |
| **Business** | train_passes_count, alerts_count, confirmations_count |
| **Infrastructure** | cpu_usage, memory_usage, disk_usage |
| **Database** | connections_active, query_duration, cache_hit_rate |

---

## 9. Interfaces Externes

### 9.1 Systeme Heartbeat

#### 9.1.1 Protocole de Communication

```
VICORE <------ HTTP/SSE ------> Heartbeat System
               |
               | Ping toutes les 30 secondes
               | Timeout: 60 secondes
               v
        Status: OK / WARNING / ERROR
```

#### 9.1.2 Format des Messages

**Requete Heartbeat:**
```json
{
    "source": "vicore-v2",
    "timestamp": "2026-01-18T10:30:00Z",
    "status": "alive"
}
```

**Reponse Heartbeat:**
```json
{
    "status": "ok",
    "cameras": [
        {
            "id": "CAM-01",
            "status": "online",
            "last_frame": "2026-01-18T10:29:58Z"
        }
    ]
}
```

### 9.2 Acquisition des Conditions Environnementales

#### 9.2.1 Architecture d'Acquisition

```
+------------------+     +------------------+     +------------------+
|  Sources Auto    |     |  Sources Ext.    |     |  Sources IA      |
|  - Horodatage    |     |  - API Meteo     |     |  - Analyse image |
|  - Vitesse RFID  |     |  - Capteurs site |     |  - Detection     |
|  - Metadata cam  |     |                  |     |    conditions    |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   ConditionsService       |
                    |   - Aggregation donnees   |
                    |   - Calcul qualite        |
                    |   - Cache Redis           |
                    +---------------------------+
                                  |
                                  v
                    +---------------------------+
                    |   Base de donnees         |
                    |   Table: train_pass_cond  |
                    +---------------------------+
```

#### 9.2.2 Sources de Donnees

**1. Horodatage et Calcul Jour/Nuit**

```python
# Calcul automatique depuis l'heure de passage
def calculate_daylight(passage_time: datetime, lat: float, lon: float) -> dict:
    """
    Calcule si le passage est de jour ou de nuit.

    Args:
        passage_time: Heure du passage
        lat, lon: Coordonnees du site (Folkestone/Coquelles)

    Returns:
        {
            "is_daylight": True/False,
            "sun_altitude": float,  # Degrees above horizon
            "civil_twilight": True/False
        }
    """
    # Utilise la librairie 'astral' pour le calcul
    pass

# Coordonnees des sites
SITE_COORDINATES = {
    'VOIE_D': {'lat': 51.0847, 'lon': 1.1167},   # Folkestone
    'VOIE_E': {'lat': 50.9281, 'lon': 1.8125}    # Coquelles
}
```

**2. Vitesse du Train (Systeme RFID)**

```python
# Recuperation depuis le systeme RFID existant
class RFIDDataService:
    def get_train_speed(self, train_pass_id: int) -> float:
        """
        Recupere la vitesse du train depuis les capteurs RFID.

        Returns:
            Vitesse en km/h
        """
        # Integration avec le systeme RFID existant
        pass
```

**3. Metadonnees Camera**

```python
# Extraction des metadonnees EXIF/camera
class CameraMetadataService:
    def extract_metadata(self, image_path: str) -> dict:
        """
        Extrait les metadonnees de capture.

        Returns:
            {
                "exposure_time": float,      # Secondes
                "iso": int,
                "aperture": float,
                "brightness_value": float,
                "image_quality_score": float  # 0-1
            }
        """
        pass
```

**4. API Meteo Externe (Optionnel)**

```python
# Integration API meteo
WEATHER_API_CONFIG = {
    'provider': 'openweathermap',  # ou 'meteofrance'
    'api_key': '${WEATHER_API_KEY}',
    'cache_ttl': 300,  # 5 minutes
    'endpoints': {
        'openweathermap': 'https://api.openweathermap.org/data/2.5/weather',
        'meteofrance': 'https://api.meteo.fr/v1/current'
    }
}

class WeatherAPIService:
    def get_current_conditions(self, lat: float, lon: float) -> dict:
        """
        Recupere les conditions meteo actuelles.

        Returns:
            {
                "temperature_c": float,
                "humidity_percent": int,
                "precipitation_mm": float,
                "visibility_m": int,
                "conditions": str,  # 'clear', 'cloudy', 'rain', 'fog'
                "wind_speed_kmh": float
            }
        """
        pass
```

**5. Capteurs Sur Site (Si Disponibles)**

```python
# Interface capteurs locaux Eurotunnel
class SiteSensorService:
    """
    Service pour les capteurs meteorologiques sur site.
    A implementer selon l'infrastructure disponible chez Eurotunnel.
    """

    def get_visibility(self, site_code: str) -> int:
        """Retourne la visibilite en metres."""
        pass

    def get_precipitation(self, site_code: str) -> bool:
        """Retourne True si precipitation detectee."""
        pass

    def get_temperature(self, site_code: str) -> float:
        """Retourne la temperature en Celsius."""
        pass
```

**6. Analyse d'Image IA (Detection de Conditions)**

```python
# Detection de conditions via analyse d'image
class ImageConditionAnalyzer:
    """
    Analyse les images pour detecter des conditions defavorables.
    """

    def analyze_image(self, image_path: str) -> dict:
        """
        Analyse une image pour detecter des conditions defavorables.

        Returns:
            {
                "water_droplets_detected": bool,
                "fog_detected": bool,
                "low_contrast": bool,
                "blur_score": float,  # 0-1, 1=net
                "overall_quality": float  # 0-1
            }
        """
        pass
```

#### 9.2.3 Modele de Donnees Conditions

```sql
-- Table des conditions par passage de train
CREATE TABLE train_pass_conditions (
    id              SERIAL PRIMARY KEY,
    train_pass_id   INTEGER NOT NULL REFERENCES train_passes(id) ON DELETE CASCADE,

    -- Conditions temporelles
    is_daylight     BOOLEAN,
    sun_altitude    DECIMAL(5,2),

    -- Conditions meteo
    temperature_c   DECIMAL(4,1),
    humidity_pct    INTEGER,
    precipitation   BOOLEAN,
    visibility_m    INTEGER,
    weather_code    VARCHAR(20),  -- 'clear', 'cloudy', 'rain', 'fog', 'snow'

    -- Conditions operationnelles
    train_speed_kmh DECIMAL(5,1),

    -- Qualite camera
    exposure_ok     BOOLEAN,
    image_quality   DECIMAL(3,2),  -- Score 0-1

    -- Alertes conditions
    conditions_alert BOOLEAN DEFAULT FALSE,
    alert_reasons   TEXT[],  -- Array of reasons

    -- Metadonnees
    data_sources    TEXT[],  -- Sources utilisees: 'timestamp', 'rfid', 'api_meteo', 'sensors', 'camera'
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_train_pass_conditions UNIQUE (train_pass_id)
);

CREATE INDEX idx_tpc_train_pass ON train_pass_conditions(train_pass_id);
CREATE INDEX idx_tpc_alert ON train_pass_conditions(conditions_alert) WHERE conditions_alert = TRUE;
```

#### 9.2.4 API Conditions

```
GET /api/v1/train-passes/{id}/conditions

Response 200:
{
    "success": true,
    "data": {
        "train_pass_id": 1234,
        "conditions": {
            "daylight": {
                "is_day": true,
                "time_of_day": "14:32",
                "sun_altitude": 25.5
            },
            "weather": {
                "temperature_c": 8,
                "conditions": "clear",
                "precipitation": false,
                "visibility_m": 10000
            },
            "operational": {
                "train_speed_kmh": 42
            },
            "camera": {
                "exposure_ok": true,
                "image_quality": 0.92
            }
        },
        "quality_assessment": {
            "overall_score": 0.95,
            "is_optimal": true,
            "alerts": []
        },
        "data_sources": ["timestamp", "rfid", "camera_metadata", "api_meteo"]
    }
}
```

#### 9.2.5 Configuration des Seuils

```python
CONDITIONS_THRESHOLDS = {
    'visibility': {
        'good': 1000,      # > 1000m = conditions bonnes
        'moderate': 500,   # 500-1000m = conditions moderees
        'poor': 200        # < 200m = alerte brouillard
    },
    'train_speed': {
        'optimal': 50,     # < 50 km/h = optimal
        'acceptable': 80,  # 50-80 km/h = acceptable
        'high': 100        # > 80 km/h = vitesse elevee
    },
    'temperature': {
        'frost_risk': 2,   # < 2°C = risque givre/buee
        'heat_risk': 35    # > 35°C = risque surchauffe
    },
    'image_quality': {
        'good': 0.8,       # > 0.8 = bonne qualite
        'acceptable': 0.6, # 0.6-0.8 = acceptable
        'poor': 0.4        # < 0.6 = qualite insuffisante
    }
}
```

### 9.3 Systeme de Cameras

#### 9.2.1 Integration

```
+------------------+     +------------------+     +------------------+
|     Cameras      | --> | Image Processing | --> |     VICORE       |
|   (hardware)     |     |    (detection)   |     |   (affichage)    |
+------------------+     +------------------+     +------------------+
                                  |
                                  v
                         +------------------+
                         |   Spring Data    |
                         |   (measurements) |
                         +------------------+
```

#### 9.2.2 Format des Donnees Ressorts

```json
{
    "car_id": "CAR-001",
    "timestamp": "2026-01-18T10:30:00Z",
    "springs": [
        {
            "position": 1,
            "side": "left",
            "height_mm": 145.5,
            "confidence": 0.95,
            "image_ref": "img_20260118_103000_001_L.jpg"
        }
    ]
}
```

---

## 10. Annexes

### 10.1 Matrice de Tracabilite Technique

| Exigence | Composant Technique | API | Table DB |
|----------|---------------------|-----|----------|
| EF-AUTH-01 | SSOService | GET /auth/sso/login, POST /auth/sso/callback | users |
| EF-TP-01 | TrainPassService | GET /train-passes | train_passes |
| EF-CAR-01 | CarService | GET /cars | cars, springs |
| EF-SPR-01 | SpringService | GET /springs | springs, spring_alerts |
| EF-MON-01 | MonitoringService | GET /system/heartbeat | - (external) |

### 10.2 Codes d'Erreur API

| Code | HTTP | Description |
|------|------|-------------|
| AUTH_001 | 401 | Token invalide ou expire |
| AUTH_002 | 401 | Identifiants incorrects |
| AUTH_003 | 403 | Acces non autorise |
| VAL_001 | 400 | Donnees de requete invalides |
| VAL_002 | 400 | Parametre manquant |
| RES_001 | 404 | Ressource non trouvee |
| RES_002 | 409 | Conflit de ressource |
| SYS_001 | 500 | Erreur serveur interne |
| SYS_002 | 503 | Service temporairement indisponible |

### 10.3 Configuration des Seuils Ressorts

```python
SPRING_THRESHOLDS = {
    'height': {
        'nominal': 150,       # mm
        'warning_low': 135,   # mm
        'critical_low': 120,  # mm
        'warning_high': 165,  # mm
        'critical_high': 180  # mm
    },
    'variance': {
        'warning': 10,        # mm difference entre cotes
        'critical': 20        # mm difference entre cotes
    }
}
```

### 10.4 Scripts de Migration

```sql
-- V1__Initial_Schema.sql
-- Creation des tables initiales

-- V2__Add_Audit_Logs.sql
-- Ajout de la table audit_logs

-- V3__Add_Indexes.sql
-- Ajout des index de performance
```

---

*Document genere le 2026-01-18*
*Version: 1.0*
*Statut: En attente de validation*
