{
    "name": "AR - Check-list",
    "version": "1.0.0",
    "summary": "Check-list de passation",
    "description": """
Module de gestion des check-lists de passation de changement d'équipe avec archives, documentation
et opérateurs affectés depuis le module RH.
    """,
    "author": "AR IT Department",
    "category": "Operations",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "kadouane",
    ],
    "data": [
        "data/sequence.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "reports/checklist_report.xml",
        "wizard/disagreement_wizard_views.xml",
        "wizard/supervisor_decision_wizard_views.xml",
        "views/checklist_views.xml",
        "views/equipment_views.xml",
        "views/zone_views.xml",
        "views/documentation_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ar_checklist/static/src/js/equipment_cards_field.js",
            "ar_checklist/static/src/xml/equipment_cards_field.xml",
            "ar_checklist/static/src/scss/ar_checklist.scss",
        ],
    },
    "application": True,
    "installable": True,
}

