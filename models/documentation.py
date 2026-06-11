from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ArChecklistDocumentation(models.Model):
    _name = "ar.checklist.documentation"
    _description = "Check-list de passation - Documentation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    description = fields.Char(string="Description", required=True, tracking=True)
    file_data = fields.Binary(string="Fichier", attachment=True, tracking=True)
    file_name = fields.Char(string="Nom du fichier", tracking=True)
    link_url = fields.Char(string="Lien", tracking=True)
    created_by = fields.Many2one("res.users", string="Realise par", related="create_uid", store=True, readonly=True)
    created_on = fields.Datetime(string="Date", related="create_date", store=True, readonly=True)

    @api.constrains("file_data", "link_url")
    def _check_file_or_link(self):
        for rec in self:
            if not rec.file_data and not rec.link_url:
                raise ValidationError(_("Vous devez renseigner soit un fichier, soit un lien."))
