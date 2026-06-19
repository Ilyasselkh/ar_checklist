from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ArChecklistZone(models.Model):
    _name = "ar.checklist.zone"
    _description = "Zone Check-list"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Nom de zone", required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._create_missing_checklist_lines()
        return records

    def write(self, vals):
        result = super().write(vals)
        if vals.get("active") is not False:
            self._create_missing_checklist_lines()
        return result

    def unlink(self):
        if self.env["ar.checklist.zone.line"].search_count([("zone_id", "in", self.ids)]):
            raise ValidationError(_("Vous ne pouvez pas supprimer une zone déjà utilisée dans une check-list. Archivez-la à la place."))
        return super().unlink()

    def _create_missing_checklist_lines(self):
        active_zones = self.filtered("active")
        if not active_zones:
            return
        checklists = self.env["ar.checklist"].search([
            ("active", "=", True),
            ("workflow_state", "=", "signature_1"),
        ])
        for checklist in checklists:
            existing_zones = checklist.zone_line_ids.mapped("zone_id")
            missing_zones = active_zones - existing_zones
            for zone in missing_zones:
                self.env["ar.checklist.zone.line"].create({
                    "checklist_id": checklist.id,
                    "zone_id": zone.id,
                })
