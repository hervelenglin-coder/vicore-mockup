# VICORE V2 - Specification Fonctionnelle Generale (SFG)

## Document Control

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 2026-01-18 | - | Creation initiale |

---

## Table des Matieres

1. [Introduction](#1-introduction)
2. [Cas d'Utilisation](#2-cas-dutilisation)
3. [Maquettes IHM](#3-maquettes-ihm)
4. [Regles de Gestion](#4-regles-de-gestion)
5. [Workflows](#5-workflows)
6. [Interfaces](#6-interfaces)

---

## 1. Introduction

### 1.1 Objectif

Ce document decrit les specifications fonctionnelles detaillees du systeme VICORE V2. Il traduit les exigences du SRS en specifications implementables.

### 1.2 Liens avec le SRS

Chaque fonctionnalite est liee aux exigences du document SRS via une matrice de tracabilite.

---

## 2. Cas d'Utilisation

### 2.1 Diagramme des Cas d'Utilisation

```
                          +------------------+
                          |     VICORE V2    |
                          +------------------+
                                   |
        +--------------------------+---------------------------+
        |                          |                           |
+-------+-------+          +-------+-------+           +-------+-------+
|  Operateur    |          |  Superviseur  |           | Administrateur|
+---------------+          +---------------+           +---------------+
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-01: Connexion |<---+---------------------------+
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-02: Voir      |<---+                           |
        |  | Train Passes     |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-03: Inspecter |<---+                           |
        |  | Wagon            |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-04: Analyser  |<---+                           |
        |  | Ressort          |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-05: Confirmer |<---+                           |
        |  | Statut           |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-06: Consulter |<---+---------------------------+
        |  | Monitoring       |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-08: Historique|<---+                           |
        |  | Photos Ressort   |    |                           |
        |  +------------------+    |                           |
        |                          |                           |
        |  +------------------+    |                           |
        +->| UC-09: Annuler   |<---+                           |
           | Confirmation     |    |                           |
           +------------------+    |                           |
                                   |                           |
           +------------------+    |                           |
           | UC-10: Historique|<---+---------------------------+
           | Operations       |    |                           |
           +------------------+    |                           |
                                   |                           |
           +------------------+    |                           |
           | UC-11: Generer   |<---+---------------------------+
           | Rapports         |    |                           |
           +------------------+    |                           |
                                   |                           |
                               +------------------+            |
                               | UC-07: Gerer     |<-----------+
                               | Utilisateurs     |
                               +------------------+
```

---

### 2.2 Description des Cas d'Utilisation

#### UC-01: Se Connecter via SSO Eurotunnel

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur, Administrateur |
| **Preconditions** | - Compte SSO Eurotunnel actif<br>- Acces reseau |
| **Postconditions** | - Session utilisateur creee<br>- Redirection vers page d'accueil |
| **Exigences liees** | EF-AUTH-01 |

**Scenario Principal:**
1. L'utilisateur accede a l'URL de l'application
2. Le systeme detecte l'absence de session valide
3. Le systeme redirige vers le portail SSO Eurotunnel
4. L'utilisateur s'authentifie sur le portail SSO (identifiants Eurotunnel)
5. Le SSO redirige vers VICORE avec un token d'authentification
6. Le systeme valide le token SSO
7. Le systeme recupere les informations utilisateur (nom, role)
8. Le systeme cree une session locale
9. Le systeme redirige vers la page System View

**Scenarios Alternatifs:**

*4a. Echec authentification SSO:*
1. Le portail SSO affiche un message d'erreur
2. L'utilisateur doit contacter le support IT Eurotunnel

*6a. Token SSO invalide:*
1. Le systeme affiche un message d'erreur
2. Le systeme redirige vers le portail SSO

*7a. Utilisateur non autorise dans VICORE:*
1. Le systeme affiche un message indiquant que l'acces a VICORE n'est pas autorise
2. L'utilisateur doit contacter l'administrateur VICORE

---

#### UC-02: Consulter les Train Passes

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Utilisateur connecte |
| **Postconditions** | - Liste des train passes affichee |
| **Exigences liees** | EF-TP-01, EF-TP-02, EF-TP-03 |

**Scenario Principal:**
1. L'utilisateur accede a la page System View
2. Le systeme charge les train passes recents
3. Le systeme affiche la liste par installation
4. L'utilisateur visualise les statuts
5. L'utilisateur peut faire defiler pour charger plus

**Scenarios Alternatifs:**

*2a. Aucun train pass:*
1. Le systeme affiche un message "Aucun passage recent"

*5a. Filtrage:*
1. L'utilisateur selectionne un filtre
2. Le systeme met a jour la liste

---

#### UC-03: Inspecter un Wagon

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Train pass selectionne |
| **Postconditions** | - Details du wagon affiches |
| **Exigences liees** | EF-CAR-01, EF-CAR-02, EF-CAR-03 |

**Scenario Principal:**
1. L'utilisateur selectionne un train pass
2. Le systeme affiche la grille des wagons
3. L'utilisateur clique sur un wagon
4. Le systeme charge la vue Car View
5. Le systeme affiche le premier ressort

---

#### UC-04: Analyser un Ressort

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Wagon selectionne |
| **Postconditions** | - Image ressort affichee |
| **Exigences liees** | EF-SPR-01, EF-SPR-02, EF-SPR-03 |

**Scenario Principal:**
1. L'utilisateur visualise l'image du ressort
2. L'utilisateur peut ajuster luminosite/contraste
3. L'utilisateur peut naviguer (precedent/suivant)
4. L'utilisateur peut cliquer sur le diagramme bogie

---

#### UC-05: Confirmer le Statut d'un Ressort

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur |
| **Preconditions** | - Ressort en anomalie (conf_code > 2)<br>- Pas deja confirme |
| **Postconditions** | - Statut enregistre<br>- Indicateurs mis a jour |
| **Exigences liees** | EF-SPR-04, EF-SPR-05 |

**Scenario Principal:**
1. Le systeme affiche le bouton "Confirmer ressort manquant"
2. L'utilisateur clique sur le bouton
3. Le systeme affiche une modale avec toutes les images
4. L'utilisateur examine les images
5. L'utilisateur clique sur "Ressort Present" ou "Ressort Absent"
6. Le systeme enregistre la confirmation
7. Le systeme met a jour les indicateurs

**Scenarios Alternatifs:**

*5a. Utilisateur incertain:*
1. L'utilisateur clique sur "Incertain - Fermer"
2. La modale se ferme
3. Aucune confirmation enregistree

---

#### UC-06: Consulter le Monitoring

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur, Administrateur |
| **Preconditions** | - Utilisateur connecte |
| **Postconditions** | - Statut systemes affiche |
| **Exigences liees** | EF-MON-01, EF-MON-02 |

**Scenario Principal:**
1. L'utilisateur clique sur l'indicateur de statut
2. Le systeme affiche le dropdown avec les systemes
3. L'utilisateur peut cliquer sur un systeme
4. Le systeme affiche les details (heartbeat, cameras)

---

#### UC-08: Consulter l'Historique Photos d'un Ressort

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Utilisateur connecte<br>- Ressort selectionne dans Car View |
| **Postconditions** | - Historique des images affiche |
| **Exigences liees** | EF-SPR-06 |

**Scenario Principal:**
1. L'utilisateur visualise un ressort dans la Car View
2. L'utilisateur clique sur le bouton "Historique"
3. Le systeme recherche les passages precedents du meme wagon
4. Le systeme affiche les images du meme ressort sur plusieurs passages
5. L'utilisateur peut comparer les images cote a cote
6. L'utilisateur peut naviguer entre les passages

**Scenarios Alternatifs:**

*3a. Aucun passage anterieur:*
1. Le systeme affiche "Aucun passage anterieur trouve pour ce wagon"

*5a. Selection pour comparaison:*
1. L'utilisateur coche les passages a comparer (2 a 4 max)
2. Le systeme affiche les images selectionnees cote a cote

---

#### UC-09: Annuler une Confirmation de Ressort Manquant

| Champ | Description |
|-------|-------------|
| **Acteurs** | Operateur, Superviseur |
| **Preconditions** | - Ressort precedemment confirme comme manquant<br>- Passage datant de moins de 24h |
| **Postconditions** | - Confirmation annulee<br>- Statut ressort reinitialise<br>- Notification au superviseur |
| **Exigences liees** | EF-SPR-07 |

**Scenario Principal:**
1. L'utilisateur visualise un ressort confirme "Manquant"
2. Le systeme affiche le bouton "Annuler confirmation"
3. L'utilisateur clique sur le bouton
4. Le systeme affiche une modale de confirmation
5. L'utilisateur saisit un motif d'annulation (obligatoire)
6. L'utilisateur clique sur "Confirmer annulation"
7. Le systeme enregistre l'annulation avec tracabilite
8. Le systeme reinitialise le statut du ressort
9. Le systeme notifie le superviseur de l'annulation

**Scenarios Alternatifs:**

*2a. Passage trop ancien (> 24h):*
1. Le bouton "Annuler confirmation" n'est pas affiche
2. Un message indique "Annulation impossible apres 24h"

*5a. Motif non saisi:*
1. Le bouton "Confirmer annulation" reste grise
2. Un message indique "Motif obligatoire"

*6a. Annulation par l'utilisateur:*
1. L'utilisateur clique sur "Fermer"
2. La modale se ferme sans modification

---

#### UC-10: Consulter l'Historique des Operations (Audit Trail)

| Champ | Description |
|-------|-------------|
| **Acteurs** | Superviseur, Administrateur |
| **Preconditions** | - Utilisateur connecte avec role Superviseur ou Admin |
| **Postconditions** | - Historique des operations affiche |
| **Exigences liees** | EF-AUD-01 |

**Scenario Principal:**
1. L'utilisateur accede au menu "Audit" dans la navigation
2. Le systeme affiche la page d'historique des operations
3. Le systeme charge les operations recentes (7 derniers jours par defaut)
4. L'utilisateur peut filtrer par criteres (date, utilisateur, type)
5. L'utilisateur peut consulter les details d'une operation
6. L'utilisateur peut exporter la liste (CSV, PDF)

**Scenarios Alternatifs:**

*3a. Aucune operation:*
1. Le systeme affiche "Aucune operation pour les criteres selectionnes"

*4a. Filtre par utilisateur:*
1. L'utilisateur selectionne un utilisateur dans la liste
2. Le systeme filtre les operations de cet utilisateur

*6a. Export PDF:*
1. Le systeme genere un PDF avec en-tete et mise en page
2. Le fichier est telecharge automatiquement

---

#### UC-11: Generer un Rapport d'Operations

| Champ | Description |
|-------|-------------|
| **Acteurs** | Superviseur, Administrateur |
| **Preconditions** | - Utilisateur connecte avec role Superviseur ou Admin |
| **Postconditions** | - Rapport genere et telecharge |
| **Exigences liees** | EF-AUD-02 |

**Scenario Principal:**
1. L'utilisateur accede a la page "Rapports" via le menu
2. L'utilisateur selectionne la date de debut
3. L'utilisateur selectionne la date de fin
4. L'utilisateur choisit le type de rapport (synthese ou detail)
5. L'utilisateur clique sur "Generer rapport"
6. Le systeme genere le rapport
7. Le systeme affiche un apercu du rapport
8. L'utilisateur peut telecharger (PDF, CSV, Excel)

**Scenarios Alternatifs:**

*2a. Dates invalides:*
1. Date fin < Date debut
2. Le systeme affiche "La date de fin doit etre posterieure a la date de debut"

*5a. Periode > 90 jours:*
1. Le systeme affiche "Periode maximale: 90 jours"
2. L'utilisateur doit reduire la periode

*6a. Periode > 30 jours:*
1. Le systeme affiche "Generation en cours..."
2. Le systeme envoie une notification par email a la fin
3. Le rapport est disponible dans "Mes rapports"

---

## 3. Maquettes IHM

### 3.1 Page de Connexion (SSO Eurotunnel)

```
+------------------------------------------------------------------+
|                                                    [FR] [EN]      |
|                           VICORE                                  |
|                    Spring Analysis System                         |
|             VIsualisation COntrole REssorts                       |
|                                                                   |
|         +------------------------------------------+              |
|         |                                          |              |
|         |           Bienvenue                      |              |
|         |                                          |              |
|         |   Cliquez sur le bouton ci-dessous      |              |
|         |   pour vous connecter avec votre        |              |
|         |   compte Eurotunnel                      |              |
|         |                                          |              |
|         |   +----------------------------------+   |              |
|         |   |    CONNEXION SSO EUROTUNNEL     |   |              |
|         |   +----------------------------------+   |              |
|         |                                          |              |
|         |   [Logo Eurotunnel]                      |              |
|         |                                          |              |
|         +------------------------------------------+              |
|                                                                   |
|                       VICORE v2.0.0                               |
+------------------------------------------------------------------+
```

**Elements:**
- Selecteur de langue [FR|EN]: En haut a droite, detecte automatiquement la langue du navigateur
- Panneau gauche: Logo VICORE avec effet lumineux
- Panneau droit: Bouton de connexion SSO
- Bouton: "Connexion SSO Eurotunnel" - redirige vers le portail SSO
- Logo Eurotunnel pour identification visuelle
- Footer: Numero de version (ex: "VICORE v2.0.0")
- Style: Dark theme avec accents neon
- Langue par defaut: FR si navigateur francais, EN sinon

---

### 3.2 Vue Systeme (System View)

```
+------------------------------------------------------------------+
| [LOGO] VICORE  [Status: Online]  [14:32:45] [FR|EN] [OP] [Logout] |
+------------------------------------------------------------------+
|                                                                   |
| +------------------+  |  +------------------------------------+  |
| | TRAIN PASSES     |  |  | 9N57 - 1234                        |  |
| |                  |  |  | 2026-01-17 14:32:45                |  |
| | VOIE D           |  |  | Direction: France > UK | Normal    |  |
| | +-------------+  |  |  |                                    |  |
| | | 9N57-1234   |  |  |  | SPRINGS: 192  WARN: 3  CRIT: 0    |  |
| | | 14:32 [OK]  |  |  |  |                                    |  |
| | +-------------+  |  |  | Legende: [OK][!!][XX][**] [?]     |  |
| | | 2K18-5678   |  |  |  |                                    |  |
| | | 14:28 [!!]  |  |  |  | +------+ +------+ +------+ +------+|  |
| | +-------------+  |  |  | |  W1  | |  W2  | |  W3  | |  W4  ||  |
| | | 1M00-9012   |  |  |  | | Loco | |Charg.| |Port. | |Port. ||  |
| | | 14:15 [OK]  |  |  |  | | [OK] | | [!!] | | [OK] | | [OK] ||  |
| | +-------------+  |  |  | +------+ +------+ +------+ +------+|  |
| |                  |  |  |                                    |  |
| | VOIE E           |  |  | +------+ +------+ +------+ +------+|  |
| | +-------------+  |  |  | |  W5  | |  W6  | |  W7  | |  W8  ||  |
| | | 4R56-2345   |  |  |  | |Port. | |Port. | |Port. | |Port. ||  |
| | | 14:30 [OK]  |  |  |  | | [!!] | | [--] | | [OK] | | [OK] ||  |
| | +-------------+  |  |  | +------+ +------+ +------+ +------+|  |
| |                  |  |  +------------------------------------+  |
| | [Load More]      |                                             |
| +------------------+                                             |
+------------------------------------------------------------------+
```

**Elements:**
- Header: Logo, Status, Heure, Langue, Utilisateur, Logout
- Panneau gauche: Liste train passes par installation (Voie D, Voie E)
- Panneau droit: Grille des wagons du train selectionne
- Direction train: "Normal" ou "Tiroir" affiche avec la direction geographique
- Type wagon: Affiche sous le numero (Loco, Chargeur, Porteur)
- Legende avec bouton [?] pour popup explicatif des statuts
- Statistiques: Compteurs springs/warnings/criticals

**Note:** Les noms des equipements (Voie D, Voie E, etc.) sont configurables depuis la base de donnees (table `installations`).

---

### 3.3 Vue Wagon (Car View)

```
+------------------------------------------------------------------+
| [LOGO] VICORE  [Status: Online]  [14:32:45] [FR|EN] [OP] [Logout] |
+------------------------------------------------------------------+
|                                                                   |
| +------+ | +----------------------------+ | +------------------+ |
| | W1   | | |                            | | | RFID: 4522       | |
| | [OK] | | |      [SPRING IMAGE]        | | | Type: Chargeur   | |
| +------+ | |                            | | |                  | |
| | W2   | | | Bogie 1 - Essieu 2         | | |  BOGIE 1 (Avant) | |
| | [!!] | | | Gauche - Menant            | | | +------------+   | |
| +------+ | +----------------------------+ | | | Essieu 1   |   | |
| | W3   | |                                | | |  [M]O[m]   |   | |
| | [OK] | | Contraste: [=======----]      | | |  [M]O[m]   |   | |
| +------+ | Luminosite: [======-----]     | | +------------+   | |
| | W4   | | Zoom: [========---]           | | | Essieu 2   |   | |
| | [OK] | |                                | | | [!]O[m]   |   | |
| +------+ | [<- Prec]  [Histo]  [Suiv ->] | | |  [M]O[m]   |   | |
|          |                                | | +------------+   | |
|          | [Confirmer le statut]         | |                  | |
|          |                                | |  BOGIE 2 (Arr.) | |
|          |                                | | +------------+   | |
|          |                                | | | Essieu 1   |   | |
|          |                                | | |  [M]O[m]   |   | |
|          |                                | | |  [M]O[m]   |   | |
|          |                                | | +------------+   | |
|          |                                | | Legende:        | |
|          |                                | | M=Menant m=Mene | |
|          |                                | | O = Roue        | |
|          |                                | | [<- Liste]      | |
|          |                                | +------------------+ |
+------------------------------------------------------------------+
```

**Elements:**
- Panneau gauche: Liste wagons (vertical)
- Panneau central: Image ressort + controles (contraste, luminosite, zoom)
- Panneau droit: Diagramme bogie avec nomenclature Menant/Mene
- Position ressort: Format "Bogie X - Essieu Y - Cote (G/D) - Menant/Mene"
- Diagramme bogie: Representation fidele avec 2 ressorts par roue
  - [M] = Menant (Leading): Ressort avant la roue dans le sens de marche
  - [m] = Mene (Trailing): Ressort apres la roue dans le sens de marche
  - O = Roue
- Total: 16 ressorts par wagon (2 bogies x 2 essieux x 2 roues x 2 ressorts)

---

### 3.4 Modale Confirmation Ressort

```
+------------------------------------------------------------------+
|                  Confirm Spring Status                      [X]   |
+------------------------------------------------------------------+
|                                                                   |
|  +----------+  +----------+  +----------+  +----------+          |
|  |  IMG 1   |  |  IMG 2   |  |  IMG 3   |  |  IMG 4   |          |
|  |          |  |          |  |          |  |          |          |
|  +----------+  +----------+  +----------+  +----------+          |
|                                                                   |
|  +----------+  +----------+  +----------+  +----------+          |
|  |  IMG 5   |  |  IMG 6   |  |  IMG 7   |  |  IMG 8   |          |
|  |          |  |          |  |          |  |          |          |
|  +----------+  +----------+  +----------+  +----------+          |
|                                                                   |
+------------------------------------------------------------------+
| [Spring Present]   [Spring Missing]   [Unsure - Close]           |
+------------------------------------------------------------------+
```

---

### 3.5 Vue Historique Photos Ressort (Spring History)

```
+------------------------------------------------------------------+
| [LOGO] VICORE  [Status: Online]  [14:32:45] [FR|EN] [OP] [Logout] |
+------------------------------------------------------------------+
|                                                                   |
|  Historique Photos - Wagon W2 - Bogie 1 - Essieu 1 - Position A  |
|  +---------------------------------------------------------------+|
|  | Filtres:  [x] 30 derniers jours  [ ] 60 jours  [ ] 90 jours  ||
|  +---------------------------------------------------------------+|
|                                                                   |
|  +-------------+ +-------------+ +-------------+ +-------------+ |
|  | 17/01/2026  | | 15/01/2026  | | 12/01/2026  | | 08/01/2026  | |
|  | 14:32       | | 09:15       | | 18:42       | | 11:23       | |
|  | Train 9N57  | | Train 2K18  | | Train 9N57  | | Train 4R56  | |
|  +-------------+ +-------------+ +-------------+ +-------------+ |
|  |             | |             | |             | |             | |
|  |   [IMG]     | |   [IMG]     | |   [IMG]     | |   [IMG]     | |
|  |             | |             | |             | |             | |
|  +-------------+ +-------------+ +-------------+ +-------------+ |
|  | Status:[OK] | | Status:[OK] | | Status:[!!] | | Status:[OK] | |
|  | [ ] Select  | | [ ] Select  | | [x] Select  | | [ ] Select  | |
|  +-------------+ +-------------+ +-------------+ +-------------+ |
|                                                                   |
|  [Comparer selection (1/4)]            [<- Retour Car View]      |
+------------------------------------------------------------------+
```

**Vue Comparaison:**
```
+------------------------------------------------------------------+
|                  Comparaison Images                          [X]  |
+------------------------------------------------------------------+
|                                                                   |
|  +---------------------------+  +---------------------------+    |
|  | 12/01/2026 - 18:42        |  | 08/01/2026 - 11:23        |    |
|  | Train 9N57 - Status: [!!] |  | Train 4R56 - Status: [OK] |    |
|  +---------------------------+  +---------------------------+    |
|  |                           |  |                           |    |
|  |                           |  |                           |    |
|  |         [IMAGE]           |  |         [IMAGE]           |    |
|  |                           |  |                           |    |
|  |                           |  |                           |    |
|  +---------------------------+  +---------------------------+    |
|                                                                   |
|  [Fermer]                                                        |
+------------------------------------------------------------------+
```

**Elements:**
- En-tete: Identification complete du ressort (wagon, bogie, essieu, position)
- Filtre temporel: Selection de la periode a afficher
- Grille chronologique: Images avec date, train et statut
- Selection: Checkboxes pour comparaison (2 a 4 images)
- Bouton comparaison: Ouvre vue cote a cote

---

### 3.6 Modale Annulation Confirmation

```
+------------------------------------------------------------------+
|              Annuler la confirmation                         [X]  |
+------------------------------------------------------------------+
|                                                                   |
|  Ressort confirme "MANQUANT" le 17/01/2026 a 14:35               |
|  Par: Jean Dupont                                                 |
|                                                                   |
|  +--------------------------------------------------------------+|
|  | Motif d'annulation (obligatoire):                            ||
|  | +----------------------------------------------------------+ ||
|  | | Le ressort a ete mal identifie, il est en fait present  | ||
|  | | sur les images alternatives.                             | ||
|  | +----------------------------------------------------------+ ||
|  +--------------------------------------------------------------+|
|                                                                   |
|  [!] Cette action sera enregistree et notifiee au superviseur    |
|                                                                   |
+------------------------------------------------------------------+
| [Annuler]                            [Confirmer l'annulation]    |
+------------------------------------------------------------------+
```

**Elements:**
- Rappel de la confirmation d'origine (date, operateur)
- Zone de texte obligatoire pour le motif
- Avertissement sur la tracabilite
- Boutons d'action

---

### 3.7 Page Audit Trail (Historique Operations)

```
+------------------------------------------------------------------+
| [LOGO] VICORE  [Status: Online]  [14:32:45] [FR|EN] [SUP] [Logout]|
+------------------------------------------------------------------+
| [Train Passes] [Audit Trail] [Rapports]                          |
+------------------------------------------------------------------+
|                                                                   |
|  HISTORIQUE DES OPERATIONS                                       |
|  +---------------------------------------------------------------+|
|  | Filtres:                                                      ||
|  | Periode: [01/01/2026] a [17/01/2026]  Utilisateur: [Tous  v] ||
|  | Type: [Tous v]                        [Appliquer] [Reset]    ||
|  +---------------------------------------------------------------+|
|                                                                   |
|  +---------------------------------------------------------------+|
|  | Date/Heure   | Utilisateur | Type         | Details          ||
|  +---------------------------------------------------------------+|
|  | 17/01 14:35  | J. Dupont   | Confirmation | W2-B1-A1-A ABSENT||
|  | 17/01 14:32  | J. Dupont   | Connexion    | IP: 10.0.1.45    ||
|  | 17/01 14:28  | M. Martin   | Annulation   | W5-B2-A2-B Motif ||
|  | 17/01 14:15  | M. Martin   | Confirmation | W8-B1-A1-A OK    ||
|  | 17/01 14:00  | A. Bernard  | Deconnexion  | Session exp.     ||
|  | 17/01 13:45  | A. Bernard  | Confirmation | W3-B2-A1-B OK    ||
|  +---------------------------------------------------------------+|
|  | [< Precedent]    Page 1/15    [Suivant >]                    ||
|  +---------------------------------------------------------------+|
|                                                                   |
|  [Exporter CSV]  [Exporter PDF]                                  |
+------------------------------------------------------------------+
```

**Elements:**
- Navigation par onglets (accessible aux superviseurs/admins)
- Filtres: Periode, utilisateur, type d'operation
- Tableau avec colonnes triables
- Pagination
- Export (CSV, PDF)

---

### 3.8 Page Generation Rapports

```
+------------------------------------------------------------------+
| [LOGO] VICORE  [Status: Online]  [14:32:45] [FR|EN] [SUP] [Logout]|
+------------------------------------------------------------------+
| [Train Passes] [Audit Trail] [Rapports]                          |
+------------------------------------------------------------------+
|                                                                   |
|  GENERATION DE RAPPORTS                                          |
|                                                                   |
|  +--------------------------------+  +-------------------------+ |
|  | PARAMETRES                     |  | APERCU                  | |
|  +--------------------------------+  +-------------------------+ |
|  |                                |  |                         | |
|  | Date debut: [01/01/2026]      |  | Rapport du 01/01/2026   | |
|  |                                |  | au 17/01/2026           | |
|  | Date fin:   [17/01/2026]      |  |                         | |
|  |                                |  | STATISTIQUES            | |
|  | Type de rapport:              |  | - Connexions: 245       | |
|  | (*) Synthese                  |  | - Confirmations: 89     | |
|  | ( ) Detail                    |  | - Annulations: 3        | |
|  |                                |  |                         | |
|  | Filtres optionnels:           |  | ACTIVITE PAR JOUR       | |
|  | Utilisateur: [Tous v]         |  | [=========] Graphique   | |
|  | Type: [Tous v]                |  |                         | |
|  |                                |  | TOP UTILISATEURS        | |
|  | [Generer rapport]             |  | 1. J. Dupont: 45 ops    | |
|  |                                |  | 2. M. Martin: 32 ops    | |
|  +--------------------------------+  | 3. A. Bernard: 28 ops   | |
|                                      +-------------------------+ |
|                                                                   |
|  MES RAPPORTS RECENTS                                            |
|  +---------------------------------------------------------------+|
|  | Date       | Periode          | Type     | Actions           ||
|  +---------------------------------------------------------------+|
|  | 15/01/2026 | 01/01 - 15/01   | Synthese | [PDF] [CSV] [XLS] ||
|  | 01/01/2026 | 01/12 - 31/12   | Detail   | [PDF] [CSV] [XLS] ||
|  +---------------------------------------------------------------+|
+------------------------------------------------------------------+
```

**Elements:**
- Formulaire de parametres (dates, type, filtres)
- Apercu en temps reel des statistiques
- Liste des rapports generes precedemment
- Actions d'export multiples formats

---

## 4. Regles de Gestion

### 4.1 Regles d'Authentification

| ID | Regle | Description |
|----|-------|-------------|
| RG-AUTH-01 | SSO Eurotunnel | Authentification deleguee au portail SSO Eurotunnel |
| RG-AUTH-02 | Token SSO | Validation du token SSO a chaque requete sensible |
| RG-AUTH-03 | Session | Expiration apres 8h d'inactivite |
| RG-AUTH-04 | Mapping roles | Groupes SSO Eurotunnel mappes vers roles VICORE (operateur, superviseur, admin) |
| RG-AUTH-05 | Autorisation | Liste des utilisateurs SSO autorises a acceder a VICORE |

### 4.2 Regles de Statut (Conf_code)

| Conf_code | Signification | Couleur | Action Requise |
|-----------|---------------|---------|----------------|
| 0 | Confirme OK (humain) | Violet | Aucune |
| 1 | OK (automatique) | Vert | Aucune |
| 2 | Incertain | Jaune | Verification recommandee |
| 3 | Anomalie detectee | Rouge | Confirmation obligatoire |

### 4.3 Regles de Confirmation

| ID | Regle | Description |
|----|-------|-------------|
| RG-CONF-01 | Unicite | Un ressort ne peut etre confirme qu'une fois (hors annulation) |
| RG-CONF-02 | Annulation | Confirmation "Manquant" annulable dans les 24h suivant le passage |
| RG-CONF-03 | Tracabilite | Enregistrement utilisateur + date + action + motif (si annulation) |
| RG-CONF-04 | Impact | Confirmation "Present" met conf_code a 0 |
| RG-CONF-05 | Motif obligatoire | Annulation requiert un motif textuel (min 10 caracteres) |
| RG-CONF-06 | Notification | Toute annulation genere une notification au superviseur |
| RG-CONF-07 | Reinitialisation | Annulation remet le ressort au statut original (conf_code 3) |

### 4.4 Regles de Heartbeat

| ID | Regle | Description |
|----|-------|-------------|
| RG-HB-01 | Frequence | Heartbeat attendu toutes les 30 secondes |
| RG-HB-02 | Alerte | Si heartbeat > 60s, statut = Erreur |
| RG-HB-03 | Affichage | Afficher date/heure du dernier heartbeat |

### 4.5 Regles d'Internationalisation

| ID | Regle | Description |
|----|-------|-------------|
| RG-I18N-01 | Langues | Interface disponible en Francais (FR) et Anglais (EN) |
| RG-I18N-02 | Detection | Langue initiale detectee depuis le navigateur |
| RG-I18N-03 | Selection | Selecteur de langue [FR\|EN] dans l'en-tete |
| RG-I18N-04 | Persistance | Preference de langue sauvegardee par utilisateur |
| RG-I18N-05 | Dates FR | Format: JJ/MM/AAAA HH:MM:SS |
| RG-I18N-06 | Dates EN | Format: MM/DD/YYYY HH:MM:SS AM/PM |
| RG-I18N-07 | Application | Changement de langue applique immediatement sans rechargement |

**Textes a traduire:**
- Labels de navigation et boutons
- Messages de confirmation et d'erreur
- Tooltips et textes d'aide
- Notifications et alertes
- Titres de pages et sections

### 4.6 Regles d'Historique Ressort

| ID | Regle | Description |
|----|-------|-------------|
| RG-HIST-01 | Identification | Ressort identifie par: wagon_id + bogie + essieu + cote (G/D) + position (Menant/Mene) |
| RG-HIST-02 | Periode | Historique disponible sur minimum 30 jours glissants |
| RG-HIST-03 | Limite | Maximum 50 passages affiches dans l'historique |
| RG-HIST-04 | Comparaison | Maximum 4 images selectionnables pour comparaison |
| RG-HIST-05 | Tri | Affichage chronologique decroissant (plus recent en premier) |

### 4.9 Regles de Nomenclature Ressorts

| ID | Regle | Description |
|----|-------|-------------|
| RG-SPRING-01 | Structure wagon | Chaque wagon possede 2 bogies, 2 essieux par bogie, 2 roues par essieu, 2 ressorts par roue = 16 ressorts |
| RG-SPRING-02 | Position Menant | Ressort Menant (Leading): situe avant la roue dans le sens de marche normal |
| RG-SPRING-03 | Position Mene | Ressort Mene (Trailing): situe apres la roue dans le sens de marche normal |
| RG-SPRING-04 | Direction impact | En mode "Tiroir", les positions Menant/Mene sont inversees visuellement |
| RG-SPRING-05 | Format ID | Format: W{wagon}-B{bogie}-E{essieu}-{G\|D}-{M\|m} (ex: W2-B1-E2-G-M) |

### 4.10 Regles Types de Wagon

| ID | Regle | Description |
|----|-------|-------------|
| RG-TYPE-01 | Locomotive | Wagon moteur (Loco) - en tete ou queue de rame |
| RG-TYPE-02 | Chargeur | Wagon chargeur - pour le chargement/dechargement des vehicules |
| RG-TYPE-03 | Porteur | Wagon porteur - wagon standard de transport |
| RG-TYPE-04 | Affichage | Le type est affiche sur chaque carte wagon sous le RFID |

### 4.11 Regles Direction Train

| ID | Regle | Description |
|----|-------|-------------|
| RG-DIR-01 | Normal | Direction normale: sens de marche standard du train |
| RG-DIR-02 | Tiroir | Direction tiroir: sens de marche inverse (le train pousse au lieu de tirer) |
| RG-DIR-03 | Affichage | La direction est affichee dans les metadonnees du train |
| RG-DIR-04 | Impact | La direction influence l'interpretation visuelle des ressorts Menant/Mene |

### 4.7 Regles d'Audit Trail

| ID | Regle | Description |
|----|-------|-------------|
| RG-AUD-01 | Acces | Historique operations accessible uniquement aux superviseurs et admins |
| RG-AUD-02 | Retention | Conservation des logs d'audit pendant 1 an minimum |
| RG-AUD-03 | Immuabilite | Les enregistrements d'audit ne peuvent pas etre modifies ou supprimes |
| RG-AUD-04 | Horodatage | Chaque operation enregistree avec timestamp UTC |
| RG-AUD-05 | Contenu | Enregistrement: utilisateur, action, cible, IP, user-agent |

**Types d'operations tracees:**
- Connexions et deconnexions
- Confirmations de ressorts
- Annulations de confirmations
- Consultations de rapports
- Exports de donnees

### 4.8 Regles de Generation Rapports

| ID | Regle | Description |
|----|-------|-------------|
| RG-RPT-01 | Acces | Rapports accessibles uniquement aux superviseurs et admins |
| RG-RPT-02 | Periode max | Periode de rapport limitee a 90 jours maximum |
| RG-RPT-03 | Generation async | Rapports > 30 jours generes de maniere asynchrone |
| RG-RPT-04 | Notification | Email de notification a la fin de generation asynchrone |
| RG-RPT-05 | Formats | Formats disponibles: PDF, CSV, Excel (XLSX) |
| RG-RPT-06 | Historique | Conservation des rapports generes pendant 90 jours |

---

## 5. Workflows

### 5.1 Workflow Principal d'Inspection

```
+-------------+     +----------------+     +---------------+
|   Login     | --> | System View    | --> | Selectionner  |
|             |     | (Train Passes) |     | Train Pass    |
+-------------+     +----------------+     +---------------+
                                                   |
                                                   v
                    +----------------+     +---------------+
                    | Cliquer sur    | <-- | Voir Grille   |
                    | Wagon          |     | Wagons        |
                    +----------------+     +---------------+
                           |
                           v
                    +----------------+
                    | Car View       |
                    | (Inspection)   |
                    +----------------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    +-----------+    +-----------+    +-----------+
    | Analyser  |    | Naviguer  |    | Confirmer |
    | Image     |    | Prev/Next |    | Statut    |
    +-----------+    +-----------+    +-----------+
          |                |                |
          +----------------+----------------+
                           |
                           v
                    +----------------+
                    | Retour System  |
                    | View ou Wagon  |
                    | Suivant        |
                    +----------------+
```

### 5.2 Workflow de Confirmation

```
                    +--------------------+
                    | Ressort en         |
                    | anomalie detecte   |
                    | (conf_code > 2)    |
                    +--------------------+
                            |
                            v
                    +--------------------+
                    | Bouton "Confirm"   |
                    | affiche            |
                    +--------------------+
                            |
                            v
                    +--------------------+
                    | Clic sur bouton    |
                    +--------------------+
                            |
                            v
                    +--------------------+
                    | Modale avec        |
                    | toutes les images  |
                    +--------------------+
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
    +------------+   +------------+   +------------+
    |  Present   |   |  Absent    |   |  Incertain |
    +------------+   +------------+   +------------+
            |               |               |
            v               v               v
    +------------+   +------------+   +------------+
    | conf_code  |   | Enregistre |   | Fermer     |
    | = 0        |   | absent     |   | modale     |
    +------------+   +------------+   +------------+
            |               |
            +-------+-------+
                    |
                    v
            +---------------+
            | Mise a jour   |
            | indicateurs   |
            +---------------+
```

---

## 6. Interfaces

### 6.1 Interface avec Base de Donnees

| Table | Operations | Description |
|-------|------------|-------------|
| users | R | Authentification |
| train_pass | R | Liste passages |
| car | R | Details wagons |
| spring | R, U | Details/Update ressorts |
| installation | R | Sites (Folkestone/Coquelles) |

### 6.2 Interface avec Redis

| Cle | Type | Description |
|-----|------|-------------|
| heartbeat:{system_id} | Hash | Dernier heartbeat |
| displayname:{train_pass_id} | String | Nom affichage cache |

### 6.3 Interface avec Systeme de Fichiers

| Chemin | Acces | Description |
|--------|-------|-------------|
| /static/train/ | Lecture | Icones wagons |
| /images/{path} | Lecture | Images ressorts |

---

## Annexes

### A. Codes Couleur Theme Dark Tech

| Variable | Valeur | Usage |
|----------|--------|-------|
| --bg-primary | #0a0a0f | Fond principal |
| --neon-cyan | #00d4ff | Accent primaire |
| --status-ok | #10b981 | Statut OK |
| --status-warn | #f59e0b | Statut Warning |
| --status-error | #ef4444 | Statut Erreur |

### B. Raccourcis Clavier (Future)

| Touche | Action |
|--------|--------|
| Fleche Gauche | Ressort precedent |
| Fleche Droite | Ressort suivant |
| Echap | Fermer modale |
| Enter | Valider |

---

*Document genere le 2026-01-18*
