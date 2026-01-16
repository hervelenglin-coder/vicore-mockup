# VICORE - Diagrammes d'Architecture Mermaid

## 1. Architecture Globale du Système

```mermaid
flowchart TB
    subgraph Client["Client (Browser)"]
        VUE["Vue.js 2.6 App"]
        AXIOS["Axios HTTP Client"]
        ELEMENT["Element-UI Components"]
        BOOTSTRAP["Bootstrap 5 CSS"]
    end

    subgraph Server["Backend Server"]
        subgraph Flask["Flask Application"]
            APP["app.py<br/>Routes & Config"]
            AUTH["user_management.py<br/>Authentication"]
            TP_EP["train_pass_endpoints.py<br/>Train Pass API"]
            MS_EP["missing_spring_endpoints.py<br/>Spring Confirmation API"]
            SYS_EP["system_endpoints.py<br/>Monitoring API"]
        end

        subgraph Services["Business Services"]
            DB_IF["db_iface.py<br/>Database Interface"]
            CONF["confidence_levels.py<br/>Confidence Calculator"]
            DISP["display_name_iface.py<br/>Display Name Generator"]
            REDIS_IF["redis_web.py<br/>Cache Interface"]
        end
    end

    subgraph Data["Data Layer"]
        PG[("PostgreSQL<br/>Database")]
        REDIS[("Redis<br/>Cache")]
        IMG["File System<br/>Wheel Images"]
    end

    subgraph External["External Package"]
        DM["eurotunnel_datamodel<br/>Shared Models & Helpers"]
    end

    VUE --> AXIOS
    AXIOS -->|HTTP/REST| APP

    APP --> AUTH
    APP --> TP_EP
    APP --> MS_EP
    APP --> SYS_EP

    TP_EP --> DB_IF
    TP_EP --> CONF
    TP_EP --> DISP
    MS_EP --> DB_IF
    SYS_EP --> REDIS_IF

    DB_IF --> PG
    DB_IF --> DM
    DISP --> REDIS_IF
    REDIS_IF --> REDIS
    CONF --> DM

    APP -->|Static Files| IMG

    AUTH --> DM
    DM --> PG
```

## 2. Architecture des Composants Backend

```mermaid
flowchart LR
    subgraph Endpoints["API Endpoints"]
        direction TB
        E1["/login<br/>/logout"]
        E2["/listpasses<br/>/get_train_passes"]
        E3["/getTrainPass<br/>/loadTrainPasses"]
        E4["/getCar"]
        E5["/get_all_images_for_spring<br/>/put_confirmation_status"]
        E6["/heartbeat<br/>/hb_time<br/>/get_worst_system_status"]
        E7["/wheelimg"]
    end

    subgraph Handlers["Request Handlers"]
        H1["user_management"]
        H2["train_pass_endpoints"]
        H3["train_pass_endpoints"]
        H4["app.py"]
        H5["missing_spring_endpoints"]
        H6["system_endpoints"]
        H7["app.py"]
    end

    subgraph Core["Core Services"]
        C1["db_iface"]
        C2["confidence_levels"]
        C3["display_name_iface"]
        C4["redis_web"]
    end

    E1 --> H1
    E2 --> H2
    E3 --> H3
    E4 --> H4
    E5 --> H5
    E6 --> H6
    E7 --> H7

    H1 --> C1
    H2 --> C1
    H2 --> C2
    H2 --> C3
    H3 --> C1
    H3 --> C2
    H3 --> C3
    H4 --> C1
    H5 --> C1
    H6 --> C4

    C3 --> C4
```

## 3. Modèle de Données (Entity Relationship)

```mermaid
erDiagram
    TRAIN_PASS ||--o{ TRAIN_PASS_CARS : contains
    TRAIN_PASS }o--|| INSTALLATION : belongs_to
    TRAIN_PASS_CARS }o--|| CAR_TYPES : has_type
    CAR_TYPES }o--|| BOGIE_TYPE : uses
    TRAIN_PASS ||--o{ SPRING_LOCATION : has
    SPRING_LOCATION ||--o| HUMAN_CONFIRMATIONS : may_have
    SPRING_LOCATION ||--o{ SPRING_IMAGE_LOCATION : has_images
    USERS ||--o{ HUMAN_CONFIRMATIONS : confirms

    TRAIN_PASS {
        int train_pass_id PK
        timestamp time_start
        timestamp time_end
        int installation_id FK
        string train_service_code
        int n_checked
        float min_confidence
    }

    INSTALLATION {
        int installation_id PK
        string location
        string description
    }

    TRAIN_PASS_CARS {
        int id PK
        int train_pass_id FK
        int car_type_id FK
        int train_pass_order
        int car_num
        string rfid_tag_code
        int rake_id
    }

    CAR_TYPES {
        int car_type_id PK
        string icon_head
        string icon_tail
        int bogie_type FK
        int num_bogies
        int axles_per_bogie
    }

    BOGIE_TYPE {
        int bogie_type_id PK
        string svgname
        string description
    }

    SPRING_LOCATION {
        int spring_location_id PK
        int train_pass_id FK
        int train_axle_number
        string cam_pos
        float confidence
        string best_image_path
    }

    HUMAN_CONFIRMATIONS {
        int id PK
        int spring_location_id FK
        boolean present_not_absent
        string confirmed_by
        timestamp confirmed_at
    }

    SPRING_IMAGE_LOCATION {
        int id PK
        int spring_location_id FK
        string image_path
    }

    USERS {
        int user_id PK
        string user_name
        string display_name
        string password_hash
        string password_salt
    }

    CONFIDENCE_LEVELS {
        int confidence_level PK
        numrange conf_range
        string level_name_en
    }
```

## 4. Flux d'Authentification

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant F as Flask
    participant U as user_management
    participant DB as PostgreSQL

    B->>F: GET /login
    F-->>B: login.html (Vue.js form)

    B->>F: POST /login {username, password}
    F->>U: authenticate_user(username, password)
    U->>DB: SELECT user WHERE username
    DB-->>U: User record (hash, salt)

    alt Valid Credentials
        U->>U: bcrypt.hashpw(password, salt)
        U->>U: Compare hashes
        U-->>F: User object
        F->>F: session[USER_DETAILS] = user.json()
        F-->>B: "1" (success)
        B->>B: Redirect to /listpasses
    else Invalid Credentials
        U-->>F: None
        F-->>B: "01" (invalid)
        B->>B: Show error message
    end
```

## 5. Flux de Visualisation des Passages

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser (Vue.js)
    participant F as Flask
    participant TP as train_pass_endpoints
    participant DB as db_iface
    participant PG as PostgreSQL
    participant R as Redis

    B->>F: GET /listpasses
    F->>F: Check session
    F->>TP: get_train_passes()
    TP->>DB: get_n_train_passes(50)
    DB->>PG: SELECT * FROM get_train_passes()
    PG-->>DB: Train pass rows

    loop For each train pass
        DB->>R: get_trainpass_displayname(tpid)
        alt Cache Hit
            R-->>DB: Displaynames
        else Cache Miss
            DB->>PG: SELECT * FROM get_first_tag(tpid)
            PG-->>DB: RFID tag
            DB->>DB: create_display_name_worker()
            DB->>R: set_trainpass_displayname()
        end
    end

    DB-->>TP: List of train passes
    TP->>TP: add_train_conf_codes()
    TP->>TP: assign_train_pass_to_system()
    TP-->>F: Grouped by installation
    F-->>B: systemview.html + JSON data

    B->>B: Vue.js renders train list
```

## 6. Flux de Confirmation de Ressort

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser (Vue.js)
    participant F as Flask
    participant MS as missing_spring_endpoints
    participant DB as PostgreSQL

    Note over B: User clicks "Confirm spring missing"

    B->>F: GET /get_all_images_for_spring/{spring_id}
    F->>MS: get_all_images_for_spring()
    MS->>DB: SELECT image_path FROM spring_image_location
    DB-->>MS: Image paths
    MS-->>F: JSON array of paths
    F-->>B: ["path1.jpg", "path2.jpg", ...]

    B->>B: Display modal with all images

    Note over B: User clicks "Spring Present" or "Spring Missing"

    B->>F: PUT /put_confirmation_status/{spring_id}/{true|false}
    F->>MS: put_confirmation_status()
    MS->>MS: Validate session
    MS->>DB: SELECT EXISTS(confirmation for spring_id)

    alt Already Confirmed
        DB-->>MS: true
        MS-->>F: 409 Conflict
        F-->>B: Error: Already confirmed
    else Not Yet Confirmed
        DB-->>MS: false
        MS->>DB: SELECT mark_human_confirmed(spring_id, status, user)
        DB-->>MS: n_remaining (unconfirmed springs)
        MS-->>F: {n_remaining: X}
        F-->>B: Success response
        B->>B: Update UI (change color, show message)
    end
```

## 7. Architecture Frontend (Vue.js)

```mermaid
flowchart TB
    subgraph Templates["Jinja2 Templates"]
        BASE["base.html<br/>CDN imports"]
        AUTH_BASE["authorised_users_base.html<br/>Header, Status bar"]
        LOGIN["login.html"]
        SYSTEM["systemview.html"]
        CAR["carview.html"]

        BASE --> AUTH_BASE
        BASE --> LOGIN
        AUTH_BASE --> SYSTEM
        AUTH_BASE --> CAR
    end

    subgraph VueApps["Vue.js Applications"]
        LOGIN_APP["Login App<br/>- Form validation<br/>- Axios POST"]
        SYSTEM_APP["SystemView App<br/>- Train pass list<br/>- Car icons<br/>- Lazy loading"]
        CAR_APP["CarView App<br/>- Spring navigation<br/>- Image display<br/>- Confirmation modal"]
    end

    subgraph Components["Shared Components"]
        ERROR["vue_error_alert.html<br/>Error display"]
        Y25["y25_include.html<br/>Y25 Bogie SVG"]
        OTHER["allotherbogies.html<br/>Other Bogie SVGs"]
    end

    subgraph Scripts["JavaScript Modules"]
        HELPER["ethelper.js<br/>HTTP utilities"]
        CONF_LOOK["confCodeLookup.js<br/>Confidence colors"]
        STATUS["systemStatus.js<br/>Health monitoring"]
        CLOCK["clock.js<br/>Time display"]
    end

    LOGIN --> LOGIN_APP
    SYSTEM --> SYSTEM_APP
    CAR --> CAR_APP

    SYSTEM_APP --> ERROR
    CAR_APP --> ERROR
    CAR_APP --> Y25
    CAR_APP --> OTHER

    SYSTEM_APP --> HELPER
    SYSTEM_APP --> CONF_LOOK
    CAR_APP --> HELPER
    CAR_APP --> CONF_LOOK
    AUTH_BASE --> STATUS
    AUTH_BASE --> CLOCK
```

## 8. Déploiement Docker

```mermaid
flowchart TB
    subgraph Docker["Docker Environment"]
        subgraph WebContainer["Web Container"]
            GUNICORN["Gunicorn WSGI<br/>Port 5000"]
            FLASK_APP["Flask App"]
            GUNICORN --> FLASK_APP
        end

        subgraph Volumes["Volumes"]
            WHEEL_VOL["/mnt/wheelimg<br/>Wheel Images"]
            CONFIG_VOL["/app/config<br/>Configuration"]
        end
    end

    subgraph External["External Services"]
        PG_SVC[("PostgreSQL<br/>Port 5432")]
        REDIS_SVC[("Redis<br/>Port 6379")]
        REVERSE["Nginx/Traefik<br/>Reverse Proxy"]
    end

    subgraph Host["Host Machine"]
        IMG_DIR["Image Directory<br/>/path/to/images"]
        HOST_PORT["Port 1234"]
    end

    REVERSE -->|":443 HTTPS"| HOST_PORT
    HOST_PORT -->|":1234 -> :5000"| GUNICORN
    FLASK_APP --> PG_SVC
    FLASK_APP --> REDIS_SVC
    FLASK_APP --> WHEEL_VOL
    IMG_DIR -.->|"mount"| WHEEL_VOL
```

## 9. Niveaux de Confiance - Machine d'État

```mermaid
stateDiagram-v2
    [*] --> Unchecked: Train passes inspection

    Unchecked --> GREEN: confidence >= threshold_green
    Unchecked --> AMBER: threshold_amber <= confidence < threshold_green
    Unchecked --> RED: confidence < threshold_amber

    GREEN --> Confirmed_Present: Human confirms
    AMBER --> Confirmed_Present: Human confirms present
    AMBER --> Confirmed_Missing: Human confirms missing
    RED --> Confirmed_Present: Human confirms present
    RED --> Confirmed_Missing: Human confirms missing

    state GREEN {
        [*] --> conf_code_1
        note right of conf_code_1: Color: Green
    }

    state AMBER {
        [*] --> conf_code_2
        note right of conf_code_2: Color: Orange
    }

    state RED {
        [*] --> conf_code_3
        note right of conf_code_3: Color: Red
    }

    state Confirmed_Present {
        [*] --> conf_code_0
        note right of conf_code_0: Color: Blue
    }

    state Confirmed_Missing {
        [*] --> stays_red
        note right of stays_red: Requires attention
    }
```

## 10. Flux de Données Complet

```mermaid
flowchart LR
    subgraph Inspection["Inspection System"]
        CAMERA["Cameras"]
        ML["ML Detection"]
        CAMERA --> ML
    end

    subgraph Storage["Data Storage"]
        PG[("PostgreSQL")]
        REDIS[("Redis")]
        FS["File System<br/>Images"]
    end

    subgraph WebApp["VICORE Web App"]
        direction TB
        API["REST API"]
        CACHE["Cache Layer"]
        RENDER["Template Renderer"]
    end

    subgraph Users["Users"]
        OP["Operators"]
        BROWSER["Web Browser"]
    end

    ML -->|"Train pass data<br/>Confidence scores"| PG
    ML -->|"Wheel images"| FS
    ML -->|"Heartbeat"| REDIS

    PG --> API
    FS --> API
    REDIS --> CACHE
    CACHE --> API

    API --> RENDER
    RENDER --> BROWSER
    BROWSER --> OP

    OP -->|"Confirmations"| BROWSER
    BROWSER -->|"PUT /put_confirmation"| API
    API -->|"mark_human_confirmed()"| PG
```

## 11. Structure des Sessions

```mermaid
flowchart TB
    subgraph Session["Flask Session"]
        SECRET["Secret Key<br/>(hardcoded - SECURITY RISK)"]
        USER_DATA["USER_DETAILS_SESSION_VAR"]

        subgraph UserJSON["User JSON Data"]
            UID["user_id: int"]
            UNAME["name: string"]
        end
    end

    subgraph Validation["Session Validation"]
        CHECK{"session.get<br/>(USER_DETAILS)"}
        PARSE["User.model_validate_json()"]
        REDIRECT["Redirect to /login"]
        PROCEED["Process request"]
    end

    SECRET --> Session
    USER_DATA --> UserJSON

    CHECK -->|"None"| REDIRECT
    CHECK -->|"JSON string"| PARSE
    PARSE --> PROCEED
```

## 12. API Routes Map

```mermaid
flowchart TB
    subgraph Public["Public Routes"]
        R1["GET /login"]
        R2["POST /login"]
    end

    subgraph Protected["Protected Routes (Auth Required)"]
        subgraph Navigation["Navigation"]
            R3["GET /"]
            R4["GET /listpasses"]
            R5["GET /cars/:tpid/:car"]
        end

        subgraph API_READ["API - Read"]
            R6["GET /get_train_passes"]
            R7["POST /getTrainPass/:tpid"]
            R8["POST /getCar/:tpid/:car"]
            R9["POST /loadTrainPasses/:last/:n/:install?"]
        end

        subgraph API_SPRING["API - Springs"]
            R10["GET /get_all_images_for_spring/:id"]
            R11["PUT /put_confirmation_status/:id/:status"]
        end

        subgraph API_SYSTEM["API - System"]
            R12["GET /heartbeat/:system"]
            R13["GET /hb_time/:system"]
            R14["GET /get_worst_system_status"]
        end

        subgraph Static["Static Files"]
            R15["GET /wheelimg/:path"]
        end
    end

    subgraph Logout["Logout"]
        R16["GET /logout"]
    end

    R1 --> R2
    R2 -->|"Success"| R3
    R3 --> R4
    R4 --> R5
    R5 --> R16
```

---

## Notes d'Utilisation

Ces diagrammes peuvent être visualisés avec:
- **GitHub**: Rendu natif dans les fichiers Markdown
- **GitLab**: Rendu natif dans les fichiers Markdown
- **VS Code**: Extension "Markdown Preview Mermaid Support"
- **Mermaid Live Editor**: https://mermaid.live

Pour intégrer dans une documentation:
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true});</script>
```

---

*Diagrammes générés le 2026-01-16*
*Version: 1.0.0.12*
