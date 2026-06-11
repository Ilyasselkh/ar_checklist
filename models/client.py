import base64
from io import BytesIO

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ArChecklistClient(models.Model):
    _name = "ar.checklist.client"
    _description = "Check-list de passation - Clients"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Description", required=True, default="Import clients", tracking=True)
    excel_file = fields.Binary(string="Fichier Excel", attachment=True, tracking=True)
    excel_filename = fields.Char(string="Nom du fichier", tracking=True)
    line_ids = fields.One2many("ar.checklist.client.line", "import_id", string="Tableau clients")

    def action_convert_excel(self):
        for rec in self:
            if not rec.excel_file:
                raise ValidationError(_("Veuillez attacher un fichier Excel."))
            try:
                import openpyxl
            except ImportError as exc:
                raise ValidationError(_("La librairie Python openpyxl est requise pour lire le fichier Excel.")) from exc

            rec.line_ids.unlink()
            try:
                workbook = openpyxl.load_workbook(BytesIO(base64.b64decode(rec.excel_file)), data_only=True)
                sheet = workbook.active
            except Exception as exc:
                raise ValidationError(_("Erreur de lecture du fichier Excel: %s") % exc) from exc

            rows = []
            for excel_row in sheet.iter_rows(min_row=2, values_only=True):
                client_name = next((self._clean_value(value) for value in excel_row if self._clean_value(value)), "")
                if not client_name:
                    continue
                rows.append(
                    (
                        0,
                        0,
                        {
                            "name": client_name,
                        },
                    )
                )
            if not rows:
                raise ValidationError(_("Aucune ligne exploitable n'a ete trouvee dans le fichier Excel."))
            rec.write({"line_ids": rows})

    @staticmethod
    def _clean_value(value):
        if value is None:
            return ""
        return str(value).strip()


class ArChecklistClientLine(models.Model):
    _name = "ar.checklist.client.line"
    _description = "Ligne client importee"
    _rec_name = "name"
    _order = "import_id desc, id"

    import_id = fields.Many2one("ar.checklist.client", string="Import", required=True, ondelete="cascade")
    name = fields.Char(string="Nom du client", required=True)
