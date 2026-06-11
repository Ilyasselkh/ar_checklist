from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ArChecklistEquipment(models.Model):
    _name = "ar.checklist.equipment"
    _description = "Équipement Check-list"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Nom d'équipement", required=True, tracking=True)
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
        if self.env["ar.checklist.equipment.line"].search_count([("equipment_id", "in", self.ids)]):
            raise ValidationError(_("Vous ne pouvez pas supprimer un équipement déjà utilisé dans une check-list. Archivez-le à la place."))
        return super().unlink()

    def _create_missing_checklist_lines(self):
        active_equipment = self.filtered("active")
        if not active_equipment:
            return
        checklists = self.env["ar.checklist"].search([("active", "=", True)])
        for checklist in checklists:
            existing_equipment = checklist.equipment_line_ids.mapped("equipment_id")
            missing_equipment = active_equipment - existing_equipment
            for equipment in missing_equipment:
                self.env["ar.checklist.equipment.line"].create({
                    "checklist_id": checklist.id,
                    "equipment_id": equipment.id,
                })
