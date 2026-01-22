# VICORE V2 - Specification des Exigences (SRS)

## Document Control

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 2026-01-18 | - | Creation initiale |

| Statut | En cours de redaction |
|--------|----------------------|
| Validation MOA | [ ] A valider |
| Validation MOE | [ ] A valider |

---

## Table des Matieres

1. [Introduction](#1-introduction)
2. [Description Generale](#2-description-generale)
3. [Acteurs et Roles](#3-acteurs-et-roles)
4. [Exigences Fonctionnelles](#4-exigences-fonctionnelles)
5. [Exigences Non-Fonctionnelles](#5-exigences-non-fonctionnelles)
6. [Contraintes](#6-contraintes)
7. [Annexes](#7-annexes)

---

## 1. Introduction

### 1.1 Objectif du Document

Ce document definit l'ensemble des exigences pour le systeme VICORE V2 (VIsualisation COntrole REssorts). Il constitue la base contractuelle entre la maitrise d'ouvrage (Eurotunnel) et la maitrise d'oeuvre pour le developpement de la nouvelle version du systeme.

### 1.2 Portee du Projet

VICORE V2 est une application web de supervision et d'analyse des ressorts de suspension des trains traversant le tunnel sous la Manche. Le systeme permet:
- La visualisation en temps reel de l'etat des ressorts
- L'analyse automatique des images capturees
- La gestion des alertes et confirmations manuelles
- Le suivi historique des passages de trains

### 1.3 Definitions et Acronymes

| Terme | Definition |
|-------|------------|
| **Train Pass** | Enregistrement d'un passage de train avec ses donnees d'inspection |
| **Wagon/Car** | Vehicule individuel composant un train |
| **Spring** | Ressort de suspension d'un bogie |
| **Bogie** | Chariot porteur d'un wagon avec ses essieux |
| **Conf_code** | Code de confiance (0-5) indiquant l'etat d'un ressort |
| **RFID** | Identification par radiofrequence des wagons |
| **Heartbeat** | Signal de vie envoye par les systemes de capture |

### 1.4 References

| Document | Version | Description |
|----------|---------|-------------|
| VICORE V1 - Code Source | 1.x | Application existante |
| Documentation Retro | 1.0 | Analyse de l'existant |
| Normes Eurotunnel | - | Standards internes |

---

## 2. Description Generale

### 2.1 Contexte Metier

Eurotunnel exploite le tunnel sous la Manche reliant la France et l'Angleterre. Les navettes transportant vehicules et passagers sont equipees de systemes de suspension a ressorts dont l'integrite est critique pour la securite.

Des cameras installees aux entrees du tunnel capturent des images des ressorts de chaque wagon. Le systeme VICORE analyse ces images pour detecter d'eventuelles anomalies (ressorts manquants, endommages, etc.).

### 2.2 Objectifs du Projet VICORE V2

| ID | Objectif | Priorite |
|----|----------|----------|
| OBJ-01 | Moderniser l'interface utilisateur | Haute |
| OBJ-02 | Ameliorer les performances | Haute |
| OBJ-03 | Renforcer la securite | Haute |
| OBJ-04 | Faciliter la maintenance | Moyenne |
| OBJ-05 | Preparer l'evolutivite | Moyenne |

### 2.3 Perimetre Fonctionnel

**Inclus dans le projet:**
- Authentification et gestion des utilisateurs
- Visualisation des passages de trains
- Inspection des wagons et ressorts
- Gestion des alertes et confirmations
- Monitoring du systeme de capture
- Interface responsive moderne

**Exclus du projet:**
- Systeme de capture d'images (existant)
- Algorithmes de detection (existant)
- Migration des donnees historiques (phase ulterieure)

### 2.4 Parties Prenantes

| Partie Prenante | Role | Attentes |
|-----------------|------|----------|
| Operateurs Eurotunnel | Utilisateurs principaux | Interface intuitive, alertes claires |
| Responsables Maintenance | Superviseurs | Tableaux de bord, historique |
| Direction Technique | Sponsor | Fiabilite, conformite |
| Equipe IT Eurotunnel | Support | Maintenabilite, documentation |

---

## 3. Acteurs et Roles

### 3.1 Acteurs Humains

#### ACT-01: Operateur
| Attribut | Description |
|----------|-------------|
| **Description** | Personnel de supervision des passages de trains |
| **Responsabilites** | Surveiller les alertes, confirmer les statuts |
| **Frequence d'utilisation** | Continue (24/7) |
| **Niveau technique** | Basique |

#### ACT-02: Superviseur
| Attribut | Description |
|----------|-------------|
| **Description** | Responsable d'equipe de supervision |
| **Responsabilites** | Validation des decisions, rapports |
| **Frequence d'utilisation** | Quotidienne |
| **Niveau technique** | Intermediaire |

#### ACT-03: Administrateur
| Attribut | Description |
|----------|-------------|
| **Description** | Personnel IT de gestion du systeme |
| **Responsabilites** | Gestion utilisateurs, configuration |
| **Frequence d'utilisation** | Hebdomadaire |
| **Niveau technique** | Avance |

### 3.2 Acteurs Systeme

#### ACT-SYS-01: Systeme de Capture
| Attribut | Description |
|----------|-------------|
| **Description** | Cameras et serveurs d'acquisition |
| **Interface** | Ecriture base de donnees, Redis |
| **Donnees** | Images, metadonnees trains |

#### ACT-SYS-02: Systeme d'Analyse
| Attribut | Description |
|----------|-------------|
| **Description** | Algorithmes de detection des ressorts |
| **Interface** | Base de donnees |
| **Donnees** | Conf_codes, positions ressorts |

---

## 4. Exigences Fonctionnelles

### 4.1 Module Authentification

#### EF-AUTH-01: Connexion Utilisateur via SSO
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Le systeme doit permettre aux utilisateurs de s'authentifier via le SSO Eurotunnel |
| **Acteurs** | Operateur, Superviseur, Administrateur |
| **Preconditions** | Compte utilisateur SSO Eurotunnel actif |
| **Postconditions** | Session utilisateur creee |
| **Regles** | - Redirection vers le portail SSO Eurotunnel<br>- Recuperation des informations utilisateur (nom, role) depuis le SSO<br>- Session expire apres 8h d'inactivite<br>- Synchronisation des roles avec l'annuaire Eurotunnel |

#### EF-AUTH-02: Deconnexion
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | L'utilisateur doit pouvoir se deconnecter a tout moment |
| **Acteurs** | Tous |
| **Postconditions** | Session detruite, redirection vers login |

#### EF-AUTH-03: Gestion des Autorisations
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P2 - Important |
| **Description** | L'administrateur peut gerer les autorisations d'acces a VICORE pour les utilisateurs SSO |
| **Acteurs** | Administrateur |
| **Regles** | - Mapping des groupes SSO vers les roles VICORE<br>- Liste blanche des utilisateurs autorises (optionnel)<br>- Historique des connexions |

---

### 4.2 Module Train Passes

#### EF-TP-01: Affichage Liste Train Passes
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher la liste des passages de trains recents |
| **Acteurs** | Operateur, Superviseur |
| **Donnees affichees** | - Date/heure du passage<br>- Identifiant train<br>- Code service<br>- Statut global (couleur)<br>- Installation (Folkestone/Coquelles) |
| **Regles** | - Tri par date decroissante<br>- Pagination (25 par defaut)<br>- Chargement dynamique au scroll |

#### EF-TP-02: Filtrage Train Passes
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P2 - Important |
| **Description** | Filtrer la liste selon differents criteres |
| **Criteres** | - Par installation<br>- Par date<br>- Par statut<br>- Par code service |

#### EF-TP-03: Selection Train Pass
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Selectionner un train pass pour voir ses wagons |
| **Postconditions** | Affichage des wagons du train selectionne |

---

### 4.3 Module Wagons (Cars)

#### EF-CAR-01: Affichage Grille Wagons
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher tous les wagons d'un train pass |
| **Donnees affichees** | - Numero d'ordre<br>- Identifiant (RFID/Coupon)<br>- Icone du type de wagon<br>- Indicateur de statut colore |
| **Regles** | - Affichage dans l'ordre de composition<br>- Liaison visuelle entre wagons couples |

#### EF-CAR-02: Selection Wagon
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Cliquer sur un wagon pour acceder a sa vue detaillee |
| **Postconditions** | Navigation vers la vue Car View |

#### EF-CAR-03: Indicateur Statut Wagon
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher le statut global du wagon par un code couleur |
| **Codes couleur** | - Gris: Non verifie<br>- Vert: OK<br>- Jaune: A verifier<br>- Rouge: Anomalie detectee<br>- Violet: Confirme manuellement |

---

### 4.4 Module Inspection Ressorts

#### EF-SPR-01: Affichage Image Ressort
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher l'image capturee d'un ressort |
| **Fonctionnalites** | - Zoom<br>- Reglage luminosite<br>- Reglage contraste |

#### EF-SPR-02: Diagramme Bogie
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher un schema du bogie avec position des ressorts |
| **Interactions** | - Clic sur un ressort = affichage de son image<br>- Couleur selon conf_code |

#### EF-SPR-03: Navigation Ressorts
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Naviguer entre les ressorts d'un wagon |
| **Controles** | - Boutons Precedent/Suivant<br>- Passage automatique au wagon suivant |

#### EF-SPR-04: Confirmation Manuelle
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Permettre a l'operateur de confirmer le statut d'un ressort |
| **Cas d'usage** | Ressort detecte comme manquant mais present |
| **Options** | - Ressort present<br>- Ressort absent<br>- Incertain (annuler) |
| **Regles** | - Une seule confirmation par ressort<br>- Non modifiable apres confirmation<br>- Trace de l'operateur et date |

#### EF-SPR-05: Affichage Images Alternatives
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P2 - Important |
| **Description** | Lors d'une anomalie, afficher toutes les images disponibles |
| **Utilite** | Permettre une verification complete avant confirmation |

#### EF-SPR-06: Historique Photos Multi-Passages
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P2 - Important |
| **Description** | Visualiser les photos d'un meme ressort sur plusieurs passages successifs |
| **Acteurs** | Operateur, Superviseur |
| **Fonctionnalites** | - Affichage chronologique des images<br>- Comparaison cote a cote (2-4 images)<br>- Navigation entre les passages<br>- Indication du statut a chaque passage |
| **Criteres** | - Identification par position (wagon + bogie + essieu + cote)<br>- Historique sur les 30 derniers jours minimum<br>- Limite de 50 passages affiches |
| **Utilite** | Suivre l'evolution de l'etat d'un ressort dans le temps |

#### EF-SPR-07: Annulation Confirmation Ressort Manquant
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Permettre a l'operateur d'annuler une confirmation de ressort manquant |
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Ressort precedemment confirme comme manquant<br>- Passage datant de moins de 24h |
| **Postconditions** | - Statut ressort reinitialise<br>- Historique de l'annulation enregistre |
| **Regles** | - Motif d'annulation obligatoire<br>- Trace complete (operateur, date, motif)<br>- Notification au superviseur si annulation |

---

### 4.5 Module Monitoring

#### EF-MON-01: Statut Systemes
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher l'etat de sante des systemes de capture |
| **Indicateurs** | - Heartbeat (dernier signal)<br>- Statut cameras<br>- Temperatures |
| **Regles** | - Alerte si heartbeat > 60s<br>- Rafraichissement automatique |

#### EF-MON-02: Indicateur Global
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Afficher un indicateur global dans l'en-tete |
| **Etats** | - Vert: Tous systemes OK<br>- Rouge: Au moins un systeme en erreur<br>- Bleu: Statut inconnu |

---

### 4.6 Module Audit et Rapports (Superviseur)

#### EF-AUD-01: Consultation Historique Operations
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P1 - Obligatoire |
| **Description** | Permettre aux superviseurs de consulter l'historique complet des operations |
| **Acteurs** | Superviseur, Administrateur |
| **Types d'operations** | - Connexions/deconnexions utilisateurs<br>- Confirmations de ressorts<br>- Annulations de confirmations<br>- Modifications de statut |
| **Donnees affichees** | - Date/heure de l'operation<br>- Type d'operation<br>- Utilisateur concerne<br>- Details (ressort, wagon, train)<br>- Adresse IP |
| **Filtres** | - Par periode (date debut/fin)<br>- Par utilisateur<br>- Par type d'operation<br>- Par train/wagon |
| **Regles** | - Acces restreint aux superviseurs et administrateurs<br>- Historique conserve 1 an minimum<br>- Export possible (CSV, PDF) |

#### EF-AUD-02: Generation Rapports Operations
| Attribut | Valeur |
|----------|--------|
| **Priorite** | P2 - Important |
| **Description** | Generer des rapports d'activite entre deux dates |
| **Acteurs** | Superviseur, Administrateur |
| **Parametres** | - Date de debut (obligatoire)<br>- Date de fin (obligatoire)<br>- Type de rapport (synthese/detail)<br>- Filtres optionnels (utilisateur, type operation) |
| **Contenu rapport** | - Resume statistique (nombre operations par type)<br>- Liste detaillee des operations<br>- Graphiques d'activite<br>- Anomalies detectees |
| **Formats export** | - PDF (impression)<br>- CSV (analyse)<br>- Excel (traitement) |
| **Regles** | - Periode maximale: 90 jours<br>- Generation asynchrone si > 30 jours<br>- Notification par email a la fin |

---

### 4.7 Matrice de Tracabilite Exigences

| ID Exigence | Cas d'Utilisation | Test |
|-------------|-------------------|------|
| EF-AUTH-01 | UC-01 | TF-01 |
| EF-AUTH-02 | UC-02 | TF-02 |
| EF-TP-01 | UC-03 | TF-03 |
| EF-TP-02 | UC-04 | TF-04 |
| EF-CAR-01 | UC-05 | TF-05 |
| EF-SPR-01 | UC-06 | TF-06 |
| EF-SPR-04 | UC-07 | TF-07 |
| EF-SPR-06 | UC-09 | TF-09 |
| EF-SPR-07 | UC-10 | TF-10 |
| EF-MON-01 | UC-08 | TF-08 |
| EF-AUD-01 | UC-11 | TF-11 |
| EF-AUD-02 | UC-12 | TF-12 |

---

## 5. Exigences Non-Fonctionnelles

### 5.1 Performance

#### ENF-PERF-01: Temps de Reponse
| Attribut | Valeur |
|----------|--------|
| **Description** | Temps de reponse des pages |
| **Objectif** | < 2 secondes pour 95% des requetes |
| **Mesure** | Temps entre clic et affichage complet |

#### ENF-PERF-02: Temps Chargement Images
| Attribut | Valeur |
|----------|--------|
| **Description** | Chargement des images de ressorts |
| **Objectif** | < 3 secondes par image |
| **Mesure** | Temps de telechargement + rendu |

#### ENF-PERF-03: Utilisateurs Simultanes
| Attribut | Valeur |
|----------|--------|
| **Description** | Nombre d'utilisateurs simultanes |
| **Objectif** | 20 utilisateurs sans degradation |

### 5.2 Securite

#### ENF-SEC-01: Authentification SSO
| Attribut | Valeur |
|----------|--------|
| **Description** | Securisation de l'authentification via SSO Eurotunnel |
| **Exigences** | - HTTPS obligatoire<br>- Integration SSO Eurotunnel (SAML/OAuth2)<br>- Protection CSRF<br>- Validation des tokens SSO |

#### ENF-SEC-02: Autorisation
| Attribut | Valeur |
|----------|--------|
| **Description** | Controle d'acces |
| **Exigences** | - Verification session sur chaque requete<br>- Pas d'acces direct aux ressources |

#### ENF-SEC-03: Donnees Sensibles
| Attribut | Valeur |
|----------|--------|
| **Description** | Protection des donnees |
| **Exigences** | - Pas de secrets dans le code<br>- Variables d'environnement<br>- Logs sans donnees sensibles |

### 5.3 Disponibilite

#### ENF-DISPO-01: Uptime
| Attribut | Valeur |
|----------|--------|
| **Description** | Disponibilite du service |
| **Objectif** | 99.5% (hors maintenance planifiee) |

#### ENF-DISPO-02: Maintenance
| Attribut | Valeur |
|----------|--------|
| **Description** | Fenetres de maintenance |
| **Contrainte** | Maintenance planifiee de nuit uniquement |

### 5.4 Maintenabilite

#### ENF-MAINT-01: Documentation
| Attribut | Valeur |
|----------|--------|
| **Description** | Documentation du code |
| **Exigences** | - Docstrings sur toutes les fonctions publiques<br>- README a jour<br>- Guide de deploiement |

#### ENF-MAINT-02: Logs
| Attribut | Valeur |
|----------|--------|
| **Description** | Journalisation |
| **Exigences** | - Logs structures (JSON)<br>- Niveaux (DEBUG, INFO, WARNING, ERROR)<br>- Rotation automatique |

### 5.5 Compatibilite

#### ENF-COMPAT-01: Navigateurs
| Attribut | Valeur |
|----------|--------|
| **Description** | Navigateurs supportes |
| **Liste** | - Chrome 90+<br>- Firefox 90+<br>- Edge 90+<br>- Safari 14+ |

#### ENF-COMPAT-02: Resolution
| Attribut | Valeur |
|----------|--------|
| **Description** | Resolutions d'ecran |
| **Minimum** | 1280 x 720 |
| **Optimale** | 1920 x 1080 |

### 5.6 Internationalisation

#### ENF-I18N-01: Langues Supportees
| Attribut | Valeur |
|----------|--------|
| **Description** | Langues de l'interface utilisateur |
| **Langues** | - Francais (fr)<br>- Anglais (en) |
| **Langue par defaut** | Determinee par le navigateur (si FR -> francais, sinon anglais) |
| **Couverture** | 100% des textes de l'interface |

#### ENF-I18N-02: Selection de Langue
| Attribut | Valeur |
|----------|--------|
| **Description** | Choix de la langue par l'utilisateur |
| **Mecanisme** | - Detection automatique depuis navigateur (`navigator.language`)<br>- Si langue navigateur FR -> francais par defaut<br>- Sinon anglais par defaut<br>- Selecteur de langue [FR\|EN] sur la page de login et dans l'en-tete<br>- Preference sauvegardee dans localStorage et en base utilisateur |

#### ENF-I18N-03: Contenu Localise
| Attribut | Valeur |
|----------|--------|
| **Description** | Elements a traduire |
| **Elements** | - Labels et boutons<br>- Messages d'erreur<br>- Notifications et alertes<br>- Textes d'aide<br>- Formats de date/heure |

#### ENF-I18N-04: Formats Regionaux
| Attribut | Valeur |
|----------|--------|
| **Description** | Adaptation des formats selon la locale |
| **Formats** | - Dates: DD/MM/YYYY (fr) vs MM/DD/YYYY (en)<br>- Heures: 24h (fr) vs 12h AM/PM (en)<br>- Nombres: 1 234,56 (fr) vs 1,234.56 (en) |

### 5.7 Affichage Version

#### ENF-VER-01: Numero de Version
| Attribut | Valeur |
|----------|--------|
| **Description** | Affichage du numero de version du logiciel |
| **Emplacement** | - Footer de la page de connexion<br>- Menu "A propos" ou info-bulle dans l'interface |
| **Format** | "VICORE vX.Y.Z" (ex: "VICORE v2.0.0") |
| **Mise a jour** | Version mise a jour a chaque deploiement |

### 5.8 Equipements Configurables

#### ENF-EQUIP-01: Liste Equipements Dynamique
| Attribut | Valeur |
|----------|--------|
| **Description** | Les equipements (sites d'installation) sont configurables depuis la base de donnees |
| **Equipements actuels** | - Voie D (anciennement Folkestone)<br>- Voie E (anciennement Coquelles) |
| **Configuration** | Table `installations` en base de donnees |
| **Avantage** | Ajout/modification d'equipements sans modification du code source |

### 5.9 Types de Wagon

#### ENF-WAGON-01: Types de Wagon
| Attribut | Valeur |
|----------|--------|
| **Description** | Affichage du type de wagon sur chaque carte wagon |
| **Types** | - Locomotive (Loco)<br>- Wagon Chargeur (Chargeur)<br>- Wagon Porteur (Porteur) |
| **Affichage** | Sous l'identifiant RFID sur chaque carte wagon |

### 5.10 Sens de Circulation du Train

#### ENF-DIR-01: Sens de Circulation
| Attribut | Valeur |
|----------|--------|
| **Description** | Affichage du sens de circulation du train |
| **Source** | Donnee fournie par le systeme de captation d'images (lecture seule) |
| **Valeurs** | - **Sens normal** (vert): Sortie tunnel vers quais (direction nominale)<br>- **En tiroir** (jaune): Quais vers entree tunnel (direction inversee) |
| **Affichage** | Badge dans les metadonnees de chaque train pass |
| **Caracteristiques** | - Non modifiable par l'operateur<br>- Determine automatiquement par le systeme de captation<br>- Propre a chaque passage de train |

#### ENF-DIR-02: Impact du Sens de Circulation
| Attribut | Valeur |
|----------|--------|
| **Description** | Impact du sens de circulation sur l'interpretation des donnees |
| **Impact visuel** | La direction influence l'interpretation des positions Menant/Mene des ressorts |
| **Impact operationnel** | L'operateur doit tenir compte du sens pour interpreter correctement les positions des ressorts |

### 5.11 Nomenclature des Ressorts

#### ENF-SPRING-01: Identification des Ressorts
| Attribut | Valeur |
|----------|--------|
| **Description** | Nomenclature d'identification des ressorts |
| **Structure** | Wagon ID + Bogie + Essieu + Cote (Gauche/Droit) + Position (Menant/Mene) |
| **Positions ressort** | - Menant (Leading): Ressort avant la roue dans le sens de marche<br>- Mene (Trailing): Ressort apres la roue dans le sens de marche |
| **Total par wagon** | 16 ressorts (2 bogies x 2 essieux x 2 roues x 2 ressorts) |

---

## 6. Contraintes

### 6.1 Contraintes Techniques

| ID | Contrainte | Impact |
|----|------------|--------|
| CT-01 | Base de donnees PostgreSQL existante | Schema a respecter |
| CT-02 | Cache Redis existant | Interface a maintenir |
| CT-03 | Images stockees sur filesystem | Chemins a respecter |
| CT-04 | Deploiement Docker | Conteneurisation obligatoire |

### 6.2 Contraintes Organisationnelles

| ID | Contrainte | Impact |
|----|------------|--------|
| CO-01 | Deploiement en heures creuses | Planning MEP |
| CO-02 | Formation utilisateurs | Temps supplementaire |
| CO-03 | Support bilingue FR/EN | Documentation double |

### 6.3 Contraintes Reglementaires

| ID | Contrainte | Impact |
|----|------------|--------|
| CR-01 | RGPD | Gestion des logs utilisateurs |
| CR-02 | Tracabilite des actions | Audit trail obligatoire |

---

## 7. Annexes

### 7.1 Glossaire Complet

| Terme | Definition |
|-------|------------|
| Axle | Essieu d'un bogie |
| Bogie | Chariot porteur avec roues et suspension |
| Conf_code | Code de confiance (0=confirme OK, 1=OK, 2=incertain, 3=anomalie) |
| Heartbeat | Signal periodique indiquant le bon fonctionnement |
| Train Pass | Enregistrement d'un passage de train |
| Spring | Ressort de suspension |

### 7.2 Historique des Modifications

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 0.1 | 2026-01-18 | - | Ebauche initiale |
| 1.0 | 2026-01-18 | - | Version complete pour validation |

---

## Signatures

| Role | Nom | Date | Signature |
|------|-----|------|-----------|
| MOA - Representant Client | | | |
| MOE - Chef de Projet | | | |
| MOE - Architecte | | | |

---

*Document genere le 2026-01-18*
