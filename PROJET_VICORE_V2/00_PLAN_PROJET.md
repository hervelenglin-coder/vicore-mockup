# VICORE V2 - Plan Projet Cycle en V

## Informations Projet

| Champ | Valeur |
|-------|--------|
| **Nom du Projet** | VICORE V2 - VIsualisation COntrole REssorts |
| **Version** | 2.0.0 |
| **Date de Creation** | 2026-01-18 |
| **Chef de Projet** | A definir |
| **Client** | Eurotunnel |

---

## 1. Presentation du Cycle en V

```
                        VALIDATION
                            |
    Specifications    +-----------+    Recette
    des Exigences     |           |    Utilisateur
         |            |     V     |         |
         v            |           |         ^
    Specifications    |           |    Tests
    Fonctionnelles    |           |    Fonctionnels
         |            |           |         |
         v            |           |         ^
    Specifications    |           |    Tests
    Techniques        |           |    Integration
         |            |           |         |
         v            |           |         ^
    Conception        |           |    Tests
    Detaillee         |           |    Unitaires
         |            |           |         |
         v            +-----------+         ^
                           |
                      CODAGE/DEV
```

---

## 2. Structure des Livrables

```
PROJET_VICORE_V2/
|
+-- 00_PLAN_PROJET.md                    # Ce document
|
+-- 01_SPECIFICATIONS/
|   +-- 01_SRS_Specification_Exigences.md
|   +-- 02_SFG_Specification_Fonctionnelle.md
|   +-- 03_STB_Specification_Technique.md
|   +-- 04_DAT_Dossier_Architecture.md
|   +-- 05_DCD_Dossier_Conception_Detaillee.md
|
+-- 02_DEVELOPPEMENT/
|   +-- vicore-v2/                       # Code source
|   +-- NORMES_CODAGE.md
|   +-- GUIDE_CONTRIBUTION.md
|
+-- 03_TESTS/
|   +-- 01_PTU_Plan_Tests_Unitaires.md
|   +-- 02_PTI_Plan_Tests_Integration.md
|   +-- 03_PTF_Plan_Tests_Fonctionnels.md
|   +-- 04_PRA_Plan_Recette.md
|   +-- Rapports/
|
+-- 04_EXPLOITATION/
|   +-- MAN_Manuel_Utilisateur.md
|   +-- MEX_Manuel_Exploitation.md
|   +-- MIG_Guide_Migration.md
|
+-- 05_QUALITE/
|   +-- PAQ_Plan_Assurance_Qualite.md
|   +-- RAN_Rapport_Analyse.md
```

---

## 3. Phases du Projet

### Phase 1: Specifications des Exigences (SRS)
**Duree estimee:** 1-2 semaines

| Activite | Livrable | Responsable |
|----------|----------|-------------|
| Analyse du besoin metier | SRS Section 1-2 | MOA + MOE |
| Identification des acteurs | SRS Section 3 | MOA |
| Definition des exigences fonctionnelles | SRS Section 4 | MOA + MOE |
| Definition des exigences non-fonctionnelles | SRS Section 5 | MOE |
| Analyse des contraintes | SRS Section 6 | MOE |
| Validation des exigences | SRS Signe | MOA |

**Criteres de sortie:**
- [ ] Document SRS valide et signe
- [ ] Matrice de tracabilite initialisee
- [ ] Exigences numerotees et priorisees

---

### Phase 2: Specifications Fonctionnelles (SFG)
**Duree estimee:** 2-3 semaines

| Activite | Livrable | Responsable |
|----------|----------|-------------|
| Modelisation des cas d'utilisation | Diagrammes UML | Analyste |
| Definition des ecrans et IHM | Maquettes/Wireframes | UX Designer |
| Description des workflows | Diagrammes d'activite | Analyste |
| Regles de gestion | SFG Section 4 | Analyste |
| Specification des interfaces | SFG Section 5 | Analyste |
| Validation fonctionnelle | SFG Signe | MOA |

**Criteres de sortie:**
- [ ] Document SFG valide et signe
- [ ] Maquettes IHM validees
- [ ] Cas d'utilisation complets

---

### Phase 3: Specifications Techniques (STB)
**Duree estimee:** 2-3 semaines

| Activite | Livrable | Responsable |
|----------|----------|-------------|
| Choix d'architecture | DAT | Architecte |
| Selection des technologies | STB Section 2 | Architecte |
| Modele de donnees | MCD/MLD | Architecte |
| Specification des APIs | OpenAPI/Swagger | Dev Lead |
| Securite et performances | STB Section 5-6 | Architecte |
| Validation technique | STB Signe | Directeur Technique |

**Criteres de sortie:**
- [ ] Document STB valide
- [ ] Architecture validee
- [ ] Stack technique approuvee

---

### Phase 4: Conception Detaillee (DCD)
**Duree estimee:** 2 semaines

| Activite | Livrable | Responsable |
|----------|----------|-------------|
| Design des composants | Diagrammes de classes | Dev Lead |
| Specification des modules | DCD Sections | Developpeurs |
| Design de la base de donnees | Scripts DDL | DBA |
| Design des APIs detaille | Schemas JSON | Dev Lead |
| Revue de conception | CR Revue | Equipe |

**Criteres de sortie:**
- [ ] DCD complet
- [ ] Diagrammes UML a jour
- [ ] Revue de conception OK

---

### Phase 5: Developpement
**Duree estimee:** 6-8 semaines

| Sprint | Fonctionnalites | Objectif |
|--------|-----------------|----------|
| Sprint 1 | Setup + SSO | Infrastructure + Integration SSO Eurotunnel |
| Sprint 2 | Train Passes | Liste + Details |
| Sprint 3 | Car View | Visualisation wagons |
| Sprint 4 | Spring Analysis | Inspection ressorts |
| Sprint 5 | Status & Alerts | Monitoring temps reel |
| Sprint 6 | Polish + Fixes | Stabilisation |

**Criteres de sortie:**
- [ ] Code complet et documente
- [ ] Tests unitaires > 80% couverture
- [ ] Code review OK

---

### Phase 6: Tests Unitaires (TU)
**Duree estimee:** En continu (pendant dev)

| Type | Couverture Cible | Outils |
|------|------------------|--------|
| Backend Python | > 80% | pytest, coverage |
| Frontend JS/Vue | > 70% | Jest, Vue Test Utils |
| API | 100% endpoints | pytest + requests |

**Criteres de sortie:**
- [ ] Couverture atteinte
- [ ] 0 test en echec
- [ ] Rapport de couverture

---

### Phase 7: Tests d'Integration (TI)
**Duree estimee:** 1-2 semaines

| Domaine | Description |
|---------|-------------|
| API Integration | Communication front/back |
| Database | Operations CRUD |
| Redis Cache | Mise en cache |
| SSO Eurotunnel | Flow authentification complet |
| External Systems | Heartbeat, cameras |

**Criteres de sortie:**
- [ ] Tous les flux integres testes
- [ ] Rapport TI OK
- [ ] Anomalies corrigees

---

### Phase 8: Tests Fonctionnels (TF)
**Duree estimee:** 1-2 semaines

| Scenario | Priorite |
|----------|----------|
| Connexion utilisateur | P1 |
| Navigation train passes | P1 |
| Visualisation wagons | P1 |
| Analyse des ressorts | P1 |
| Confirmation statut | P2 |
| Gestion des alertes | P2 |

**Criteres de sortie:**
- [ ] 100% cas P1 OK
- [ ] > 90% cas P2 OK
- [ ] PV de recette interne

---

### Phase 9: Recette Utilisateur (UAT)
**Duree estimee:** 1-2 semaines

| Activite | Participants |
|----------|--------------|
| Formation utilisateurs | MOE + MOA |
| Execution scenarios | Utilisateurs finaux |
| Collecte retours | MOE |
| Corrections mineures | Dev |
| Validation finale | MOA |

**Criteres de sortie:**
- [ ] PV de recette signe
- [ ] Go pour MEP

---

### Phase 10: Mise en Production
**Duree estimee:** 1 semaine

| Etape | Responsable |
|-------|-------------|
| Preparation environnement | Ops |
| Migration donnees | DBA |
| Deploiement application | DevOps |
| Tests de verification | QA |
| Bascule production | Ops |
| Hypercare | Equipe complete |

---

## 4. Planning Previsionnel

```
Semaine:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
          |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
SRS       [===]
SFG           [=======]
STB                   [=======]
DCD                           [===]
DEV                               [=======================]
TU                                [=======================]
TI                                                        [===]
TF                                                            [===]
UAT                                                               [===]
MEP                                                                   [=]
```

---

## 5. Equipe Projet

| Role | Responsabilites |
|------|-----------------|
| **Chef de Projet** | Coordination, planning, reporting |
| **Architecte** | Architecture technique, choix techno |
| **Dev Lead** | Supervision dev, code review |
| **Developpeurs (x2)** | Implementation |
| **QA Engineer** | Tests, qualite |
| **UX Designer** | Maquettes, experience utilisateur |
| **DBA** | Base de donnees |
| **Ops/DevOps** | Infrastructure, deploiement |

---

## 6. Gestion des Risques

| Risque | Impact | Probabilite | Mitigation |
|--------|--------|-------------|------------|
| Retard specifications | Eleve | Moyenne | Buffer planning |
| Complexite technique | Moyen | Moyenne | POC prealables |
| Indisponibilite ressources | Eleve | Faible | Backup identifies |
| Changement exigences | Eleve | Moyenne | Gestion du changement |
| Performance insuffisante | Moyen | Faible | Tests de charge |

---

## 7. Outils et Methodes

| Categorie | Outil |
|-----------|-------|
| Gestion de projet | Jira / Azure DevOps |
| Versionning | Git (GitHub/GitLab) |
| Documentation | Markdown + Confluence |
| CI/CD | GitHub Actions / GitLab CI |
| Tests | pytest, Jest, Cypress |
| Monitoring | Prometheus + Grafana |

---

## 8. Prochaines Etapes

1. **Validation du plan projet** par les parties prenantes
2. **Constitution de l'equipe** projet
3. **Lancement Phase 1** - Specifications des Exigences
4. **Kick-off meeting** avec l'ensemble des acteurs

---

## Annexes

- A. Glossaire
- B. Acronymes
- C. References documentaires
- D. Historique des modifications

---

*Document genere le 2026-01-18*
*Version: 1.0*
