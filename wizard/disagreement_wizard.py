from odoo import fields, models


class ArChecklistDisagreementWizard(models.TransientModel):
    _name = "ar.checklist.disagreement.wizard"
    _description = "Confirmation Non d'accord Check-list"

    checklist_id = fields.Many2one("ar.checklist", string="Check-list", required=True, readonly=True)
    motif = fields.Text(string="Motifs", required=True)

    def action_confirm(self):
        self.ensure_one()
        self.checklist_id.action_confirm_disagreement(self.motif)
        return {"type": "ir.actions.act_window_close"}
