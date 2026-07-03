from odoo import api, fields, models, tools
from odoo.osv import expression


class ArChecklistKadouaneDossier(models.Model):
    _name = "ar.checklist.kadouane.dossier"
    _description = "Dossier Kadouane Import/Export"
    _auto = False
    _rec_name = "referenceID"
    _order = "create_date desc, id desc"

    referenceID = fields.Char(string="N° dossier", readonly=True)
    name = fields.Char(string="Nom", readonly=True)
    client_name = fields.Char(string="Client", readonly=True)
    supplier_name = fields.Char(string="Fournisseur", readonly=True)
    partner_name = fields.Char(string="Client / Fournisseur", readonly=True)
    source_model = fields.Selection(
        [
            ("kadouane.kadouane", "Export"),
            ("kadouane.dmdimport", "Import"),
        ],
        string="Type",
        readonly=True,
    )
    res_id = fields.Integer(string="ID source", readonly=True)
    state = fields.Char(string="État", readonly=True)
    create_date = fields.Datetime(string="Date de création", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    (export_dossier.id * 2) AS id,
                    export_dossier."referenceID" AS "referenceID",
                    export_dossier."referenceID" AS name,
                    export_client.name AS client_name,
                    NULL::varchar AS supplier_name,
                    export_client.name AS partner_name,
                    'kadouane.kadouane' AS source_model,
                    export_dossier.id AS res_id,
                    export_dossier.state AS state,
                    export_dossier.create_date AS create_date
                FROM kadouane_kadouane export_dossier
                LEFT JOIN kadouane_client export_client ON export_client.id = export_dossier.client_id
                WHERE COALESCE(export_dossier."referenceID", '') NOT IN ('', 'Nouvelle demande')

                UNION ALL

                SELECT
                    (import_dossier.id * 2 + 1) AS id,
                    import_dossier."referenceID" AS "referenceID",
                    import_dossier."referenceID" AS name,
                    NULL::varchar AS client_name,
                    import_supplier.name AS supplier_name,
                    import_supplier.name AS partner_name,
                    'kadouane.dmdimport' AS source_model,
                    import_dossier.id AS res_id,
                    import_dossier.state AS state,
                    import_dossier.create_date AS create_date
                FROM kadouane_dmdimport import_dossier
                LEFT JOIN kadouane_supplier import_supplier ON import_supplier.id = import_dossier.supplier_id
                WHERE COALESCE(import_dossier."referenceID", '') NOT IN ('', 'Nouvelle demande')
            )
        """ % self._table)
        self.env.cr.execute("""
            SELECT 1
              FROM information_schema.columns
             WHERE table_name = 'ar_checklist_line'
               AND column_name = 'dechargement_dossier_id'
        """)
        if self.env.cr.fetchone():
            self.env.cr.execute("""
                UPDATE ar_checklist_line
                   SET dechargement_dossier_id = dossier_id * 2
                 WHERE section = 'dechargement'
                   AND dossier_id IS NOT NULL
                   AND dechargement_dossier_id IS NULL
            """)

    @api.depends("referenceID", "partner_name", "source_model")
    def _compute_display_name(self):
        for record in self:
            label = record.referenceID or str(record.res_id or record.id)
            if record.partner_name:
                label = f"{label} - {record.partner_name}"
            if record.source_model == "kadouane.dmdimport":
                label = f"{label} (Import)"
            elif record.source_model == "kadouane.kadouane":
                label = f"{label} (Export)"
            record.display_name = label

    @api.model
    def _name_search(self, name="", domain=None, operator="ilike", limit=None, order=None):
        if not name:
            return super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
        search_domain = expression.OR([
            [("referenceID", operator, name)],
            [("name", operator, name)],
            [("client_name", operator, name)],
            [("supplier_name", operator, name)],
            [("partner_name", operator, name)],
        ])
        return self._search(expression.AND([domain or [], search_domain]), limit=limit, order=order)
