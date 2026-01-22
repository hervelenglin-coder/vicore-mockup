# DCD - Dossier de Conception Detaillee
## VICORE V2 - VIsualisation COntrole REssorts

| Champ | Valeur |
|-------|--------|
| **Version** | 1.0 |
| **Date** | 2026-01-18 |
| **Statut** | En cours de redaction |
| **Auteur** | Equipe Developpement |
| **Validation** | A valider |

---

## Historique des Modifications

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-01-18 | Dev Lead | Creation initiale |

---

## Table des Matieres

1. [Introduction](#1-introduction)
2. [Conception des Modules](#2-conception-des-modules)
3. [Diagrammes de Classes](#3-diagrammes-de-classes)
4. [Diagrammes de Sequences](#4-diagrammes-de-sequences)
5. [Conception Base de Donnees](#5-conception-base-de-donnees)
6. [Conception des APIs](#6-conception-des-apis)
7. [Conception Frontend](#7-conception-frontend)
8. [Gestion des Erreurs](#8-gestion-des-erreurs)
9. [Tests et Validation](#9-tests-et-validation)

---

## 1. Introduction

### 1.1 Objet du Document

Ce document decrit la conception detaillee du systeme VICORE V2. Il fournit les specifications necessaires a l'implementation des differents composants du systeme.

### 1.2 Conventions

| Convention | Description |
|------------|-------------|
| `CamelCase` | Classes et types |
| `snake_case` | Fonctions, variables, fichiers Python |
| `kebab-case` | URLs, fichiers CSS/HTML |
| `SCREAMING_SNAKE` | Constantes |

### 1.3 Documents de Reference

| Reference | Document |
|-----------|----------|
| STB-VICORE-V2 | Specification Technique |
| DAT-VICORE-V2 | Dossier Architecture |
| SFG-VICORE-V2 | Specification Fonctionnelle |

---

## 2. Conception des Modules

### 2.1 Module Auth

#### 2.1.1 Responsabilites

- Authentification des utilisateurs
- Integration SSO Eurotunnel (SAML)
- Verification des permissions
- Gestion des sessions

#### 2.1.2 Structure

```
app/modules/auth/
├── __init__.py          # Blueprint registration
├── routes.py            # HTTP endpoints
├── services.py          # Business logic
├── models.py            # User model
├── schemas.py           # Validation schemas
├── decorators.py        # Auth decorators
└── saml.py              # SSO SAML utilities
```

#### 2.1.3 Classes Principales

```python
# models.py
class User(db.Model):
    """Modele utilisateur (synchronise depuis SSO Eurotunnel)."""

    __tablename__ = 'users'

    id: int                    # Primary key
    sso_id: str                # Identifiant SSO Eurotunnel
    username: str              # Unique username (from SSO)
    email: str                 # Email utilisateur
    display_name: str          # Nom affiche
    role: str                  # admin, operator, viewer (from SSO groups)
    locale: str                # Preference de langue (fr, en)
    is_active: bool            # Account status
    created_at: datetime       # Creation timestamp
    last_login: datetime       # Last login timestamp

    def has_permission(self, permission: str) -> bool:
        """Verifie si l'utilisateur a la permission."""
        return ROLE_PERMISSIONS.get(self.role, []).contains(permission)

    @classmethod
    def from_saml_attributes(cls, saml_attrs: dict) -> 'User':
        """Cree ou met a jour un utilisateur depuis les attributs SAML."""
        return cls(
            sso_id=saml_attrs['NameID'],
            username=saml_attrs.get('sAMAccountName', saml_attrs['NameID']),
            email=saml_attrs.get('mail'),
            display_name=saml_attrs.get('displayName'),
            role=cls._map_sso_groups_to_role(saml_attrs.get('memberOf', []))
        )

    @staticmethod
    def _map_sso_groups_to_role(groups: list) -> str:
        """Mappe les groupes SSO vers un role VICORE."""
        if 'VICORE_ADMINS' in groups:
            return 'admin'
        elif 'VICORE_OPERATORS' in groups:
            return 'operator'
        return 'viewer'
```

```python
# services.py
class SSOAuthService:
    """Service d'authentification SSO Eurotunnel."""

    def __init__(self, user_repository: UserRepository,
                 saml_client: SAMLClient):
        self.user_repo = user_repository
        self.saml_client = saml_client

    def initiate_login(self, return_url: str = None) -> str:
        """Initie le flux SSO et retourne l'URL de redirection."""
        return self.saml_client.create_authn_request(return_url)

    def process_callback(self, saml_response: str) -> User:
        """Traite la reponse SAML et retourne l'utilisateur."""
        # Valider la reponse SAML
        saml_attrs = self.saml_client.validate_response(saml_response)

        if not saml_attrs:
            raise AuthenticationError("Invalid SAML response")

        # Trouver ou creer l'utilisateur
        user = self.user_repo.find_by_sso_id(saml_attrs['NameID'])

        if not user:
            user = User.from_saml_attributes(saml_attrs)
        else:
            # Mettre a jour les attributs depuis le SSO
            user.display_name = saml_attrs.get('displayName', user.display_name)
            user.email = saml_attrs.get('mail', user.email)
            user.role = User._map_sso_groups_to_role(saml_attrs.get('memberOf', []))

        user.last_login = datetime.utcnow()
        self.user_repo.save(user)

        return user

    def logout(self, user: User) -> str:
        """Initie le Single Logout SSO et retourne l'URL."""
        self.token_service.revoke_token(token)

    def refresh_tokens(self, refresh_token: str) -> AuthResult:
        """Renouvelle les tokens avec un refresh token."""
        payload = self.token_service.verify_refresh_token(refresh_token)
        user = self.user_repo.get_by_id(payload['sub'])

        if not user or not user.is_active:
            raise AuthenticationError("Invalid token")

        return AuthResult(
            access_token=self.token_service.create_access_token(user),
            refresh_token=self.token_service.create_refresh_token(user),
            user=user
        )
```

```python
# decorators.py
def require_auth(f):
    """Decorateur pour endpoints authentifies."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            raise AuthenticationError("Missing token")

        try:
            payload = TokenService.verify_access_token(token)
            g.current_user = UserRepository.get_by_id(payload['sub'])
        except TokenExpiredError:
            raise AuthenticationError("Token expired")
        except TokenInvalidError:
            raise AuthenticationError("Invalid token")

        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorateur pour verification de role."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if g.current_user.role not in roles:
                raise AuthorizationError("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated
    return decorator
```

### 2.2 Module Train Passes

#### 2.2.1 Responsabilites

- Gestion des passages de trains
- Confirmation des passages
- Calcul des statistiques
- Notifications

#### 2.2.2 Structure

```
app/modules/train_passes/
├── __init__.py
├── routes.py
├── services.py
├── models.py
├── schemas.py
├── repositories.py
└── events.py
```

#### 2.2.3 Classes Principales

```python
# models.py
class TrainPass(db.Model):
    """Modele passage de train."""

    __tablename__ = 'train_passes'

    id: int
    installation_id: int         # FK vers installations (Voie D, Voie E, etc.)
    passage_time: datetime
    direction: str               # france_uk, uk_france (direction geographique)
    train_direction: str         # 'normal' (Sens normal: sortie tunnel vers quais) ou 'tiroir' (En tiroir: quais vers tunnel)
    train_number: str
    status: str                  # pending, in_progress, confirmed, alert
    created_at: datetime
    updated_at: datetime

    # Relations
    cars = relationship('Car', back_populates='train_pass',
                       cascade='all, delete-orphan')
    confirmations = relationship('Confirmation', back_populates='train_pass')

    @property
    def cars_count(self) -> int:
        return len(self.cars)

    @property
    def alerts_count(self) -> int:
        return sum(c.alerts_count for c in self.cars)

    @property
    def has_pending_alerts(self) -> bool:
        return any(c.has_pending_alerts for c in self.cars)
```

```python
# services.py
class TrainPassService:
    """Service gestion passages trains."""

    def __init__(self, repository: TrainPassRepository,
                 car_service: CarService,
                 alert_service: AlertService,
                 event_bus: EventBus):
        self.repository = repository
        self.car_service = car_service
        self.alert_service = alert_service
        self.event_bus = event_bus

    def get_pending_passes(self, page: int = 1,
                           per_page: int = 20) -> PaginatedResult:
        """Recupere les passages en attente."""
        return self.repository.find_pending(page, per_page)

    def get_pass_details(self, pass_id: int) -> TrainPass:
        """Recupere les details d'un passage avec wagons."""
        train_pass = self.repository.get_with_cars(pass_id)
        if not train_pass:
            raise NotFoundError(f"Train pass {pass_id} not found")
        return train_pass

    def confirm_pass(self, pass_id: int, user: User,
                     notes: str = None) -> TrainPass:
        """Confirme un passage de train."""
        train_pass = self.repository.get_by_id(pass_id)

        if not train_pass:
            raise NotFoundError(f"Train pass {pass_id} not found")

        if train_pass.status == 'confirmed':
            raise BusinessError("Train pass already confirmed")

        # Verifier alertes non acquittees
        pending_alerts = self.alert_service.get_pending_for_train(pass_id)
        if pending_alerts:
            raise BusinessError(
                f"Cannot confirm: {len(pending_alerts)} pending alerts"
            )

        # Confirmer
        train_pass.status = 'confirmed'
        train_pass.updated_at = datetime.utcnow()
        self.repository.save(train_pass)

        # Creer confirmation
        confirmation = Confirmation(
            user_id=user.id,
            train_pass_id=pass_id,
            confirmation_type='train_pass_ok',
            notes=notes
        )
        self.repository.save_confirmation(confirmation)

        # Emettre evenement
        self.event_bus.publish(TrainPassConfirmedEvent(
            train_pass_id=pass_id,
            confirmed_by=user.id
        ))

        return train_pass

    def get_statistics(self, date_from: date,
                       date_to: date) -> TrainPassStats:
        """Calcule les statistiques des passages."""
        return self.repository.calculate_statistics(date_from, date_to)
```

```python
# repositories.py
class TrainPassRepository:
    """Repository pour acces donnees TrainPass."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[TrainPass]:
        return self.session.query(TrainPass).get(id)

    def get_with_cars(self, id: int) -> Optional[TrainPass]:
        return self.session.query(TrainPass)\
            .options(
                joinedload(TrainPass.cars)
                .joinedload(Car.springs)
            )\
            .filter(TrainPass.id == id)\
            .first()

    def find_pending(self, page: int, per_page: int) -> PaginatedResult:
        query = self.session.query(TrainPass)\
            .filter(TrainPass.status.in_(['pending', 'in_progress']))\
            .order_by(TrainPass.passage_time.desc())

        return paginate(query, page, per_page)

    def find_by_filters(self, filters: TrainPassFilters,
                        page: int, per_page: int) -> PaginatedResult:
        query = self.session.query(TrainPass)

        if filters.status:
            query = query.filter(TrainPass.status == filters.status)
        if filters.direction:
            query = query.filter(TrainPass.direction == filters.direction)
        if filters.date_from:
            query = query.filter(TrainPass.passage_time >= filters.date_from)
        if filters.date_to:
            query = query.filter(TrainPass.passage_time <= filters.date_to)

        query = query.order_by(TrainPass.passage_time.desc())
        return paginate(query, page, per_page)

    def save(self, train_pass: TrainPass) -> TrainPass:
        self.session.add(train_pass)
        self.session.commit()
        return train_pass

    def calculate_statistics(self, date_from: date,
                            date_to: date) -> TrainPassStats:
        result = self.session.query(
            func.count(TrainPass.id).label('total'),
            func.count(case(
                (TrainPass.status == 'confirmed', 1)
            )).label('confirmed'),
            func.count(case(
                (TrainPass.status == 'alert', 1)
            )).label('with_alerts')
        ).filter(
            TrainPass.passage_time.between(date_from, date_to)
        ).first()

        return TrainPassStats(
            total=result.total,
            confirmed=result.confirmed,
            with_alerts=result.with_alerts,
            pending=result.total - result.confirmed - result.with_alerts
        )
```

### 2.3 Module Cars

#### 2.3.1 Classes Principales

```python
# models.py
class Car(db.Model):
    """Modele wagon."""

    __tablename__ = 'cars'

    id: int
    train_pass_id: int
    position: int
    rfid: str                  # Identifiant RFID du wagon
    car_type: str              # 'locomotive' (Loco), 'chargeur', 'porteur'
    status: str                # pending, ok, warning, alert
    created_at: datetime
    updated_at: datetime

    # Note: Types de wagon
    # - locomotive: Wagon moteur (affiche "Loco")
    # - chargeur: Wagon chargeur (affiche "Chargeur")
    # - porteur: Wagon porteur standard (affiche "Porteur")

    # Relations
    train_pass = relationship('TrainPass', back_populates='cars')
    springs = relationship('Spring', back_populates='car',
                          cascade='all, delete-orphan')

    @property
    def springs_status(self) -> str:
        """Calcule le statut global des ressorts."""
        if not self.springs:
            return 'unknown'

        statuses = [s.status for s in self.springs]
        if 'critical' in statuses:
            return 'critical'
        if 'warning' in statuses:
            return 'warning'
        if all(s == 'ok' for s in statuses):
            return 'ok'
        return 'unknown'

    @property
    def alerts_count(self) -> int:
        return sum(len(s.alerts) for s in self.springs)

    @property
    def pending_alerts(self) -> List['SpringAlert']:
        alerts = []
        for spring in self.springs:
            alerts.extend([a for a in spring.alerts if not a.is_acknowledged])
        return alerts
```

```python
# services.py
class CarService:
    """Service gestion wagons."""

    def __init__(self, repository: CarRepository,
                 spring_service: SpringService):
        self.repository = repository
        self.spring_service = spring_service

    def get_car_details(self, car_id: int) -> Car:
        """Recupere les details d'un wagon avec ressorts."""
        car = self.repository.get_with_springs(car_id)
        if not car:
            raise NotFoundError(f"Car {car_id} not found")
        return car

    def get_cars_for_train(self, train_pass_id: int) -> List[Car]:
        """Recupere tous les wagons d'un passage."""
        return self.repository.find_by_train_pass(train_pass_id)

    def confirm_car(self, car_id: int, user: User,
                    notes: str = None) -> Car:
        """Confirme l'inspection d'un wagon."""
        car = self.repository.get_by_id(car_id)

        if not car:
            raise NotFoundError(f"Car {car_id} not found")

        # Verifier alertes pendantes
        if car.pending_alerts:
            raise BusinessError("Cannot confirm car with pending alerts")

        car.status = 'ok'
        car.updated_at = datetime.utcnow()

        confirmation = Confirmation(
            user_id=user.id,
            car_id=car_id,
            confirmation_type='car_ok',
            notes=notes
        )

        self.repository.save(car)
        self.repository.save_confirmation(confirmation)

        return car

    def update_spring_data(self, car_id: int,
                           spring_data: List[SpringData]) -> Car:
        """Met a jour les donnees des ressorts."""
        car = self.repository.get_with_springs(car_id)

        for data in spring_data:
            spring = self._find_or_create_spring(car, data)
            self.spring_service.update_measurement(spring, data)

        self.repository.save(car)
        return car
```

### 2.4 Module Springs

#### 2.4.1 Classes Principales

```python
# models.py
class Spring(db.Model):
    """Modele ressort."""

    __tablename__ = 'springs'

    id: int
    car_id: int
    position: int
    side: str                    # left, right
    height_mm: Decimal
    status: str                  # ok, warning, critical, unknown
    created_at: datetime

    # Relations
    car = relationship('Car', back_populates='springs')
    alerts = relationship('SpringAlert', back_populates='spring',
                         cascade='all, delete-orphan')


class SpringAlert(db.Model):
    """Modele alerte ressort."""

    __tablename__ = 'spring_alerts'

    id: int
    spring_id: int
    alert_type: str
    severity: str                # info, warning, critical
    message: str
    is_acknowledged: bool
    acknowledged_by: int
    acknowledged_at: datetime
    created_at: datetime

    # Relations
    spring = relationship('Spring', back_populates='alerts')
    acknowledged_user = relationship('User')
```

```python
# services.py
class SpringService:
    """Service gestion ressorts."""

    THRESHOLDS = {
        'height': {
            'nominal': 150,
            'warning_low': 135,
            'critical_low': 120,
            'warning_high': 165,
            'critical_high': 180
        }
    }

    def __init__(self, repository: SpringRepository,
                 alert_service: AlertService):
        self.repository = repository
        self.alert_service = alert_service

    def update_measurement(self, spring: Spring,
                           data: SpringData) -> Spring:
        """Met a jour une mesure de ressort."""
        spring.height_mm = data.height_mm

        # Evaluer le statut
        new_status = self._evaluate_status(data.height_mm)
        old_status = spring.status

        spring.status = new_status

        # Creer alerte si necessaire
        if new_status in ['warning', 'critical'] and old_status == 'ok':
            self._create_alert(spring, new_status, data.height_mm)

        return spring

    def _evaluate_status(self, height: Decimal) -> str:
        """Evalue le statut selon la hauteur."""
        t = self.THRESHOLDS['height']

        if height < t['critical_low'] or height > t['critical_high']:
            return 'critical'
        if height < t['warning_low'] or height > t['warning_high']:
            return 'warning'
        return 'ok'

    def _create_alert(self, spring: Spring, status: str,
                      height: Decimal) -> SpringAlert:
        """Cree une alerte pour un ressort."""
        t = self.THRESHOLDS['height']

        if height < t['critical_low']:
            alert_type = 'height_critical_low'
            message = f"Spring height critically low: {height}mm"
        elif height > t['critical_high']:
            alert_type = 'height_critical_high'
            message = f"Spring height critically high: {height}mm"
        elif height < t['warning_low']:
            alert_type = 'height_low'
            message = f"Spring height below threshold: {height}mm"
        else:
            alert_type = 'height_high'
            message = f"Spring height above threshold: {height}mm"

        return self.alert_service.create_alert(
            spring_id=spring.id,
            alert_type=alert_type,
            severity=status,
            message=message
        )

    def get_springs_for_car(self, car_id: int) -> List[Spring]:
        """Recupere tous les ressorts d'un wagon."""
        return self.repository.find_by_car(car_id)
```

### 2.5 Module Alerts

#### 2.5.1 Classes Principales

```python
# services.py
class AlertService:
    """Service gestion alertes."""

    def __init__(self, repository: AlertRepository,
                 notification_service: NotificationService):
        self.repository = repository
        self.notification_service = notification_service

    def create_alert(self, spring_id: int, alert_type: str,
                     severity: str, message: str) -> SpringAlert:
        """Cree une nouvelle alerte."""
        alert = SpringAlert(
            spring_id=spring_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            is_acknowledged=False
        )

        self.repository.save(alert)

        # Notification temps reel
        self.notification_service.notify_alert(alert)

        return alert

    def acknowledge_alert(self, alert_id: int, user: User,
                          notes: str = None) -> SpringAlert:
        """Acquitte une alerte."""
        alert = self.repository.get_by_id(alert_id)

        if not alert:
            raise NotFoundError(f"Alert {alert_id} not found")

        if alert.is_acknowledged:
            raise BusinessError("Alert already acknowledged")

        alert.is_acknowledged = True
        alert.acknowledged_by = user.id
        alert.acknowledged_at = datetime.utcnow()

        self.repository.save(alert)

        return alert

    def get_pending_alerts(self, filters: AlertFilters = None,
                          page: int = 1, per_page: int = 20) -> PaginatedResult:
        """Recupere les alertes non acquittees."""
        return self.repository.find_pending(filters, page, per_page)

    def get_pending_for_train(self, train_pass_id: int) -> List[SpringAlert]:
        """Recupere les alertes pendantes pour un passage."""
        return self.repository.find_pending_for_train(train_pass_id)

    def get_alert_statistics(self, date_from: date,
                            date_to: date) -> AlertStats:
        """Calcule les statistiques d'alertes."""
        return self.repository.calculate_statistics(date_from, date_to)
```

### 2.6 Module Monitoring

#### 2.6.1 Classes Principales

```python
# services.py
class MonitoringService:
    """Service monitoring systeme."""

    def __init__(self, heartbeat_client: HeartbeatClient,
                 cache: RedisCache):
        self.heartbeat_client = heartbeat_client
        self.cache = cache

    def get_system_health(self) -> SystemHealth:
        """Recupere l'etat de sante global du systeme."""
        return SystemHealth(
            status=self._get_overall_status(),
            components={
                'database': self._check_database(),
                'redis': self._check_redis(),
                'heartbeat': self._check_heartbeat()
            },
            uptime_seconds=self._get_uptime(),
            version=current_app.config['VERSION']
        )

    def get_heartbeat_status(self) -> HeartbeatStatus:
        """Recupere le statut du heartbeat externe."""
        # Verifier cache
        cached = self.cache.get('heartbeat_status')
        if cached:
            return HeartbeatStatus.from_dict(cached)

        # Appeler service externe
        try:
            response = self.heartbeat_client.ping()
            status = HeartbeatStatus(
                status='ok',
                last_heartbeat=datetime.utcnow(),
                cameras=response.cameras
            )
        except HeartbeatError as e:
            status = HeartbeatStatus(
                status='error',
                error_message=str(e)
            )

        # Mettre en cache
        self.cache.set('heartbeat_status', status.to_dict(), ttl=30)

        return status

    def _check_database(self) -> ComponentStatus:
        """Verifie la connexion base de donnees."""
        try:
            db.session.execute(text('SELECT 1'))
            return ComponentStatus(status='healthy')
        except Exception as e:
            return ComponentStatus(status='unhealthy', error=str(e))

    def _check_redis(self) -> ComponentStatus:
        """Verifie la connexion Redis."""
        try:
            self.cache.ping()
            return ComponentStatus(status='healthy')
        except Exception as e:
            return ComponentStatus(status='unhealthy', error=str(e))

    def _check_heartbeat(self) -> ComponentStatus:
        """Verifie le service heartbeat."""
        status = self.get_heartbeat_status()
        if status.status == 'ok':
            return ComponentStatus(status='healthy')
        return ComponentStatus(status='unhealthy', error=status.error_message)
```

### 2.7 Module Internationalisation (i18n)

#### 2.7.1 Responsabilites

- Gestion des traductions (FR/EN)
- Detection de la langue du navigateur
- Persistance des preferences utilisateur
- Formatage des dates et nombres selon la locale

#### 2.7.2 Structure

```
app/modules/i18n/
├── __init__.py          # Configuration Flask-Babel
├── translations/
│   ├── fr/
│   │   └── LC_MESSAGES/
│   │       └── messages.po
│   └── en/
│       └── LC_MESSAGES/
│           └── messages.po
└── utils.py             # Helpers i18n
```

#### 2.7.3 Configuration

```python
# app/modules/i18n/__init__.py

from flask_babel import Babel, get_locale
from flask import request, g

babel = Babel()

SUPPORTED_LOCALES = ['fr', 'en']
DEFAULT_LOCALE = 'fr'

def init_i18n(app):
    """Initialise l'internationalisation."""
    babel.init_app(app)

    @babel.localeselector
    def get_locale():
        # 1. Preference utilisateur (si connecte)
        if hasattr(g, 'current_user') and g.current_user:
            return g.current_user.locale

        # 2. Parametre URL ?lang=xx
        lang = request.args.get('lang')
        if lang in SUPPORTED_LOCALES:
            return lang

        # 3. Header Accept-Language du navigateur
        return request.accept_languages.best_match(SUPPORTED_LOCALES, DEFAULT_LOCALE)
```

#### 2.7.4 Utilisation dans les Templates

```html
<!-- Jinja2 avec Flask-Babel -->
<h1>{{ _('Welcome to VICORE') }}</h1>
<p>{{ _('Last updated: %(date)s', date=format_datetime(last_update)) }}</p>

<!-- Selecteur de langue -->
<div class="lang-selector">
    <a href="?lang=fr" class="{{ 'active' if get_locale() == 'fr' }}">FR</a>
    <a href="?lang=en" class="{{ 'active' if get_locale() == 'en' }}">EN</a>
</div>
```

#### 2.7.5 Utilisation dans JavaScript (Vue.js)

```javascript
// static/js/i18n.js

const messages = {
    fr: {
        trainPasses: 'Passages de trains',
        springStatus: 'Etat des ressorts',
        confirm: 'Confirmer',
        cancel: 'Annuler',
        alertCritical: 'Alerte critique',
        ok: 'OK',
        warning: 'Attention',
        // ...
    },
    en: {
        trainPasses: 'Train Passes',
        springStatus: 'Spring Status',
        confirm: 'Confirm',
        cancel: 'Cancel',
        alertCritical: 'Critical Alert',
        ok: 'OK',
        warning: 'Warning',
        // ...
    }
};

// Fonction de traduction
function t(key) {
    const locale = document.documentElement.lang || 'fr';
    return messages[locale][key] || key;
}
```

#### 2.7.6 Fichiers de Traduction

```
# translations/fr/LC_MESSAGES/messages.po

msgid "Welcome to VICORE"
msgstr "Bienvenue sur VICORE"

msgid "Train Passes"
msgstr "Passages de trains"

msgid "Spring Status"
msgstr "Etat des ressorts"

msgid "Confirm"
msgstr "Confirmer"

msgid "Cancel"
msgstr "Annuler"

msgid "Critical Alert"
msgstr "Alerte critique"
```

```
# translations/en/LC_MESSAGES/messages.po

msgid "Welcome to VICORE"
msgstr "Welcome to VICORE"

msgid "Train Passes"
msgstr "Train Passes"

msgid "Spring Status"
msgstr "Spring Status"
```

---

### 2.8 Module Historique Ressorts (Spring History)

#### 2.8.1 Responsabilites

- Recherche des passages precedents d'un meme wagon
- Recuperation des images d'un ressort sur plusieurs passages
- Comparaison d'images entre passages

#### 2.8.2 Structure

```
app/modules/spring_history/
    __init__.py
    routes.py
    service.py
    schemas.py
```

#### 2.8.3 Classes Principales

```python
# app/modules/spring_history/service.py

from datetime import datetime, timedelta
from typing import List, Optional
from app.models import Spring, Car, TrainPass
from app.extensions import db

class SpringHistoryService:
    """Service pour l'historique des photos de ressorts."""

    MAX_DAYS = 90
    DEFAULT_DAYS = 30
    MAX_RESULTS = 50

    @staticmethod
    def get_spring_history(
        wagon_rfid: str,
        bogie: int,
        axle: int,
        position: str,
        days: int = DEFAULT_DAYS,
        limit: int = 20
    ) -> dict:
        """
        Recupere l'historique des photos d'un ressort.

        Args:
            wagon_rfid: Identifiant RFID du wagon
            bogie: Numero du bogie (1 ou 2)
            axle: Numero de l'essieu
            position: Position (L ou R)
            days: Nombre de jours d'historique
            limit: Nombre max de passages

        Returns:
            dict avec spring_id, identifiants et liste des passages
        """
        days = min(days, SpringHistoryService.MAX_DAYS)
        limit = min(limit, SpringHistoryService.MAX_RESULTS)

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Recherche des passages avec ce wagon
        passages = db.session.query(
            TrainPass, Car, Spring
        ).join(
            Car, TrainPass.id == Car.train_pass_id
        ).join(
            Spring, Car.id == Spring.car_id
        ).filter(
            Car.rfid == wagon_rfid,
            Spring.bogie == bogie,
            Spring.axle == axle,
            Spring.position == position,
            TrainPass.passage_time >= cutoff_date
        ).order_by(
            TrainPass.passage_time.desc()
        ).limit(limit).all()

        return {
            'spring_id': f"W{wagon_rfid}_B{bogie}_A{axle}_{position}",
            'wagon_rfid': wagon_rfid,
            'bogie': bogie,
            'axle': axle,
            'position': position,
            'history': [
                SpringHistoryService._format_passage(tp, car, spring)
                for tp, car, spring in passages
            ],
            'total_passages': len(passages)
        }

    @staticmethod
    def _format_passage(train_pass: TrainPass, car: Car, spring: Spring) -> dict:
        """Formate un passage pour la reponse."""
        confirmation = spring.get_last_confirmation()
        return {
            'train_pass_id': train_pass.id,
            'train_code': train_pass.train_number,
            'passage_date': train_pass.passage_time.isoformat(),
            'conf_code': spring.conf_code,
            'status': SpringHistoryService._get_status(spring.conf_code),
            'image_url': spring.image_path,
            'confirmed_by': confirmation.user.display_name if confirmation else None,
            'confirmed_at': confirmation.confirmed_at.isoformat() if confirmation else None,
            'confirmation': confirmation.confirmation_value if confirmation else None
        }

    @staticmethod
    def _get_status(conf_code: int) -> str:
        """Convertit le conf_code en statut lisible."""
        statuses = {0: 'confirmed_ok', 1: 'ok', 2: 'uncertain', 3: 'anomaly', 5: 'missing'}
        return statuses.get(conf_code, 'unknown')
```

```python
# app/modules/spring_history/routes.py

from flask import Blueprint, request
from flask_login import login_required
from app.modules.spring_history.service import SpringHistoryService
from app.modules.spring_history.schemas import SpringHistoryQuerySchema
from app.utils.response import api_response

bp = Blueprint('spring_history', __name__, url_prefix='/api/v1/springs')

@bp.route('/<spring_id>/history', methods=['GET'])
@login_required
def get_spring_history(spring_id: str):
    """GET /api/v1/springs/{spring_id}/history"""
    # Parse spring_id: W1234_B1_A1_L
    parts = spring_id.split('_')
    wagon_rfid = parts[0][1:]  # Remove 'W' prefix
    bogie = int(parts[1][1:])  # Remove 'B' prefix
    axle = int(parts[2][1:])   # Remove 'A' prefix
    position = parts[3]

    schema = SpringHistoryQuerySchema()
    params = schema.load(request.args)

    history = SpringHistoryService.get_spring_history(
        wagon_rfid=wagon_rfid,
        bogie=bogie,
        axle=axle,
        position=position,
        days=params.get('days', 30),
        limit=params.get('limit', 20)
    )

    return api_response(data=history)
```

---

### 2.9 Module Annulation Confirmations

#### 2.9.1 Responsabilites

- Annulation de confirmations de ressorts manquants
- Validation des regles metier (delai 24h, motif obligatoire)
- Notification au superviseur
- Tracabilite complete

#### 2.9.2 Structure

```
app/modules/cancellation/
    __init__.py
    routes.py
    service.py
    schemas.py
    notifications.py
```

#### 2.9.3 Classes Principales

```python
# app/modules/cancellation/service.py

from datetime import datetime, timedelta
from typing import Optional
from flask import g
from app.models import Confirmation, ConfirmationCancellation, Spring, User
from app.extensions import db
from app.modules.cancellation.notifications import notify_supervisor
from app.modules.audit.service import AuditService

class CancellationService:
    """Service pour l'annulation des confirmations."""

    CANCELLATION_WINDOW_HOURS = 24
    MIN_REASON_LENGTH = 10

    @staticmethod
    def cancel_confirmation(
        spring_id: str,
        train_pass_id: int,
        reason: str,
        user: User
    ) -> dict:
        """
        Annule une confirmation de ressort manquant.

        Args:
            spring_id: Identifiant du ressort
            train_pass_id: ID du passage
            reason: Motif d'annulation
            user: Utilisateur effectuant l'annulation

        Returns:
            dict avec les details de l'annulation

        Raises:
            ValidationError: Si les regles metier ne sont pas respectees
        """
        # Validation du motif
        if len(reason.strip()) < CancellationService.MIN_REASON_LENGTH:
            raise ValidationError(f"Le motif doit contenir au moins {CancellationService.MIN_REASON_LENGTH} caracteres")

        # Recherche de la confirmation
        confirmation = Confirmation.query.filter_by(
            spring_id=spring_id,
            train_pass_id=train_pass_id,
            confirmation_type='spring_missing',
            is_cancelled=False
        ).first()

        if not confirmation:
            raise NotFoundError("Confirmation non trouvee ou deja annulee")

        # Verification du delai
        cutoff = datetime.utcnow() - timedelta(hours=CancellationService.CANCELLATION_WINDOW_HOURS)
        if confirmation.confirmed_at < cutoff:
            raise ValidationError("Annulation impossible: delai de 24h depasse")

        # Creation de l'annulation
        cancellation = ConfirmationCancellation(
            confirmation_id=confirmation.id,
            cancelled_by=user.id,
            reason=reason.strip()
        )

        # Mise a jour de la confirmation
        confirmation.is_cancelled = True

        # Reinitialisation du statut du ressort
        spring = Spring.query.get(confirmation.spring_id)
        old_conf_code = spring.conf_code
        spring.conf_code = 3  # Retour a l'etat "anomalie"

        db.session.add(cancellation)
        db.session.commit()

        # Notification au superviseur
        notification_sent = notify_supervisor(
            cancellation=cancellation,
            spring=spring,
            cancelled_by=user
        )

        if notification_sent:
            cancellation.notified_supervisor = True
            cancellation.notification_sent_at = datetime.utcnow()
            db.session.commit()

        # Audit trail
        AuditService.log_operation(
            user_id=user.id,
            action='cancellation',
            entity_type='confirmation',
            entity_id=confirmation.id,
            old_values={'conf_code': old_conf_code, 'is_cancelled': False},
            new_values={'conf_code': 3, 'is_cancelled': True, 'reason': reason}
        )

        return {
            'spring_id': spring_id,
            'previous_status': 'missing',
            'new_status': 'pending',
            'cancelled_by': user.display_name,
            'cancelled_at': cancellation.cancelled_at.isoformat(),
            'reason': reason,
            'notification_sent': notification_sent
        }
```

```python
# app/modules/cancellation/notifications.py

from flask import current_app
from app.models import User, ConfirmationCancellation, Spring
from app.utils.email import send_email

def notify_supervisor(
    cancellation: ConfirmationCancellation,
    spring: Spring,
    cancelled_by: User
) -> bool:
    """
    Notifie les superviseurs d'une annulation.

    Returns:
        True si la notification a ete envoyee
    """
    supervisors = User.query.filter_by(role='supervisor', is_active=True).all()

    if not supervisors:
        return False

    subject = f"[VICORE] Annulation de confirmation - {spring.id}"

    body = f"""
    Une confirmation de ressort manquant a ete annulee.

    Details:
    - Ressort: {spring.id}
    - Wagon: {spring.car.rfid}
    - Annule par: {cancelled_by.display_name}
    - Date: {cancellation.cancelled_at.strftime('%d/%m/%Y %H:%M')}
    - Motif: {cancellation.reason}

    Veuillez verifier cette annulation dans l'interface VICORE.
    """

    for supervisor in supervisors:
        try:
            send_email(
                to=supervisor.email,
                subject=subject,
                body=body
            )
        except Exception as e:
            current_app.logger.error(f"Erreur notification superviseur: {e}")

    return True
```

---

### 2.10 Module Audit Trail

#### 2.10.1 Responsabilites

- Enregistrement de toutes les operations
- Consultation de l'historique
- Export des logs d'audit
- Retention et purge automatique

#### 2.10.2 Structure

```
app/modules/audit/
    __init__.py
    routes.py
    service.py
    schemas.py
    export.py
```

#### 2.10.3 Classes Principales

```python
# app/modules/audit/service.py

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from flask import request, g
from app.models import AuditLog, User
from app.extensions import db
from sqlalchemy import and_, or_

class AuditService:
    """Service pour l'audit trail."""

    DEFAULT_RETENTION_DAYS = 365

    @staticmethod
    def log_operation(
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None
    ) -> AuditLog:
        """
        Enregistre une operation dans l'audit trail.
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request else None,
            session_id=g.get('session_id')
        )

        db.session.add(audit_log)
        db.session.commit()

        return audit_log

    @staticmethod
    def get_operations(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Dict:
        """
        Recupere l'historique des operations avec filtres.
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        query = AuditLog.query.filter(
            AuditLog.created_at.between(start_date, end_date)
        )

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if operation_type:
            query = query.filter(AuditLog.action == operation_type)

        query = query.order_by(AuditLog.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page)

        return {
            'operations': [
                AuditService._format_operation(op) for op in pagination.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'total_pages': pagination.pages
            }
        }

    @staticmethod
    def _format_operation(audit_log: AuditLog) -> Dict:
        """Formate un log d'audit pour la reponse API."""
        user = User.query.get(audit_log.user_id)
        return {
            'id': audit_log.id,
            'timestamp': audit_log.created_at.isoformat(),
            'user_id': audit_log.user_id,
            'username': user.username if user else None,
            'display_name': user.display_name if user else None,
            'operation_type': audit_log.action,
            'target_type': audit_log.entity_type,
            'target_id': audit_log.entity_id,
            'details': audit_log.new_values,
            'ip_address': str(audit_log.ip_address) if audit_log.ip_address else None,
            'user_agent': audit_log.user_agent
        }

    @staticmethod
    def get_operation_detail(operation_id: int) -> Dict:
        """Recupere les details complets d'une operation."""
        audit_log = AuditLog.query.get_or_404(operation_id)
        user = User.query.get(audit_log.user_id)

        return {
            'id': audit_log.id,
            'timestamp': audit_log.created_at.isoformat(),
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'role': user.role
            } if user else None,
            'operation_type': audit_log.action,
            'target': {
                'type': audit_log.entity_type,
                'id': audit_log.entity_id
            },
            'details': {
                'old_values': audit_log.old_values,
                'new_values': audit_log.new_values
            },
            'metadata': {
                'ip_address': str(audit_log.ip_address) if audit_log.ip_address else None,
                'user_agent': audit_log.user_agent,
                'session_id': audit_log.session_id
            }
        }
```

```python
# app/modules/audit/export.py

import csv
import io
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class AuditExporter:
    """Export des logs d'audit en differents formats."""

    @staticmethod
    def export_csv(operations: List[dict]) -> str:
        """Exporte en CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        # En-tetes
        writer.writerow([
            'Date/Heure', 'Utilisateur', 'Type', 'Cible', 'Details', 'IP'
        ])

        for op in operations:
            writer.writerow([
                op['timestamp'],
                op['display_name'] or op['username'],
                op['operation_type'],
                f"{op['target_type']}:{op['target_id']}",
                str(op['details']),
                op['ip_address']
            ])

        return output.getvalue()

    @staticmethod
    def export_pdf(operations: List[dict], title: str = "Audit Trail") -> bytes:
        """Exporte en PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = []

        # Titre
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(f"Genere le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

        # Tableau
        data = [['Date', 'Utilisateur', 'Type', 'Cible']]
        for op in operations[:100]:  # Limite pour le PDF
            data.append([
                op['timestamp'][:19],
                op['display_name'] or op['username'],
                op['operation_type'],
                f"{op['target_type']}"
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)
        doc.build(elements)

        return buffer.getvalue()
```

---

### 2.11 Module Rapports

#### 2.11.1 Responsabilites

- Generation de rapports d'operations
- Calcul des statistiques
- Generation asynchrone pour les grandes periodes
- Stockage et gestion des rapports generes

#### 2.11.2 Structure

```
app/modules/reports/
    __init__.py
    routes.py
    service.py
    schemas.py
    generator.py
    tasks.py      # Taches Celery pour generation async
```

#### 2.11.3 Classes Principales

```python
# app/modules/reports/service.py

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid
from app.models import Report, AuditLog, User
from app.extensions import db
from sqlalchemy import func

class ReportService:
    """Service pour la generation de rapports."""

    MAX_PERIOD_DAYS = 90
    ASYNC_THRESHOLD_DAYS = 30
    REPORT_RETENTION_DAYS = 90

    @staticmethod
    def generate_report_id() -> str:
        """Genere un ID unique pour le rapport."""
        return f"rpt_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def create_report(
        user: User,
        start_date: datetime,
        end_date: datetime,
        report_type: str,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Cree et genere un rapport.
        """
        # Validation periode
        days = (end_date - start_date).days
        if days > ReportService.MAX_PERIOD_DAYS:
            raise ValidationError(f"Periode maximale: {ReportService.MAX_PERIOD_DAYS} jours")

        report_id = ReportService.generate_report_id()

        report = Report(
            id=report_id,
            created_by=user.id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            filters=filters,
            expires_at=datetime.utcnow() + timedelta(days=ReportService.REPORT_RETENTION_DAYS)
        )

        db.session.add(report)
        db.session.commit()

        # Generation synchrone ou asynchrone selon la periode
        if days > ReportService.ASYNC_THRESHOLD_DAYS:
            # Lancer tache Celery
            from app.modules.reports.tasks import generate_report_async
            generate_report_async.delay(report_id)

            report.status = 'processing'
            db.session.commit()

            return {
                'report_id': report_id,
                'status': 'processing',
                'estimated_completion': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
                'notification_email': user.email
            }
        else:
            # Generation immediate
            return ReportService._generate_report_sync(report)

    @staticmethod
    def _generate_report_sync(report: Report) -> Dict:
        """Genere le rapport de maniere synchrone."""
        # Calcul des statistiques
        stats = ReportService._calculate_statistics(
            report.start_date,
            report.end_date,
            report.filters
        )

        report.summary_data = stats
        report.status = 'completed'
        report.completed_at = datetime.utcnow()

        # Generation des fichiers
        from app.modules.reports.generator import ReportGenerator
        generator = ReportGenerator(report, stats)

        report.file_path_pdf = generator.generate_pdf()
        report.file_path_csv = generator.generate_csv()
        report.file_path_xlsx = generator.generate_xlsx()

        db.session.commit()

        return {
            'report_id': report.id,
            'status': 'completed',
            'created_at': report.created_at.isoformat(),
            'summary': stats,
            'download_urls': {
                'pdf': f"/api/v1/reports/{report.id}/download?format=pdf",
                'csv': f"/api/v1/reports/{report.id}/download?format=csv",
                'xlsx': f"/api/v1/reports/{report.id}/download?format=xlsx"
            }
        }

    @staticmethod
    def _calculate_statistics(
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Calcule les statistiques pour le rapport."""
        query = AuditLog.query.filter(
            AuditLog.created_at.between(start_date, end_date)
        )

        if filters and filters.get('user_id'):
            query = query.filter(AuditLog.user_id == filters['user_id'])

        if filters and filters.get('operation_types'):
            query = query.filter(AuditLog.action.in_(filters['operation_types']))

        # Comptage par type
        by_type = db.session.query(
            AuditLog.action,
            func.count(AuditLog.id)
        ).filter(
            AuditLog.created_at.between(start_date, end_date)
        ).group_by(AuditLog.action).all()

        # Utilisateurs actifs
        active_users = db.session.query(
            func.count(func.distinct(AuditLog.user_id))
        ).filter(
            AuditLog.created_at.between(start_date, end_date)
        ).scalar()

        total = sum(count for _, count in by_type)

        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            'total_operations': total,
            'operations_by_type': {action: count for action, count in by_type},
            'active_users': active_users
        }

    @staticmethod
    def list_user_reports(user_id: int) -> List[Dict]:
        """Liste les rapports d'un utilisateur."""
        reports = Report.query.filter_by(
            created_by=user_id
        ).order_by(
            Report.created_at.desc()
        ).limit(20).all()

        return [
            {
                'report_id': r.id,
                'created_at': r.created_at.isoformat(),
                'period': f"{r.start_date} - {r.end_date}",
                'report_type': r.report_type,
                'status': r.status,
                'expires_at': r.expires_at.isoformat() if r.expires_at else None
            }
            for r in reports
        ]
```

```python
# app/modules/reports/tasks.py

from celery import shared_task
from app.modules.reports.service import ReportService
from app.models import Report
from app.extensions import db
from app.utils.email import send_email

@shared_task
def generate_report_async(report_id: str):
    """Tache Celery pour generation asynchrone de rapport."""
    report = Report.query.get(report_id)

    if not report:
        return

    try:
        result = ReportService._generate_report_sync(report)

        # Notification email
        user = report.user
        if user and user.email:
            send_email(
                to=user.email,
                subject=f"[VICORE] Rapport {report_id} disponible",
                body=f"""
                Votre rapport a ete genere avec succes.

                Periode: {report.start_date} - {report.end_date}
                Type: {report.report_type}

                Connectez-vous a VICORE pour telecharger le rapport.
                """
            )
    except Exception as e:
        report.status = 'failed'
        report.error_message = str(e)
        db.session.commit()
```

### 2.12 Module Conditions Environnementales

#### 2.12.1 Responsabilites

- Collecte des conditions environnementales au moment du passage
- Agregation des donnees depuis plusieurs sources
- Calcul du score de qualite des conditions
- Generation d'alertes si conditions defavorables
- Affichage des conditions dans l'interface

#### 2.12.2 Structure

```
app/modules/conditions/
├── __init__.py          # Blueprint registration
├── routes.py            # HTTP endpoints
├── services.py          # Business logic principale
├── models.py            # TrainPassConditions model
├── schemas.py           # Validation schemas
├── sources/             # Sources de donnees
│   ├── __init__.py
│   ├── daylight.py      # Calcul jour/nuit (astral)
│   ├── weather_api.py   # API meteo externe
│   ├── site_sensors.py  # Capteurs sur site
│   ├── camera_meta.py   # Metadonnees camera
│   └── rfid_speed.py    # Vitesse train RFID
└── analyzers/
    ├── __init__.py
    └── image_quality.py # Analyse qualite image IA
```

#### 2.12.3 Classes Principales

```python
# models.py
class TrainPassConditions(db.Model):
    """Conditions environnementales d'un passage de train."""

    __tablename__ = 'train_pass_conditions'

    id: int
    train_pass_id: int        # FK vers train_passes

    # Conditions temporelles
    is_daylight: bool         # Jour ou nuit
    sun_altitude: float       # Altitude du soleil en degres

    # Conditions meteo
    temperature_c: float      # Temperature en Celsius
    humidity_pct: int         # Humidite en %
    precipitation: bool       # Precipitation detectee
    visibility_m: int         # Visibilite en metres
    weather_code: str         # 'clear', 'cloudy', 'rain', 'fog', 'snow'

    # Conditions operationnelles
    train_speed_kmh: float    # Vitesse du train

    # Qualite camera
    exposure_ok: bool         # Exposition correcte
    image_quality: float      # Score 0-1

    # Alertes
    conditions_alert: bool    # Alerte conditions defavorables
    alert_reasons: list       # Raisons de l'alerte

    # Metadonnees
    data_sources: list        # Sources utilisees
    created_at: datetime

    @property
    def quality_score(self) -> float:
        """Calcule le score global de qualite des conditions."""
        score = 1.0

        # Penalites selon les conditions
        if not self.is_daylight:
            score -= 0.15
        if self.visibility_m and self.visibility_m < 500:
            score -= 0.3
        if self.precipitation:
            score -= 0.2
        if self.train_speed_kmh and self.train_speed_kmh > 80:
            score -= 0.1
        if self.image_quality:
            score = min(score, self.image_quality)

        return max(0, score)

    @property
    def is_optimal(self) -> bool:
        """Les conditions sont-elles optimales pour l'analyse."""
        return self.quality_score >= 0.8
```

```python
# services.py
class ConditionsService:
    """Service de gestion des conditions environnementales."""

    def __init__(self,
                 daylight_source: DaylightSource,
                 weather_source: WeatherSource,
                 camera_source: CameraMetadataSource,
                 rfid_source: RFIDSpeedSource,
                 sensor_source: SiteSensorSource = None):
        self.daylight = daylight_source
        self.weather = weather_source
        self.camera = camera_source
        self.rfid = rfid_source
        self.sensors = sensor_source

    async def collect_conditions(self, train_pass: TrainPass) -> TrainPassConditions:
        """Collecte toutes les conditions pour un passage."""
        conditions = TrainPassConditions(train_pass_id=train_pass.id)
        sources_used = []

        # 1. Calcul jour/nuit (toujours disponible)
        daylight_data = self.daylight.calculate(
            passage_time=train_pass.passage_time,
            site_code=train_pass.installation.code
        )
        conditions.is_daylight = daylight_data['is_daylight']
        conditions.sun_altitude = daylight_data['sun_altitude']
        sources_used.append('timestamp')

        # 2. Vitesse train (systeme RFID)
        try:
            speed = self.rfid.get_speed(train_pass.id)
            conditions.train_speed_kmh = speed
            sources_used.append('rfid')
        except Exception:
            pass  # Source non disponible

        # 3. Metadonnees camera
        try:
            camera_data = self.camera.extract(train_pass.images[0])
            conditions.exposure_ok = camera_data['exposure_ok']
            conditions.image_quality = camera_data['quality_score']
            sources_used.append('camera_metadata')
        except Exception:
            pass

        # 4. Capteurs sur site (prioritaires si disponibles)
        if self.sensors:
            try:
                sensor_data = self.sensors.get_conditions(
                    train_pass.installation.code
                )
                conditions.visibility_m = sensor_data.get('visibility_m')
                conditions.precipitation = sensor_data.get('precipitation', False)
                conditions.temperature_c = sensor_data.get('temperature_c')
                sources_used.append('site_sensors')
            except Exception:
                pass

        # 5. API meteo (si pas de capteurs site)
        if 'site_sensors' not in sources_used:
            try:
                weather_data = await self.weather.get_current(
                    lat=train_pass.installation.latitude,
                    lon=train_pass.installation.longitude
                )
                conditions.temperature_c = conditions.temperature_c or weather_data['temperature_c']
                conditions.visibility_m = conditions.visibility_m or weather_data['visibility_m']
                conditions.precipitation = conditions.precipitation or weather_data['precipitation']
                conditions.weather_code = weather_data['conditions']
                sources_used.append('api_meteo')
            except Exception:
                pass

        # Calculer alertes
        conditions.data_sources = sources_used
        self._evaluate_alerts(conditions)

        return conditions

    def _evaluate_alerts(self, conditions: TrainPassConditions):
        """Evalue si des alertes conditions sont necessaires."""
        alerts = []

        if conditions.visibility_m and conditions.visibility_m < 200:
            alerts.append('Brouillard detecte (visibilite < 200m)')

        if conditions.precipitation:
            alerts.append('Precipitation detectee')

        if not conditions.is_daylight:
            alerts.append('Passage de nuit')

        if conditions.image_quality and conditions.image_quality < 0.6:
            alerts.append('Qualite image insuffisante')

        if conditions.train_speed_kmh and conditions.train_speed_kmh > 80:
            alerts.append(f'Vitesse elevee ({conditions.train_speed_kmh} km/h)')

        conditions.conditions_alert = len(alerts) > 0
        conditions.alert_reasons = alerts

    def get_conditions(self, train_pass_id: int) -> dict:
        """Retourne les conditions pour affichage."""
        conditions = TrainPassConditions.query.filter_by(
            train_pass_id=train_pass_id
        ).first()

        if not conditions:
            return None

        return {
            'train_pass_id': train_pass_id,
            'conditions': {
                'daylight': {
                    'is_day': conditions.is_daylight,
                    'sun_altitude': conditions.sun_altitude
                },
                'weather': {
                    'temperature_c': conditions.temperature_c,
                    'conditions': conditions.weather_code,
                    'precipitation': conditions.precipitation,
                    'visibility_m': conditions.visibility_m
                },
                'operational': {
                    'train_speed_kmh': conditions.train_speed_kmh
                },
                'camera': {
                    'exposure_ok': conditions.exposure_ok,
                    'image_quality': conditions.image_quality
                }
            },
            'quality_assessment': {
                'overall_score': conditions.quality_score,
                'is_optimal': conditions.is_optimal,
                'alerts': conditions.alert_reasons or []
            },
            'data_sources': conditions.data_sources
        }
```

```python
# sources/daylight.py
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime

# Coordonnees des sites
SITE_LOCATIONS = {
    'VOIE_D': LocationInfo('Folkestone', 'England', 'Europe/London', 51.0847, 1.1167),
    'VOIE_E': LocationInfo('Coquelles', 'France', 'Europe/Paris', 50.9281, 1.8125)
}

class DaylightSource:
    """Calcul jour/nuit depuis l'horodatage."""

    def calculate(self, passage_time: datetime, site_code: str) -> dict:
        """
        Calcule si le passage est de jour ou de nuit.

        Returns:
            {
                'is_daylight': bool,
                'sun_altitude': float,
                'civil_twilight': bool
            }
        """
        location = SITE_LOCATIONS.get(site_code)
        if not location:
            # Par defaut, utiliser Coquelles
            location = SITE_LOCATIONS['VOIE_E']

        s = sun(location.observer, date=passage_time.date())

        sunrise = s['sunrise']
        sunset = s['sunset']
        dawn = s['dawn']
        dusk = s['dusk']

        is_daylight = sunrise <= passage_time.replace(tzinfo=sunrise.tzinfo) <= sunset
        civil_twilight = dawn <= passage_time.replace(tzinfo=dawn.tzinfo) <= dusk

        # Calcul altitude approximatif
        # (simplification - pour precision utiliser elevation())
        if is_daylight:
            midday = s['noon']
            hours_from_noon = abs((passage_time.hour + passage_time.minute/60) - 12)
            sun_altitude = max(0, 45 - hours_from_noon * 7.5)  # Approximation
        else:
            sun_altitude = -10  # Sous l'horizon

        return {
            'is_daylight': is_daylight,
            'sun_altitude': sun_altitude,
            'civil_twilight': civil_twilight
        }
```

```python
# sources/weather_api.py
import aiohttp
from typing import Optional

class WeatherAPISource:
    """Integration API meteo externe (OpenWeatherMap ou MeteoFrance)."""

    def __init__(self, api_key: str, provider: str = 'openweathermap'):
        self.api_key = api_key
        self.provider = provider
        self.base_urls = {
            'openweathermap': 'https://api.openweathermap.org/data/2.5/weather',
            'meteofrance': 'https://api.meteo.fr/v1/current'
        }

    async def get_current(self, lat: float, lon: float) -> Optional[dict]:
        """
        Recupere les conditions meteo actuelles.

        Returns:
            {
                'temperature_c': float,
                'humidity_pct': int,
                'precipitation': bool,
                'visibility_m': int,
                'conditions': str
            }
        """
        if self.provider == 'openweathermap':
            return await self._fetch_openweathermap(lat, lon)
        else:
            return await self._fetch_meteofrance(lat, lon)

    async def _fetch_openweathermap(self, lat: float, lon: float) -> dict:
        """Fetch depuis OpenWeatherMap API."""
        url = f"{self.base_urls['openweathermap']}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

        return {
            'temperature_c': data['main']['temp'],
            'humidity_pct': data['main']['humidity'],
            'precipitation': data['weather'][0]['main'] in ['Rain', 'Snow', 'Drizzle'],
            'visibility_m': data.get('visibility', 10000),
            'conditions': self._map_conditions(data['weather'][0]['main'])
        }

    def _map_conditions(self, owm_condition: str) -> str:
        """Mappe les conditions OWM vers nos codes."""
        mapping = {
            'Clear': 'clear',
            'Clouds': 'cloudy',
            'Rain': 'rain',
            'Drizzle': 'rain',
            'Snow': 'snow',
            'Fog': 'fog',
            'Mist': 'fog',
            'Haze': 'fog'
        }
        return mapping.get(owm_condition, 'unknown')
```

#### 2.12.4 Configuration

```python
# config/conditions.py

CONDITIONS_CONFIG = {
    # Sources de donnees
    'sources': {
        'daylight': {
            'enabled': True,
            'library': 'astral'
        },
        'rfid': {
            'enabled': True,
            'endpoint': '${RFID_API_ENDPOINT}'
        },
        'camera_metadata': {
            'enabled': True,
            'extract_exif': True
        },
        'site_sensors': {
            'enabled': False,  # A activer si capteurs installes
            'endpoint': '${SENSORS_API_ENDPOINT}'
        },
        'weather_api': {
            'enabled': True,
            'provider': 'openweathermap',
            'api_key': '${WEATHER_API_KEY}',
            'cache_ttl': 300  # 5 minutes
        }
    },

    # Seuils d'alerte
    'thresholds': {
        'visibility_poor': 200,      # metres
        'visibility_moderate': 500,
        'speed_high': 80,            # km/h
        'temperature_frost': 2,      # Celsius
        'temperature_heat': 35,
        'image_quality_poor': 0.6
    },

    # Cache Redis
    'cache': {
        'enabled': True,
        'ttl': 3600,  # 1 heure
        'key_prefix': 'vicore:conditions:'
    }
}
```

---

## 3. Diagrammes de Classes

### 3.1 Domaine Principal

```
+-------------------+         +-------------------+
|       User        |         |   TrainPass       |
+-------------------+         +-------------------+
| -id: int          |         | -id: int          |
| -sso_id: str      |         | -passage_time: dt |
| -username: str    |         | -direction: str   |
| -role: str        |         | -train_number: str|
| -is_active: bool  |         | -status: str      |
+-------------------+         +-------------------+
| +has_permission() |         | +cars_count       |
| +from_saml_attrs()|    1    | +alerts_count     |
|                   |<------->| +has_pending()    |
+-------------------+    *    +-------------------+
                                      |
                                      | 1
                                      |
                                      | *
                              +-------------------+
                              |       Car         |
                              +-------------------+
                              | -id: int          |
                              | -position: int    |
                              | -car_type: str    |
                              | -status: str      |
                              +-------------------+
                              | +springs_status   |
                              | +alerts_count     |
                              | +pending_alerts   |
                              +-------------------+
                                      |
                                      | 1
                                      |
                                      | *
                              +-------------------+
                              |      Spring       |
                              +-------------------+
                              | -id: int          |
                              | -position: int    |
                              | -side: str        |
                              | -height_mm: dec   |
                              | -status: str      |
                              +-------------------+
                                      |
                                      | 1
                                      |
                                      | *
                              +-------------------+
                              |   SpringAlert     |
                              +-------------------+
                              | -id: int          |
                              | -alert_type: str  |
                              | -severity: str    |
                              | -message: str     |
                              | -is_acknowledged  |
                              +-------------------+
```

### 3.2 Services

```
+-------------------------+
|     SSOAuthService      |
+-------------------------+
| -user_repo              |
| -saml_client            |
+-------------------------+
| +initiate_login()       |
| +process_callback()     |
| +logout()               |
+-------------------------+

+-------------------------+         +-------------------------+
|   TrainPassService      |-------->|      CarService         |
+-------------------------+         +-------------------------+
| -repository             |         | -repository             |
| -car_service            |         | -spring_service         |
| -alert_service          |         +-------------------------+
| -event_bus              |         | +get_car_details()      |
+-------------------------+         | +get_cars_for_train()   |
| +get_pending_passes()   |         | +confirm_car()          |
| +get_pass_details()     |         +-------------------------+
| +confirm_pass()         |                   |
| +get_statistics()       |                   |
+-------------------------+                   v
            |                       +-------------------------+
            |                       |     SpringService       |
            v                       +-------------------------+
+-------------------------+         | -repository             |
|     AlertService        |<--------| -alert_service          |
+-------------------------+         +-------------------------+
| -repository             |         | +update_measurement()   |
| -notification_service   |         | +get_springs_for_car()  |
+-------------------------+         +-------------------------+
| +create_alert()         |
| +acknowledge_alert()    |
| +get_pending_alerts()   |
+-------------------------+
```

---

## 4. Diagrammes de Sequences

### 4.1 Sequence: Authentification

```
User        Browser       SSOController    SSOService    UserRepo    SSO Eurotunnel
 |             |               |                |             |             |
 |--Acces VICORE->             |                |             |             |
 |             |--GET /------->|                |             |             |
 |             |               |--check session-|             |             |
 |             |               |  (no session)  |             |             |
 |             |               |                |             |             |
 |             |               |--initiate_login()----------->|             |
 |             |               |                |--create SAML AuthnRequest->|
 |             |<--302 Redirect to SSO----------|             |             |
 |             |                                              |             |
 |             |--Login on SSO Portal------------------------->             |
 |             |<--SAML Response (POST callback)--------------|             |
 |             |                                              |             |
 |             |--POST /auth/sso/callback---->|               |             |
 |             |               |--process_callback()--------->|             |
 |             |               |                |--validate SAML----------->|
 |             |               |                |<--saml_attrs--------------|
 |             |               |                |--find_by_sso_id()-------->|
 |             |               |                |<--user (or null)----------|
 |             |               |                |--create/update user------>|
 |             |               |                |             |             |
 |             |               |<--User---------|             |             |
 |             |               |--create session|             |             |
 |             |<--302 Redirect + Session Cookie|             |             |
 |<--System View|              |                |             |             |
 |             |               |                |             |             |
```

### 4.2 Sequence: Consultation Passage

```
User      Browser      TrainPassCtrl    TrainPassSvc    TrainPassRepo    Cache
 |           |              |                |               |             |
 |--Click--->|              |                |               |             |
 |           |--GET /train-passes/{id}------>|               |             |
 |           |              |                |               |             |
 |           |              |--get_details()->               |             |
 |           |              |                |--get_with_cars()----------->|
 |           |              |                |<--train_pass----------------|
 |           |              |                |               |             |
 |           |              |<--train_pass---|               |             |
 |           |<--200 + JSON-|                |               |             |
 |           |              |                |               |             |
 |<--Render--|              |                |               |             |
 |           |              |                |               |             |
```

### 4.3 Sequence: Confirmation Passage

```
User     Browser    TrainPassCtrl   TrainPassSvc   AlertSvc    ConfirmRepo   EventBus
 |          |            |              |             |             |            |
 |--Confirm->            |              |             |             |            |
 |          |--POST /confirm----------->|             |             |            |
 |          |            |              |             |             |            |
 |          |            |--confirm_pass()----------->|             |            |
 |          |            |              |             |             |            |
 |          |            |              |--get_pending_for_train()-->            |
 |          |            |              |<--alerts----|             |            |
 |          |            |              |             |             |            |
 |          |            |              |[if alerts.empty]          |            |
 |          |            |              |   |                       |            |
 |          |            |              |   |--update status        |            |
 |          |            |              |   |                       |            |
 |          |            |              |   |--save_confirmation()-------------->|
 |          |            |              |   |<--ok------------------|            |
 |          |            |              |   |                       |            |
 |          |            |              |   |--publish(ConfirmedEvent)---------->|
 |          |            |              |   |                       |            |
 |          |            |<--train_pass-|   |                       |            |
 |          |<--200 + JSON|              |             |             |            |
 |<--Success-|            |              |             |             |            |
 |          |            |              |             |             |            |
```

### 4.4 Sequence: Creation Alerte Automatique

```
Camera      DataReceiver    SpringSvc    AlertSvc    NotificationSvc    WebSocket
   |              |             |            |              |               |
   |--spring_data->             |            |              |               |
   |              |             |            |              |               |
   |              |--update_measurement()--->|              |               |
   |              |             |            |              |               |
   |              |             |--evaluate_status()        |               |
   |              |             |            |              |               |
   |              |             |[if status changed to warning/critical]    |
   |              |             |   |        |              |               |
   |              |             |   |--create_alert()------>|               |
   |              |             |   |        |              |               |
   |              |             |   |        |--notify_alert()------------->|
   |              |             |   |        |              |               |
   |              |             |   |        |              |--broadcast()-->
   |              |             |   |        |              |               |
   |              |             |   |<--alert|              |               |
   |              |<--spring----|            |              |               |
   |              |             |            |              |               |
```

### 4.5 Sequence: Consultation Historique Ressort

```
Operateur   Browser    SpringHistoryCtrl   SpringHistorySvc    DB
   |           |              |                   |              |
   |--click history btn------>|                   |              |
   |           |              |                   |              |
   |           |--GET /springs/{id}/history------>|              |
   |           |              |                   |              |
   |           |              |--get_spring_history()----------->|
   |           |              |                   |              |
   |           |              |                   |--query springs by wagon--|
   |           |              |                   |              |
   |           |              |                   |<--passages---|
   |           |              |                   |              |
   |           |              |                   |--format_passages()       |
   |           |              |                   |              |
   |           |              |<--history_data----|              |
   |           |              |                   |              |
   |           |<--200 + JSON--|                  |              |
   |           |              |                   |              |
   |<--display history--------|                   |              |
   |           |              |                   |              |
```

### 4.6 Sequence: Annulation Confirmation

```
Operateur   Browser    CancellationCtrl   CancellationSvc   NotificationSvc    DB
   |           |              |                 |                  |            |
   |--click cancel btn------->|                 |                  |            |
   |           |              |                 |                  |            |
   |--enter reason + confirm->|                 |                  |            |
   |           |              |                 |                  |            |
   |           |--POST /springs/{id}/cancel-confirmation---------->|            |
   |           |              |                 |                  |            |
   |           |              |--validate_reason()                 |            |
   |           |              |                 |                  |            |
   |           |              |--check_time_limit()                |            |
   |           |              |                 |                  |            |
   |           |              |                 |--get_confirmation()--------->|
   |           |              |                 |                  |<--conf-----|
   |           |              |                 |                  |            |
   |           |              |                 |--create_cancellation()------>|
   |           |              |                 |                  |            |
   |           |              |                 |--update_spring_status()----->|
   |           |              |                 |                  |            |
   |           |              |                 |--log_audit()---------------->|
   |           |              |                 |                  |            |
   |           |              |                 |--notify_supervisor()-------->|
   |           |              |                 |                  |            |
   |           |              |                 |                  |--send_email|
   |           |              |                 |                  |            |
   |           |              |<--result--------|                  |            |
   |           |              |                 |                  |            |
   |           |<--200 + JSON--|                |                  |            |
   |           |              |                 |                  |            |
   |<--success + notification-|                 |                  |            |
   |           |              |                 |                  |            |
```

### 4.7 Sequence: Consultation Audit Trail

```
Superviseur   Browser    AuditCtrl    AuditService    DB
    |            |           |              |          |
    |--access audit page---->|              |          |
    |            |           |              |          |
    |            |--GET /audit/operations--->          |
    |            |           |              |          |
    |            |           |--get_operations()------>|
    |            |           |              |          |
    |            |           |              |--query with filters--|
    |            |           |              |          |
    |            |           |              |<--logs---|
    |            |           |              |          |
    |            |           |              |--format_operations() |
    |            |           |              |          |
    |            |           |<--operations-|          |
    |            |           |              |          |
    |            |<--200 + JSON             |          |
    |            |           |              |          |
    |<--display audit table--|              |          |
    |            |           |              |          |
    |            |           |              |          |
    |--click export PDF----->|              |          |
    |            |           |              |          |
    |            |--GET /audit/export?format=pdf------>|
    |            |           |              |          |
    |            |           |--export_pdf()---------->|
    |            |           |              |          |
    |            |           |<--pdf_bytes--|          |
    |            |           |              |          |
    |            |<--200 + file             |          |
    |            |           |              |          |
    |<--download PDF---------|              |          |
    |            |           |              |          |
```

### 4.8 Sequence: Generation Rapport (Asynchrone)

```
Superviseur  Browser   ReportCtrl   ReportService   CeleryWorker   DB    EmailSvc
    |           |          |             |               |          |        |
    |--fill report form--->|             |               |          |        |
    |           |          |             |               |          |        |
    |--click generate----->|             |               |          |        |
    |           |          |             |               |          |        |
    |           |--POST /reports--------->               |          |        |
    |           |          |             |               |          |        |
    |           |          |--create_report()----------->           |        |
    |           |          |             |               |          |        |
    |           |          |             |--save_report()---------->|        |
    |           |          |             |               |          |        |
    |           |          |             |[if period > 30 days]     |        |
    |           |          |             |   |           |          |        |
    |           |          |             |   |--queue_task()------->|        |
    |           |          |             |   |           |          |        |
    |           |          |             |   |<--task_id-|          |        |
    |           |          |             |               |          |        |
    |           |          |<--202 + processing status--|          |        |
    |           |          |             |               |          |        |
    |           |<--202 + "Processing"---|              |          |        |
    |           |          |             |               |          |        |
    |<--notification pending|             |               |          |        |
    |           |          |             |               |          |        |
    |           |          |             |               |          |        |
    |           |          |             | [Celery Worker]          |        |
    |           |          |             |               |          |        |
    |           |          |             |               |--get_report()---->|
    |           |          |             |               |          |        |
    |           |          |             |               |--calculate_stats()|
    |           |          |             |               |          |        |
    |           |          |             |               |--generate_files() |
    |           |          |             |               |          |        |
    |           |          |             |               |--update_status()-->|
    |           |          |             |               |          |        |
    |           |          |             |               |--send_notification-->
    |           |          |             |               |          |        |
    |<--email: "Report ready"----------------------------------------|--------|
    |           |          |             |               |          |        |
```

---

## 5. Conception Base de Donnees

### 5.1 Scripts DDL Complets

```sql
-- ============================================
-- VICORE V2 - Database Schema
-- Version: 1.0
-- ============================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLES
-- ============================================

-- Users table (synchronises depuis SSO Eurotunnel)
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    sso_id          VARCHAR(100) NOT NULL,    -- Identifiant SSO Eurotunnel
    username        VARCHAR(50) NOT NULL,
    email           VARCHAR(100),
    display_name    VARCHAR(100),
    role            VARCHAR(20) NOT NULL DEFAULT 'operator',
    locale          VARCHAR(5) NOT NULL DEFAULT 'fr',  -- Preference de langue
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP,

    CONSTRAINT uq_users_sso_id UNIQUE (sso_id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'supervisor', 'operator', 'viewer')),
    CONSTRAINT chk_users_locale CHECK (locale IN ('fr', 'en'))
);

-- Train passes table
CREATE TABLE train_passes (
    id              SERIAL PRIMARY KEY,
    passage_time    TIMESTAMP NOT NULL,
    direction       VARCHAR(20) NOT NULL,
    train_number    VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_tp_direction CHECK (direction IN ('france_uk', 'uk_france')),
    CONSTRAINT chk_tp_status CHECK (
        status IN ('pending', 'in_progress', 'confirmed', 'alert')
    )
);

-- Cars table
CREATE TABLE cars (
    id              SERIAL PRIMARY KEY,
    train_pass_id   INTEGER NOT NULL,
    position        INTEGER NOT NULL,
    car_type        VARCHAR(20) NOT NULL DEFAULT 'passenger',
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cars_train_pass
        FOREIGN KEY (train_pass_id) REFERENCES train_passes(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_cars_position UNIQUE (train_pass_id, position),
    CONSTRAINT chk_cars_type CHECK (
        car_type IN ('locomotive', 'passenger', 'freight', 'service')
    ),
    CONSTRAINT chk_cars_status CHECK (
        status IN ('pending', 'ok', 'warning', 'alert')
    )
);

-- Springs table
CREATE TABLE springs (
    id              SERIAL PRIMARY KEY,
    car_id          INTEGER NOT NULL,
    position        INTEGER NOT NULL,
    side            VARCHAR(10) NOT NULL,
    height_mm       DECIMAL(6,2),
    status          VARCHAR(20) NOT NULL DEFAULT 'unknown',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_springs_car
        FOREIGN KEY (car_id) REFERENCES cars(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_springs_position UNIQUE (car_id, position, side),
    CONSTRAINT chk_springs_side CHECK (side IN ('left', 'right')),
    CONSTRAINT chk_springs_status CHECK (
        status IN ('ok', 'warning', 'critical', 'unknown')
    )
);

-- Spring alerts table
CREATE TABLE spring_alerts (
    id                  SERIAL PRIMARY KEY,
    spring_id           INTEGER NOT NULL,
    alert_type          VARCHAR(50) NOT NULL,
    severity            VARCHAR(20) NOT NULL,
    message             TEXT,
    is_acknowledged     BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by     INTEGER,
    acknowledged_at     TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alerts_spring
        FOREIGN KEY (spring_id) REFERENCES springs(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_alerts_user
        FOREIGN KEY (acknowledged_by) REFERENCES users(id),
    CONSTRAINT chk_alerts_severity CHECK (
        severity IN ('info', 'warning', 'critical')
    )
);

-- Confirmations table
CREATE TABLE confirmations (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL,
    train_pass_id       INTEGER,
    car_id              INTEGER,
    confirmation_type   VARCHAR(30) NOT NULL,
    confirmed_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes               TEXT,

    CONSTRAINT fk_conf_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_conf_train_pass
        FOREIGN KEY (train_pass_id) REFERENCES train_passes(id),
    CONSTRAINT fk_conf_car
        FOREIGN KEY (car_id) REFERENCES cars(id),
    CONSTRAINT chk_conf_type CHECK (
        confirmation_type IN (
            'train_pass_ok', 'car_ok', 'spring_validated', 'alert_acknowledged'
        )
    )
);

-- Audit logs table
CREATE TABLE audit_logs (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER,
    action          VARCHAR(50) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       INTEGER,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      VARCHAR(255),
    session_id      VARCHAR(64),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_audit_action CHECK (
        action IN ('login', 'logout', 'confirmation', 'cancellation', 'view', 'export', 'report_generated')
    )
);

-- Confirmation cancellations table
CREATE TABLE confirmation_cancellations (
    id                      SERIAL PRIMARY KEY,
    confirmation_id         INTEGER NOT NULL,
    cancelled_by            INTEGER NOT NULL,
    cancelled_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason                  TEXT NOT NULL,
    notified_supervisor     BOOLEAN NOT NULL DEFAULT FALSE,
    notification_sent_at    TIMESTAMP,

    CONSTRAINT fk_cancel_confirmation
        FOREIGN KEY (confirmation_id) REFERENCES confirmations(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cancel_user
        FOREIGN KEY (cancelled_by) REFERENCES users(id),
    CONSTRAINT chk_reason_min_length CHECK (LENGTH(reason) >= 10)
);

-- Reports table
CREATE TABLE reports (
    id              VARCHAR(20) PRIMARY KEY,  -- Format: rpt_xxxxx
    created_by      INTEGER NOT NULL,
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

    CONSTRAINT fk_reports_user
        FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT chk_report_type CHECK (report_type IN ('summary', 'detailed')),
    CONSTRAINT chk_report_status CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT chk_date_range CHECK (end_date >= start_date),
    CONSTRAINT chk_max_period CHECK (end_date - start_date <= 90)
);

-- ============================================
-- INDEXES
-- ============================================

-- Users indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- Train passes indexes
CREATE INDEX idx_tp_passage_time ON train_passes(passage_time DESC);
CREATE INDEX idx_tp_status ON train_passes(status);
CREATE INDEX idx_tp_direction ON train_passes(direction);
CREATE INDEX idx_tp_pending ON train_passes(passage_time DESC)
    WHERE status IN ('pending', 'in_progress');

-- Cars indexes
CREATE INDEX idx_cars_train_pass ON cars(train_pass_id);
CREATE INDEX idx_cars_status ON cars(status);

-- Springs indexes
CREATE INDEX idx_springs_car ON springs(car_id);
CREATE INDEX idx_springs_status ON springs(status);

-- Alerts indexes
CREATE INDEX idx_alerts_spring ON spring_alerts(spring_id);
CREATE INDEX idx_alerts_pending ON spring_alerts(created_at DESC)
    WHERE is_acknowledged = FALSE;
CREATE INDEX idx_alerts_severity ON spring_alerts(severity);

-- Confirmations indexes
CREATE INDEX idx_conf_user ON confirmations(user_id);
CREATE INDEX idx_conf_train_pass ON confirmations(train_pass_id);
CREATE INDEX idx_conf_date ON confirmations(confirmed_at DESC);

-- Audit logs indexes
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_date ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_date_action ON audit_logs(created_at, action);

-- Confirmation cancellations indexes
CREATE INDEX idx_cancel_confirmation ON confirmation_cancellations(confirmation_id);
CREATE INDEX idx_cancel_user ON confirmation_cancellations(cancelled_by);
CREATE INDEX idx_cancel_date ON confirmation_cancellations(cancelled_at DESC);

-- Reports indexes
CREATE INDEX idx_reports_user ON reports(created_by);
CREATE INDEX idx_reports_date ON reports(created_at DESC);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_expires ON reports(expires_at);

-- ============================================
-- TRIGGERS
-- ============================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER trg_train_passes_updated
    BEFORE UPDATE ON train_passes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_cars_updated
    BEFORE UPDATE ON cars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- INITIAL DATA
-- ============================================

-- Note: Les utilisateurs sont crees automatiquement lors de leur
-- premiere connexion SSO. Aucune donnee initiale requise.
-- Le mapping des groupes SSO vers les roles est configure dans l'application.
```

### 5.2 Migrations Alembic

```python
# migrations/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Create Date: 2026-01-18
"""

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sso_id', sa.String(100), nullable=False, unique=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='operator'),
        sa.Column('locale', sa.String(5), nullable=False, server_default='fr'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True)
    )

    # ... other tables


def downgrade():
    op.drop_table('users')
    # ... other drops
```

---

## 6. Conception des APIs

### 6.1 Schemas de Validation

```python
# app/modules/auth/schemas.py

from marshmallow import Schema, fields, validate, validates, ValidationError


class SAMLCallbackSchema(Schema):
    """Schema validation pour callback SSO."""

    SAMLResponse = fields.String(required=True)
    RelayState = fields.String(required=False)


class UserSchema(Schema):
    """Schema serialisation utilisateur."""

    id = fields.Integer(dump_only=True)
    sso_id = fields.String()
    username = fields.String()
    email = fields.String()
    display_name = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    last_login = fields.DateTime()


class SessionInfoSchema(Schema):
    """Schema informations de session."""

    user = fields.Nested(UserSchema)
    expires_at = fields.DateTime()
```

```python
# app/modules/train_passes/schemas.py

class TrainPassFilterSchema(Schema):
    """Schema filtres liste passages."""

    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    status = fields.String(validate=validate.OneOf([
        'pending', 'in_progress', 'confirmed', 'alert'
    ]))
    direction = fields.String(validate=validate.OneOf([
        'france_uk', 'uk_france'
    ]))
    date_from = fields.DateTime()
    date_to = fields.DateTime()

    @validates('date_to')
    def validate_date_range(self, value, **kwargs):
        if self.context.get('date_from') and value < self.context['date_from']:
            raise ValidationError("date_to must be after date_from")


class CarSummarySchema(Schema):
    """Schema resume wagon."""

    id = fields.Integer()
    position = fields.Integer()
    car_type = fields.String()
    status = fields.String()
    springs_status = fields.String()


class TrainPassSchema(Schema):
    """Schema passage de train."""

    id = fields.Integer(dump_only=True)
    passage_time = fields.DateTime()
    direction = fields.String()
    train_number = fields.String()
    status = fields.String()
    cars_count = fields.Integer()
    alerts_count = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class TrainPassDetailSchema(TrainPassSchema):
    """Schema detail passage avec wagons."""

    cars = fields.List(fields.Nested(CarSummarySchema))


class ConfirmationSchema(Schema):
    """Schema confirmation."""

    notes = fields.String(validate=validate.Length(max=500))
```

### 6.2 Controllers

```python
# app/modules/train_passes/routes.py

from flask import Blueprint, request, g
from app.common.decorators import require_auth, require_role
from app.common.responses import success_response, paginated_response

bp = Blueprint('train_passes', __name__)


@bp.route('/', methods=['GET'])
@require_auth
def list_train_passes():
    """Liste les passages de trains avec filtrage."""
    # Validation
    schema = TrainPassFilterSchema()
    filters = schema.load(request.args)

    # Service call
    service = get_train_pass_service()
    result = service.get_passes(
        filters=filters,
        page=filters['page'],
        per_page=filters['per_page']
    )

    # Serialisation
    output_schema = TrainPassSchema(many=True)
    return paginated_response(
        data=output_schema.dump(result.items),
        pagination=result.pagination
    )


@bp.route('/<int:id>', methods=['GET'])
@require_auth
def get_train_pass(id: int):
    """Recupere les details d'un passage."""
    service = get_train_pass_service()
    train_pass = service.get_pass_details(id)

    schema = TrainPassDetailSchema()
    return success_response(data=schema.dump(train_pass))


@bp.route('/<int:id>/confirm', methods=['POST'])
@require_auth
@require_role('operator', 'admin')
def confirm_train_pass(id: int):
    """Confirme un passage de train."""
    schema = ConfirmationSchema()
    data = schema.load(request.get_json() or {})

    service = get_train_pass_service()
    train_pass = service.confirm_pass(
        pass_id=id,
        user=g.current_user,
        notes=data.get('notes')
    )

    output_schema = TrainPassSchema()
    return success_response(
        data=output_schema.dump(train_pass),
        message="Train pass confirmed successfully"
    )
```

### 6.3 Format Reponses

```python
# app/common/responses.py

from flask import jsonify
from datetime import datetime
import uuid


def success_response(data=None, message=None, status_code=200):
    """Genere une reponse de succes."""
    response = {
        'success': True,
        'data': data,
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': str(uuid.uuid4())
        }
    }
    if message:
        response['message'] = message

    return jsonify(response), status_code


def paginated_response(data, pagination, status_code=200):
    """Genere une reponse paginee."""
    response = {
        'success': True,
        'data': data,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        },
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': str(uuid.uuid4())
        }
    }
    return jsonify(response), status_code


def error_response(code, message, details=None, status_code=400):
    """Genere une reponse d'erreur."""
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        },
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': str(uuid.uuid4())
        }
    }
    if details:
        response['error']['details'] = details

    return jsonify(response), status_code
```

---

## 7. Conception Frontend

### 7.1 Structure Composants

```
static/
├── css/
│   ├── design-system.css       # Variables CSS, reset, base
│   ├── dark-tech-theme.css     # Theme principal
│   └── components/
│       ├── _buttons.css
│       ├── _cards.css
│       ├── _forms.css
│       ├── _modals.css
│       └── _tables.css
│
├── js/
│   ├── app.js                  # Application principale
│   ├── api.js                  # Client API
│   ├── store.js                # State management
│   └── components/
│       ├── AlertBadge.js
│       ├── ConfirmModal.js
│       ├── SpringDiagram.js
│       ├── StatusIndicator.js
│       └── TrainPassCard.js
│
└── images/
    ├── logo.svg
    └── icons/
```

### 7.2 Composants Vue.js

```javascript
// static/js/components/TrainPassCard.js

Vue.component('train-pass-card', {
    props: {
        trainPass: {
            type: Object,
            required: true
        }
    },

    template: `
        <div class="card card--train-pass"
             :class="statusClass"
             @click="$emit('select', trainPass)">
            <div class="card__header">
                <span class="card__time">{{ formattedTime }}</span>
                <span class="card__direction">{{ directionLabel }}</span>
            </div>
            <div class="card__body">
                <div class="card__train-number">{{ trainPass.train_number }}</div>
                <div class="card__stats">
                    <span class="stat">
                        <i class="icon-car"></i> {{ trainPass.cars_count }}
                    </span>
                    <span class="stat stat--alerts" v-if="trainPass.alerts_count > 0">
                        <i class="icon-alert"></i> {{ trainPass.alerts_count }}
                    </span>
                </div>
            </div>
            <div class="card__footer">
                <status-badge :status="trainPass.status" />
            </div>
        </div>
    `,

    computed: {
        statusClass() {
            return `card--${this.trainPass.status}`;
        },

        formattedTime() {
            return new Date(this.trainPass.passage_time)
                .toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        },

        directionLabel() {
            return this.trainPass.direction === 'france_uk'
                ? 'FR → UK'
                : 'UK → FR';
        }
    }
});
```

```javascript
// static/js/components/SpringDiagram.js

Vue.component('spring-diagram', {
    props: {
        springs: {
            type: Array,
            required: true
        },
        carType: {
            type: String,
            default: 'passenger'
        }
    },

    template: `
        <div class="spring-diagram">
            <div class="spring-diagram__wagon">
                <div class="wagon-body" :class="carTypeClass">
                    <span class="wagon-label">{{ carTypeLabel }}</span>
                </div>
                <div class="spring-diagram__springs">
                    <div class="springs-row springs-row--left">
                        <spring-indicator
                            v-for="spring in leftSprings"
                            :key="spring.id"
                            :spring="spring"
                            @click="$emit('spring-click', spring)"
                        />
                    </div>
                    <div class="springs-row springs-row--right">
                        <spring-indicator
                            v-for="spring in rightSprings"
                            :key="spring.id"
                            :spring="spring"
                            @click="$emit('spring-click', spring)"
                        />
                    </div>
                </div>
            </div>
            <div class="spring-diagram__legend">
                <span class="legend-item legend-item--ok">OK</span>
                <span class="legend-item legend-item--warning">Warning</span>
                <span class="legend-item legend-item--critical">Critical</span>
            </div>
        </div>
    `,

    computed: {
        leftSprings() {
            return this.springs.filter(s => s.side === 'left')
                .sort((a, b) => a.position - b.position);
        },

        rightSprings() {
            return this.springs.filter(s => s.side === 'right')
                .sort((a, b) => a.position - b.position);
        },

        carTypeClass() {
            return `wagon-body--${this.carType}`;
        },

        carTypeLabel() {
            const labels = {
                locomotive: 'LOCO',
                passenger: 'PAX',
                freight: 'FRT',
                service: 'SVC'
            };
            return labels[this.carType] || this.carType;
        }
    }
});


Vue.component('spring-indicator', {
    props: {
        spring: {
            type: Object,
            required: true
        }
    },

    template: `
        <div class="spring-indicator"
             :class="statusClass"
             :title="tooltip"
             @click="$emit('click', spring)">
            <div class="spring-indicator__coil"></div>
            <div class="spring-indicator__value">{{ height }}</div>
        </div>
    `,

    computed: {
        statusClass() {
            return `spring-indicator--${this.spring.status}`;
        },

        height() {
            return this.spring.height_mm
                ? `${this.spring.height_mm}mm`
                : '---';
        },

        tooltip() {
            return `Position ${this.spring.position} ${this.spring.side}\n`
                + `Height: ${this.height}\n`
                + `Status: ${this.spring.status}`;
        }
    }
});
```

### 7.3 Client API

```javascript
// static/js/api.js

class ApiClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    async request(method, path, data = null, options = {}) {
        const url = this.baseUrl + path;

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            method,
            headers,
            ...options
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            const json = await response.json();

            if (!response.ok) {
                throw new ApiError(json.error.code, json.error.message);
            }

            return json;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError('NETWORK_ERROR', error.message);
        }
    }

    // Auth endpoints (SSO Eurotunnel)
    initiateLogin(returnUrl = null) {
        // Redirection vers le portail SSO Eurotunnel
        const params = returnUrl ? `?return_url=${encodeURIComponent(returnUrl)}` : '';
        window.location.href = `${this.baseUrl}/auth/sso/login${params}`;
    }

    async logout() {
        // Initie le Single Logout SSO
        window.location.href = `${this.baseUrl}/auth/sso/logout`;
    }

    async getCurrentUser() {
        return this.request('GET', '/auth/me');
    }

    // Train passes endpoints
    async getTrainPasses(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request('GET', `/train-passes?${query}`);
    }

    async getTrainPass(id) {
        return this.request('GET', `/train-passes/${id}`);
    }

    async confirmTrainPass(id, notes = null) {
        return this.request('POST', `/train-passes/${id}/confirm`, { notes });
    }

    // Cars endpoints
    async getCar(id) {
        return this.request('GET', `/cars/${id}`);
    }

    async confirmCar(id, notes = null) {
        return this.request('POST', `/cars/${id}/confirm`, { notes });
    }

    // Alerts endpoints
    async getAlerts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request('GET', `/alerts?${query}`);
    }

    async acknowledgeAlert(id, notes = null) {
        return this.request('POST', `/alerts/${id}/acknowledge`, { notes });
    }

    // System endpoints
    async getSystemHealth() {
        return this.request('GET', '/system/health');
    }

    async getHeartbeatStatus() {
        return this.request('GET', '/system/heartbeat');
    }
}


class ApiError extends Error {
    constructor(code, message) {
        super(message);
        this.code = code;
        this.name = 'ApiError';
    }
}


// Export singleton instance
const api = new ApiClient();
```

---

## 8. Gestion des Erreurs

### 8.1 Exceptions Personnalisees

```python
# app/common/exceptions.py

class VicoreException(Exception):
    """Exception de base VICORE."""

    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()


class AuthenticationError(VicoreException):
    """Erreur d'authentification."""
    pass


class AuthorizationError(VicoreException):
    """Erreur d'autorisation."""
    pass


class NotFoundError(VicoreException):
    """Ressource non trouvee."""
    pass


class ValidationError(VicoreException):
    """Erreur de validation."""

    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.errors = errors or {}


class BusinessError(VicoreException):
    """Erreur metier."""
    pass


class ExternalServiceError(VicoreException):
    """Erreur service externe."""
    pass
```

### 8.2 Handlers d'Erreurs

```python
# app/common/error_handlers.py

from flask import jsonify
from app.common.exceptions import *
from app.common.responses import error_response


def register_error_handlers(app):
    """Enregistre les handlers d'erreurs."""

    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        return error_response(
            code=error.code,
            message=error.message,
            status_code=401
        )

    @app.errorhandler(AuthorizationError)
    def handle_authz_error(error):
        return error_response(
            code=error.code,
            message=error.message,
            status_code=403
        )

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return error_response(
            code=error.code,
            message=error.message,
            status_code=404
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return error_response(
            code=error.code,
            message=error.message,
            details=error.errors,
            status_code=400
        )

    @app.errorhandler(BusinessError)
    def handle_business_error(error):
        return error_response(
            code=error.code,
            message=error.message,
            status_code=400
        )

    @app.errorhandler(ExternalServiceError)
    def handle_external_error(error):
        return error_response(
            code=error.code,
            message=error.message,
            status_code=503
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        # Log the error
        app.logger.exception("Internal server error")

        return error_response(
            code='INTERNAL_ERROR',
            message='An internal error occurred',
            status_code=500
        )

    @app.errorhandler(404)
    def handle_404(error):
        return error_response(
            code='NOT_FOUND',
            message='The requested resource was not found',
            status_code=404
        )
```

### 8.3 Logging

```python
# app/common/logging.py

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app):
    """Configure le logging applicatif."""

    # Format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File handler
    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_handler = RotatingFileHandler(
        'logs/vicore.log',
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/vicore-errors.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)

    # Set level based on environment
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
```

---

## 9. Tests et Validation

### 9.1 Structure des Tests

```
tests/
├── conftest.py              # Fixtures pytest
├── unit/
│   ├── test_auth_service.py
│   ├── test_train_pass_service.py
│   ├── test_spring_service.py
│   └── test_alert_service.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_train_passes_api.py
│   ├── test_cars_api.py
│   └── test_database.py
└── e2e/
    ├── test_sso_flow.py
    ├── test_inspection_flow.py
    └── test_confirmation_flow.py
```

### 9.2 Fixtures

```python
# tests/conftest.py

import pytest
from app import create_app
from app.extensions import db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        session = db.create_scoped_session(
            options={'bind': connection, 'binds': {}}
        )
        db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def test_user(db_session):
    """Create test user (simulating SSO user)."""
    from app.modules.auth.models import User

    user = User(
        sso_id='testuser@eurotunnel.com',
        username='testuser',
        email='testuser@eurotunnel.com',
        display_name='Test User',
        role='operator',
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    return user


@pytest.fixture
def auth_headers(test_user, app):
    """Create authenticated headers."""
    from app.modules.auth.services import TokenService

    with app.app_context():
        token = TokenService.create_access_token(test_user)
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_train_pass(db_session):
    """Create sample train pass with cars."""
    from app.modules.train_passes.models import TrainPass
    from app.modules.cars.models import Car
    from app.modules.springs.models import Spring
    from datetime import datetime

    train_pass = TrainPass(
        passage_time=datetime.utcnow(),
        direction='france_uk',
        train_number='ET-TEST-001',
        status='pending'
    )

    for i in range(3):
        car = Car(
            position=i + 1,
            car_type='passenger' if i > 0 else 'locomotive',
            status='pending'
        )

        for pos in range(1, 5):
            for side in ['left', 'right']:
                spring = Spring(
                    position=pos,
                    side=side,
                    height_mm=150.0,
                    status='ok'
                )
                car.springs.append(spring)

        train_pass.cars.append(car)

    db_session.add(train_pass)
    db_session.commit()

    return train_pass
```

### 9.3 Tests Unitaires

```python
# tests/unit/test_spring_service.py

import pytest
from decimal import Decimal
from app.modules.springs.services import SpringService


class TestSpringService:
    """Tests pour SpringService."""

    def test_evaluate_status_ok(self):
        """Status OK pour hauteur nominale."""
        service = SpringService(None, None)

        assert service._evaluate_status(Decimal('150')) == 'ok'
        assert service._evaluate_status(Decimal('145')) == 'ok'
        assert service._evaluate_status(Decimal('155')) == 'ok'

    def test_evaluate_status_warning_low(self):
        """Status warning pour hauteur basse."""
        service = SpringService(None, None)

        assert service._evaluate_status(Decimal('130')) == 'warning'
        assert service._evaluate_status(Decimal('135')) == 'ok'  # limite
        assert service._evaluate_status(Decimal('134')) == 'warning'

    def test_evaluate_status_warning_high(self):
        """Status warning pour hauteur haute."""
        service = SpringService(None, None)

        assert service._evaluate_status(Decimal('170')) == 'warning'
        assert service._evaluate_status(Decimal('165')) == 'ok'  # limite
        assert service._evaluate_status(Decimal('166')) == 'warning'

    def test_evaluate_status_critical_low(self):
        """Status critical pour hauteur tres basse."""
        service = SpringService(None, None)

        assert service._evaluate_status(Decimal('110')) == 'critical'
        assert service._evaluate_status(Decimal('120')) == 'warning'  # limite
        assert service._evaluate_status(Decimal('119')) == 'critical'

    def test_evaluate_status_critical_high(self):
        """Status critical pour hauteur tres haute."""
        service = SpringService(None, None)

        assert service._evaluate_status(Decimal('190')) == 'critical'
        assert service._evaluate_status(Decimal('180')) == 'warning'  # limite
        assert service._evaluate_status(Decimal('181')) == 'critical'
```

### 9.4 Tests Integration

```python
# tests/integration/test_train_passes_api.py

import pytest


class TestTrainPassesAPI:
    """Tests integration API train passes."""

    def test_list_train_passes_unauthorized(self, client):
        """Liste refuse si non authentifie."""
        response = client.get('/api/v1/train-passes')
        assert response.status_code == 401

    def test_list_train_passes(self, client, auth_headers, sample_train_pass):
        """Liste les passages avec authentification."""
        response = client.get(
            '/api/v1/train-passes',
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1
        assert 'pagination' in data

    def test_get_train_pass_details(self, client, auth_headers, sample_train_pass):
        """Recupere les details d'un passage."""
        response = client.get(
            f'/api/v1/train-passes/{sample_train_pass.id}',
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == sample_train_pass.id
        assert len(data['data']['cars']) == 3

    def test_get_train_pass_not_found(self, client, auth_headers):
        """Erreur 404 pour passage inexistant."""
        response = client.get(
            '/api/v1/train-passes/99999',
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_confirm_train_pass(self, client, auth_headers, sample_train_pass):
        """Confirme un passage de train."""
        response = client.post(
            f'/api/v1/train-passes/{sample_train_pass.id}/confirm',
            headers=auth_headers,
            json={'notes': 'Test confirmation'}
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['data']['status'] == 'confirmed'

    def test_confirm_already_confirmed(self, client, auth_headers, sample_train_pass):
        """Erreur si deja confirme."""
        # First confirmation
        client.post(
            f'/api/v1/train-passes/{sample_train_pass.id}/confirm',
            headers=auth_headers
        )

        # Second confirmation should fail
        response = client.post(
            f'/api/v1/train-passes/{sample_train_pass.id}/confirm',
            headers=auth_headers
        )
        assert response.status_code == 400
        assert 'already confirmed' in response.get_json()['error']['message']
```

---

## Annexes

### A. Checklist de Developpement

| Phase | Element | Verifie |
|-------|---------|---------|
| **Avant dev** | Specifications lues | [ ] |
| **Avant dev** | Tests ecrits | [ ] |
| **Pendant dev** | Code documente | [ ] |
| **Pendant dev** | Gestion erreurs | [ ] |
| **Apres dev** | Tests passent | [ ] |
| **Apres dev** | Code review OK | [ ] |
| **Apres dev** | Documentation a jour | [ ] |

### B. Conventions de Nommage

| Element | Convention | Exemple |
|---------|------------|---------|
| Classe | CamelCase | `TrainPassService` |
| Fonction | snake_case | `get_train_pass()` |
| Variable | snake_case | `train_pass_id` |
| Constante | SCREAMING_SNAKE | `MAX_RETRIES` |
| Fichier | snake_case | `train_pass_service.py` |
| Module | snake_case | `train_passes` |
| URL | kebab-case | `/train-passes` |
| CSS | kebab-case | `.train-pass-card` |

### C. Codes d'Erreur

| Code | HTTP | Signification |
|------|------|---------------|
| AUTH_INVALID_CREDENTIALS | 401 | Identifiants invalides |
| AUTH_TOKEN_EXPIRED | 401 | Token expire |
| AUTH_TOKEN_INVALID | 401 | Token invalide |
| AUTH_INSUFFICIENT_PERMISSIONS | 403 | Permissions insuffisantes |
| VALIDATION_ERROR | 400 | Erreur de validation |
| NOT_FOUND | 404 | Ressource non trouvee |
| BUSINESS_ERROR | 400 | Erreur metier |
| INTERNAL_ERROR | 500 | Erreur interne |
| SERVICE_UNAVAILABLE | 503 | Service indisponible |

---

*Document genere le 2026-01-18*
*Version: 1.0*
*Statut: En attente de validation*
