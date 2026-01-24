# CLAUDE.md - VICORE Project Guidelines

## Project Overview

**VICORE** (VIsualisation COntrole REssorts) is a web-based monitoring platform for railway suspension spring inspection at Eurotunnel. The system provides real-time visualization of spring conditions through automated image analysis, alert management, and historical tracking of train passes through the Channel Tunnel.

**Current Version:** 1.0.0.12
**VICORE V2:** In specification phase with UI/UX mockups

## Quick Commands

```bash
# Run Flask development server
python eurotunnel_web/app.py

# Run tests
pytest tests/

# Code quality (pre-commit hooks)
pre-commit run --all-files

# Deploy mockups to Vercel
git push vicore-mockup master:main
```

## Project Structure

```
eurotunnel_web-master/
├── eurotunnel_web/              # Main Flask application
│   ├── app.py                   # Flask entry point
│   ├── models/                  # Pydantic data models
│   ├── templates/               # Jinja2 HTML templates
│   ├── static/                  # CSS, JS, images
│   ├── db_iface.py              # Database interface (SQLAlchemy)
│   ├── train_pass_endpoints.py  # Train pass API
│   ├── missing_spring_endpoints.py  # Spring confirmation
│   ├── system_endpoints.py      # System health monitoring
│   ├── user_management.py       # Authentication
│   ├── confidence_levels.py     # Confidence calculations
│   └── redis_web.py             # Redis caching
├── tests/integration/           # Integration tests
├── scripts/                     # Utility scripts
├── PROJET_VICORE_V2/            # V2 specifications & mockups
│   ├── 01_SPECIFICATIONS/       # Design documents (V-Cycle)
│   └── 02_MOCKUPS/              # Interactive HTML mockups
├── pyproject.toml               # Poetry configuration
├── requirements.txt             # Python dependencies
└── vercel.json                  # Vercel deployment config
```

## Technology Stack

### Backend
- **Python 3.10-3.12** with Flask 3.0+
- **SQLAlchemy 2.0** for PostgreSQL ORM
- **Redis** for caching and sessions
- **Pydantic** for data validation
- **Bcrypt** for password hashing

### Frontend
- **Vue.js 2.6** + Element-UI
- **Bootstrap 5.3** for responsive layout
- **Axios** for HTTP requests
- **Custom dark-tech theme CSS**

### External Dependency
- **eurotunnel_datamodel** - Database models, ConfigManager, Redis helpers (required as sibling project or installed via Poetry)

## Key Application Components

### Routes (app.py)
| Route | Purpose |
|-------|---------|
| `/` | Train pass list |
| `/login`, `/logout` | Authentication |
| `/cars/<train_pass_id>/<car_num>` | Car detail view |
| `/wheelimg/<path>` | Serve wheel images |

### Database Interface (db_iface.py)
```python
get_train_pass_info(train_pass_id)     # Single train pass
get_n_train_passes(n)                   # Latest n passes
get_train_pass_cars(train_pass_id)      # Cars in a pass
get_car_info_with_wheels(tpid, car_num) # Car with spring data
```

### Confidence System (confidence_levels.py)
- Codes: 0=confirmed, 1-4=confidence ranges, 5=unchecked
- Train codes: 1=GREEN, 3=AMBER, 5=RED
- Method: minimum confidence across wheels/cars

## PROJET_VICORE_V2 (Mockups)

**Deployment URL:** https://vicore-mockup.vercel.app

### Pages
| File | Description |
|------|-------------|
| `00_alerts_dashboard.html` | Home - Alert management |
| `01_login.html` | SSO authentication |
| `02_system_view.html` | Train passes list |
| `03_car_view.html` | Wagon inspection view |
| `04_historique_ressort.html` | Spring history |
| `05_audit_trail.html` | Audit log |
| `06_rapports.html` | Reports |

### Mockup Conventions
- **Theme:** Dark tech with cyan/blue accents
- **CSS Variables:** Defined in `css/style.css`
- **Status Colors:** Green (OK), Yellow (Alerte), Red (Critique), Purple (Confirme)
- **Direction Badges:**
  - `Sens normal` (green) = Tunnel vers Quais
  - `En tiroir` (yellow) = Quais vers Tunnel

### Deploy Mockups
```bash
git add PROJET_VICORE_V2/02_MOCKUPS/
git commit -m "feat(vicore): Description"
git push vicore-mockup master:main
```

## Code Conventions

### Python
- **snake_case** for functions and variables
- **UPPER_CASE** for constants
- **CamelCase** for classes
- Line length: 120 characters (Black formatter)

### Templates (Jinja2)
- Base templates: `base.html`, `authorised_users_base.html`
- Template includes in `includes/`
- Bootstrap 5 classes for layout

### Session Management
```python
# Session key for user
SESSION_USER_KEY = "user"  # from common_consts.py

# Check authentication
if SESSION_USER_KEY not in session:
    return redirect(url_for("login"))
```

### Database Patterns
```python
# Always use context manager
with get_session() as session:
    result = session.query(Model).filter(...).all()
```

### API Responses
- JSON format for all API endpoints
- HTTP status codes: 200 (OK), 400 (Bad Request), 403 (Forbidden), 500 (Error)

## Environment Variables

### Required in Production
```bash
FLASK_SECRET_KEY=<secure-random-key>
VICORE_ENV=production
```

### Development Defaults
```bash
WEB_HOST=127.0.0.1
WEB_PORT=5000
WEB_DEBUG=True
VICORE_ENV=development
```

### Database (via eurotunnel_datamodel)
```bash
DB_HOST=localhost
DB_PORT=5432
DB=euro_tunnel_dev
DB_USER=<user>
DB_PASSWORD=<password>
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=eurotunnel_web tests/

# Single test file
pytest tests/integration/test_dbiface.py -v
```

**Test database required:** PostgreSQL with test credentials in `pyproject.toml`

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- **Black** - Code formatting
- **isort** - Import sorting
- **Flake8** - Linting
- **Bandit** - Security scanning

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Git Remotes

| Remote | Repository | Purpose |
|--------|------------|---------|
| `origin` | hervelenglin-coder/Vicore | Main development |
| `vicore-mockup` | hervelenglin-coder/vicore-mockup | Mockups deployment (Vercel) |

## Important Notes

1. **Never hardcode credentials** - Use environment variables
2. **External dependency** - `eurotunnel_datamodel` must be available
3. **Timezone handling** - All datetimes are timezone-aware (Europe/Paris default)
4. **Redis caching** - Display names cached for 3 days, installations for 1 hour
5. **Lazy loading** - Train passes load 25 at a time on scroll
6. **Direction indicator** - Read-only data from capture system, not user-modifiable

## V-Cycle Documentation (PROJET_VICORE_V2/01_SPECIFICATIONS/)

| Document | Purpose |
|----------|---------|
| `01_SRS_*.md` | Requirements specification |
| `02_SFG_*.md` | Functional specification |
| `03_STB_*.md` | Technical specification |
| `04_DAT_*.md` | Architecture design |
| `05_DCD_*.md` | Detailed design |

## Contact & Resources

- **Project Plan:** `PROJET_VICORE_V2/00_PLAN_PROJET.md`
- **Architecture:** `ARCHITECTURE_DIAGRAMS.md`
- **UI/UX Improvements:** `AMELIORATIONS_UI_UX.md`

---

## Session Context (Last Updated: 2026-01-24)

### Recent Work Completed

#### Sens de Circulation Feature (Direction Indicator)
Added train circulation direction indicator to VICORE V2 mockups and documentation:

**Terminology:**
- **Sens normal** (green badge): Sortie tunnel vers quais - normal direction
- **En tiroir** (yellow badge): Quais vers entrée tunnel - reversed direction

**Key Implementation Details:**
- Direction is **read-only** data from the capture system database
- Each train pass has its own direction value (not a global setting)
- Operators cannot modify the direction - it's metadata from image capture
- Badge displayed on: Dashboard alerts, System View, Car View, Spring History

**Files Modified:**
- `PROJET_VICORE_V2/02_MOCKUPS/css/style.css` - Direction badge styles (.direction-badge.nominal, .direction-badge.inverted)
- `PROJET_VICORE_V2/02_MOCKUPS/00_alerts_dashboard.html` - Per-train-pass direction badges
- `PROJET_VICORE_V2/02_MOCKUPS/02_system_view.html` - Direction badge in train details
- `PROJET_VICORE_V2/02_MOCKUPS/03_car_view.html` - Direction badge in bogie panel
- `PROJET_VICORE_V2/02_MOCKUPS/04_historique_ressort.html` - Direction badge in header

**Documentation Updated:**
- `01_SRS`: Section 5.10 - ENF-DIR-01, ENF-DIR-02 requirements
- `02_SFG`: Section 3.2 mockup, Section 4.11 RG-DIR rules
- `03_STB`: Database schema comments for train_direction column
- `05_DCD`: TrainPass dataclass documentation

**Database Schema:**
```sql
train_direction VARCHAR(10) NOT NULL DEFAULT 'normal'
-- Values: 'normal' (Sens normal) or 'tiroir' (En tiroir)
```

### Deployment Status
- **Mockups deployed** to https://vicore-mockup.vercel.app
- **Git remote:** `vicore-mockup` → `hervelenglin-coder/vicore-mockup.git`
- **Branch mapping:** Push `master:main` for Vercel deployment

### Pending/Future Work
- Implement actual backend for direction data from capture system
- Add direction filtering in train pass list
- Consider direction impact on spring position visualization (Menant/Mené inversion)
