# AR - Check-list

Module Odoo de gestion des check-lists de passation de changement d'equipe.

Le module permet de preparer une check-list par dossier, de verifier les equipements, zones et operateurs, de collecter les signatures des equipes, de traiter les desaccords et d'archiver les passations terminees.

## Objectif fonctionnel

Centraliser les passations entre equipes et tracer l'etat reel du terrain au moment du changement.

Le module permet de :

- creer une check-list de passation ;
- rattacher la check-list a une equipe, un dossier ou un contexte operationnel ;
- controler les equipements et zones avec les statuts `OK`, `NOK` ou `ABS` ;
- affecter les operateurs depuis les donnees RH ;
- collecter les signatures de l'equipe sortante et de l'equipe entrante ;
- signaler un desaccord avec motif ;
- faire arbitrer le superviseur ;
- archiver les check-lists terminees ;
- imprimer un rapport de passation.

## Roles fonctionnels

### Operateur / equipe

Les utilisateurs terrain renseignent les controles et signent la passation.

Ils peuvent :

- consulter la check-list ;
- renseigner les lignes d'equipements et de zones ;
- indiquer les absences ou anomalies ;
- signer la passation ;
- signaler un desaccord si la passation n'est pas acceptee.

### Superviseur

Le superviseur intervient lorsque la passation necessite une decision.

Il peut :

- consulter les motifs de desaccord ;
- accepter ou refuser la passation ;
- renseigner un motif de decision ;
- faire avancer le dossier vers son etat final.

### Administrateur

L'administrateur gere les donnees de reference.

Il peut :

- parametrer les equipements ;
- parametrer les zones ;
- maintenir la documentation ;
- verifier les droits et groupes de securite.

## Etats principaux

Les etats de workflow couvrent la creation, les signatures, les desaccords, la decision superviseur et l'archivage.

Les statuts des lignes terrain sont :

- `OK` : controle conforme ;
- `NOK` : anomalie ou non-conformite ;
- `ABS` : element absent ou non applicable.

## Fonctionnement operationnel

1. Creer une check-list.
2. Renseigner l'equipe et le contexte de passation.
3. Completer les lignes d'equipements, zones et operateurs.
4. Sauvegarder la check-list.
5. Faire signer l'equipe sortante.
6. Faire signer l'equipe entrante.
7. En cas de desaccord, ouvrir l'assistant et saisir le motif.
8. Faire trancher le superviseur.
9. Archiver la check-list finalisee.

## Gestion des equipements et zones

Les equipements et zones sont geres comme referentiels du module.

Chaque ligne de controle peut recevoir :

- un statut ;
- un commentaire ;
- des informations de suivi visibles dans le rapport.

Le module fournit aussi des composants backend pour faciliter la saisie visuelle des cartes equipement.

## Assistants

Le module contient deux assistants principaux :

- assistant de desaccord ;
- assistant de decision superviseur.

Ils servent a encadrer les changements d'etat sensibles et a obliger la saisie des motifs utiles au suivi.

## Rapports

Le module fournit un rapport de check-list permettant d'imprimer ou d'exporter la passation.

Fichier principal :

- `reports/checklist_report.xml`

## Modeles principaux

- `ar.checklist`
- `ar.checklist.line`
- `ar.checklist.equipment`
- `ar.checklist.equipment.line`
- `ar.checklist.zone`
- `ar.checklist.zone.line`
- `ar.checklist.operator.line`
- `ar.checklist.documentation`
- `ar.checklist.disagreement.wizard`
- `ar.checklist.supervisor.decision.wizard`

## Securite et droits

Les droits sont definis dans :

- `security/security.xml`
- `security/ir.model.access.csv`

Points a verifier apres installation :

- les groupes utilisateurs ;
- l'acces aux check-lists ;
- l'acces aux referentiels equipements et zones ;
- l'acces aux assistants ;
- la coherence avec les employes du module RH.

## Structure du module

- `data/sequence.xml`
- `security/security.xml`
- `security/ir.model.access.csv`
- `reports/checklist_report.xml`
- `views/checklist_views.xml`
- `views/equipment_views.xml`
- `views/zone_views.xml`
- `views/documentation_views.xml`
- `views/menus.xml`
- `wizard/disagreement_wizard.py`
- `wizard/supervisor_decision_wizard.py`
- `models/checklist.py`
- `models/equipment.py`
- `models/zone.py`
- `models/documentation.py`
- `models/hr_employee.py`
- `models/kadouane_dossier.py`
- `static/src/js/equipment_cards_field.js`
- `static/src/xml/equipment_cards_field.xml`
- `static/src/scss/ar_checklist.scss`

## Installation

1. Copier le module dans le dossier addons Odoo.
2. Redemarrer le serveur Odoo si necessaire.
3. Mettre a jour la liste des applications.
4. Installer le module `AR - Check-list`.
5. Verifier les groupes et droits utilisateurs.
6. Creer quelques equipements et zones de test.
7. Tester une passation complete avec signatures et archivage.

## Maintenance fonctionnelle

Lorsqu'une regle de passation change, verifier aussi :

- les etats du modele `ar.checklist` ;
- les boutons de la vue formulaire ;
- les assistants de desaccord et de decision superviseur ;
- le rapport de check-list ;
- les droits de securite ;
- ce README.
