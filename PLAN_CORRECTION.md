# VICORE - Plan de Correction des Faiblesses

## Résumé Exécutif

| Priorité | Catégorie | Nombre d'actions | Effort Total |
|----------|-----------|------------------|--------------|
| 🔴 P0 - Critique | Sécurité | 2 | 1h |
| 🟠 P1 - Haute | Sécurité + Qualité | 4 | 4-6h |
| 🟡 P2 - Moyenne | Qualité de code | 5 | 2-3h |
| 🟢 P3 - Basse | Améliorations | 4 | 1-2 jours |

---

## 🔴 PRIORITÉ 0 - CRITIQUE (À faire immédiatement)

### P0-1: Externaliser la Secret Key

**Fichier:** `eurotunnel_web/app.py`
**Ligne:** 27
**Risque:** Compromission de toutes les sessions utilisateur

#### Code Actuel (VULNÉRABLE)
```python
app.secret_key = 'slkfjaslkfdjlsadflknisdf64s6d4f56asf'
```

#### Code Corrigé
```python
import os
import secrets

def get_secret_key():
    """Get secret key from environment or generate a secure one."""
    key = os.environ.get('FLASK_SECRET_KEY')
    if not key:
        # En développement seulement - générer une clé temporaire
        if os.environ.get('WEB_DEBUG', 'False').lower() == 'true':
            key = secrets.token_hex(32)
            print("WARNING: Using temporary secret key. Set FLASK_SECRET_KEY in production!")
        else:
            raise ValueError("FLASK_SECRET_KEY environment variable must be set in production")
    return key

app.secret_key = get_secret_key()
```

#### Actions
1. Modifier `app.py` avec le code ci-dessus
2. Générer une clé sécurisée: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Ajouter au `.env`: `export FLASK_SECRET_KEY="<clé_générée>"`
4. Mettre à jour la documentation de déploiement

**Effort:** 30 minutes

---

### P0-2: Supprimer les Credentials par Défaut en Production

**Fichier:** `eurotunnel_web/user_management.py`
**Ligne:** 27-36
**Risque:** Accès non autorisé avec identifiants publics

#### Code Actuel (VULNÉRABLE)
```python
def create_users_if_none():
    """I create the default users if there aren't any in the DB"""
    with get_session() as session:
        qry = func.count().select().select_from(Users)
        n_users = session.execute(qry).scalar()
        logger.info(f"There are {n_users} setup on this system")
        if(n_users == 0):
            logger.info(f"Creating user")
            create_user("eurotunnel","Spr1ngs","Euro Tunnel")
```

#### Code Corrigé
```python
import os

def create_users_if_none():
    """Create default user only in development mode."""
    # Ne JAMAIS créer d'utilisateur par défaut en production
    if os.environ.get('VICORE_ENV', 'production').lower() == 'production':
        logger.warning("Skipping default user creation in production mode")
        return

    with get_session() as session:
        qry = func.count().select().select_from(Users)
        n_users = session.execute(qry).scalar()
        logger.info(f"There are {n_users} users on this system")

        if n_users == 0:
            # Utiliser des credentials depuis les variables d'environnement
            default_user = os.environ.get('VICORE_DEFAULT_USER', 'admin')
            default_pass = os.environ.get('VICORE_DEFAULT_PASS')

            if not default_pass:
                logger.error("VICORE_DEFAULT_PASS not set. Cannot create default user.")
                return

            logger.info(f"Creating default user: {default_user}")
            create_user(default_user, default_pass, "Default Admin")
```

#### Actions
1. Modifier `user_management.py`
2. Ajouter variable d'environnement `VICORE_ENV=development` pour le dev
3. Documenter la procédure de création du premier utilisateur en production
4. Créer un script CLI pour ajouter des utilisateurs

**Effort:** 30 minutes

---

## 🟠 PRIORITÉ 1 - HAUTE (Semaine 1)

### P1-1: Corriger le Bare Except

**Fichier:** `eurotunnel_web/version.py`
**Ligne:** 8
**Risque:** Masque des erreurs inattendues

#### Code Actuel
```python
try:
    #code...
except:
    #fallback
```

#### Code Corrigé
```python
try:
    from importlib.metadata import version as get_version
    VERSION = get_version('eurotunnel_web')
except (ImportError, PackageNotFoundError) as e:
    logger.warning(f"Could not determine version: {e}")
    VERSION = "unknown"
```

**Effort:** 15 minutes

---

### P1-2: Corriger les Comparaisons à None

**Fichiers:** `db_iface.py`, `train_pass_endpoints.py`
**Risque:** Comportement inattendu avec objets ayant `__eq__` personnalisé

#### Rechercher et Remplacer
```python
# INCORRECT
if db_session == None:
if variable == None:

# CORRECT
if db_session is None:
if variable is None:
```

#### Localisations
| Fichier | Ligne | Code à corriger |
|---------|-------|-----------------|
| `db_iface.py` | 82 | `if db_session == None:` |
| `db_iface.py` | 168 | `if db_session == None:` |
| `db_iface.py` | 194 | `if db_session == None:` |
| `train_pass_endpoints.py` | 79 | `if n_to_fetch:` (OK mais vérifier) |
| `display_name_iface.py` | 37 | `if displaynames == None:` |

**Effort:** 30 minutes

---

### P1-3: Supprimer les Imports Inutilisés

**Fichiers multiples**

#### Liste des imports à supprimer
| Fichier | Import inutilisé |
|---------|------------------|
| `db_iface.py` | `SpringLocation` (si non utilisé) |
| `db_iface.py` | `TrainPass` |
| `db_iface.py` | `CarTypes` |
| `db_iface.py` | `TrainPassCars` |
| `confidence_levels.py` | `select` |
| `user_management.py` | `Session` |

#### Commande automatique
```bash
pip install autoflake
autoflake --in-place --remove-all-unused-imports eurotunnel_web/*.py
```

**Effort:** 15 minutes

---

### P1-4: Ajouter Rate Limiting sur /login

**Fichier:** `eurotunnel_web/app.py`
**Risque:** Attaque par force brute

#### Installation
```bash
pip install Flask-Limiter
```

#### Code à ajouter
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 tentatives par minute
def login():
    # ... code existant ...
```

**Effort:** 1-2 heures

---

## 🟡 PRIORITÉ 2 - MOYENNE (Semaine 2)

### P2-1: Formater le Code avec Black

#### Installation et exécution
```bash
pip install black isort

# Formater tout le code
black eurotunnel_web/ --line-length 120

# Trier les imports
isort eurotunnel_web/ --profile black
```

#### Configuration `.pyproject.toml`
```toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 120
```

**Effort:** 30 minutes

---

### P2-2: Ajouter Pre-commit Hooks

#### Installation
```bash
pip install pre-commit
```

#### Fichier `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        args: ['--line-length=120']

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ['--profile=black']

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--ignore=E501,W503']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

#### Activation
```bash
pre-commit install
pre-commit run --all-files  # Première exécution
```

**Effort:** 30 minutes

---

### P2-3: Corriger l'Indentation Incohérente

**Fichiers concernés:** `db_iface.py`, `user_management.py`

Les erreurs E111/E117 indiquent des problèmes d'indentation. Black corrigera automatiquement la plupart, mais vérifier manuellement:

```python
# INCORRECT (E117 over-indented)
def function():
        return value  # 8 espaces au lieu de 4

# CORRECT
def function():
    return value  # 4 espaces
```

**Effort:** 30 minutes (après Black)

---

### P2-4: Ajouter Configuration Flake8

#### Fichier `setup.cfg` ou `.flake8`
```ini
[flake8]
max-line-length = 120
ignore = E501, W503, E203
exclude =
    .venv,
    __pycache__,
    .git,
    build,
    dist
per-file-ignores =
    __init__.py: F401
    tests/*: E501
```

**Effort:** 15 minutes

---

### P2-5: Corriger les Commentaires Mal Formatés

**Erreur E265:** Block comment should start with '# '

#### Rechercher et corriger
```python
# INCORRECT
#This is a comment
#Comment without space

# CORRECT
# This is a comment
# Comment with space
```

**Commande de recherche:**
```bash
grep -rn "^#[^ #]" eurotunnel_web/*.py
```

**Effort:** 30 minutes

---

## 🟢 PRIORITÉ 3 - BASSE (Mois suivant)

### P3-1: Ajouter Protection CSRF

#### Installation
```bash
pip install Flask-WTF
```

#### Configuration
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)
```

#### Templates (ajouter dans les formulaires)
```html
<form method="post">
    {{ csrf_token() }}
    <!-- ... -->
</form>
```

**Effort:** 4-8 heures

---

### P3-2: Ajouter Tests Unitaires

#### Structure proposée
```
tests/
├── unit/
│   ├── test_confidence_levels.py
│   ├── test_display_name.py
│   ├── test_user_management.py
│   └── test_redis_web.py
├── integration/
│   └── test_dbiface.py  (existant)
└── conftest.py  (fixtures partagées)
```

#### Exemple de test unitaire avec mock
```python
# tests/unit/test_confidence_levels.py
import pytest
from unittest.mock import Mock, patch

from eurotunnel_web.confidence_levels import confidence_interface

class TestConfidenceInterface:

    @patch('eurotunnel_web.confidence_levels.get_session')
    def test_confidence_level_green(self, mock_session):
        # Arrange
        mock_levels = [Mock(conf_range=Mock(contains=lambda x: 0.8 <= x <= 1.0),
                           confidence_level=1, level_name_en='GREEN')]
        mock_session.return_value.__enter__ = Mock(return_value=Mock(
            execute=Mock(return_value=Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=mock_levels)))))
        ))

        # Act
        ci = confidence_interface()
        result = ci.confidence_level_car_and_spring(0.9, None)

        # Assert
        assert result == '1'
```

**Effort:** 2-3 jours

---

### P3-3: Ajouter Logging Structuré pour Audit

#### Code à ajouter dans `missing_spring_endpoints.py`
```python
from datetime import datetime

def log_confirmation(spring_id: int, status: bool, user: str):
    """Log spring confirmation for audit trail."""
    logger.info(
        "AUDIT_CONFIRMATION",
        extra={
            "event_type": "spring_confirmation",
            "spring_location_id": spring_id,
            "confirmed_present": status,
            "confirmed_by": user,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": request.remote_addr
        }
    )
```

**Effort:** 2-4 heures

---

### P3-4: Documenter l'API avec OpenAPI/Swagger

#### Installation
```bash
pip install flask-swagger-ui flasgger
```

#### Configuration
```python
from flasgger import Swagger

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, config=swagger_config)
```

**Effort:** 1-2 jours

---

## Script de Correction Automatique

Créer `scripts/fix_code_quality.sh`:

```bash
#!/bin/bash
# Script de correction automatique de la qualité du code

echo "=== VICORE Code Quality Fix ==="

# 1. Installer les outils
echo "[1/5] Installing tools..."
pip install black isort autoflake flake8 pre-commit

# 2. Supprimer imports inutilisés
echo "[2/5] Removing unused imports..."
autoflake --in-place --remove-all-unused-imports --recursive eurotunnel_web/

# 3. Trier les imports
echo "[3/5] Sorting imports..."
isort eurotunnel_web/ --profile black --line-length 120

# 4. Formater avec Black
echo "[4/5] Formatting with Black..."
black eurotunnel_web/ --line-length 120

# 5. Vérifier avec Flake8
echo "[5/5] Checking with Flake8..."
flake8 eurotunnel_web/ --max-line-length=120 --ignore=E501,W503 --statistics

echo "=== Done ==="
```

---

## Checklist de Validation

### Avant Déploiement Production

- [ ] P0-1: Secret key externalisée
- [ ] P0-2: Pas de credentials par défaut
- [ ] P1-1: Bare except corrigé
- [ ] P1-2: Comparaisons None corrigées
- [ ] P1-4: Rate limiting actif sur /login
- [ ] Variables d'environnement documentées
- [ ] HTTPS configuré
- [ ] Logs d'audit activés

### Qualité de Code

- [ ] P2-1: Code formaté avec Black
- [ ] P2-2: Pre-commit hooks installés
- [ ] P2-3: Indentation cohérente
- [ ] P1-3: Imports inutilisés supprimés
- [ ] P2-5: Commentaires formatés
- [ ] Flake8 < 50 warnings

### Tests

- [ ] Tests d'intégration passent
- [ ] Tests unitaires ajoutés (couverture > 60%)
- [ ] Tests de sécurité basiques effectués

---

## Timeline Proposée

```
Semaine 1: Corrections Critiques (P0 + P1)
├── Jour 1-2: P0-1, P0-2 (Sécurité immédiate)
├── Jour 3: P1-1, P1-2, P1-3 (Corrections rapides)
└── Jour 4-5: P1-4 (Rate limiting)

Semaine 2: Qualité de Code (P2)
├── Jour 1: P2-1, P2-2 (Black, pre-commit)
├── Jour 2: P2-3, P2-4, P2-5 (Nettoyage)
└── Jour 3-5: Revue et validation

Mois 2: Améliorations (P3)
├── Semaine 1: P3-1 (CSRF)
├── Semaine 2-3: P3-2 (Tests unitaires)
└── Semaine 4: P3-3, P3-4 (Audit, Documentation API)
```

---

*Plan de correction généré le 2026-01-16*
