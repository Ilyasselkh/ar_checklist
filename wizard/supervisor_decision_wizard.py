from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ArChecklistSupervisorDecisionWizard(models.TransientModel):
    _name = "ar.checklist.supervisor.decision.wizard"
    _description = "Décision superviseur Check-list"

    checklist_id = fields.Many2one("ar.checklist", string="Check-list", required=True, readonly=True)
    decision = fields.Selection(
        [
            ("validated", "Valider"),
            ("refused", "Refuser"),
        ],
        string="Décision",
        required=True,
        readonly=True,
    )
    disagreement_motif = fields.Text(string="Motif de refus Opérateur", compute="_compute_disagreement_motif")
    motif = fields.Text(string="Motif de refus Superviseur")

    @api.depends("checklist_id.disagreement_motif")
    def _compute_disagreement_motif(self):
        for wizard in self:
            wizard.disagreement_motif = wizard.checklist_id.disagreement_motif or ""

    def action_confirm(self):
        self.ensure_one()
        if self.decision == "refused" and not (self.motif or "").strip():
            raise ValidationError(_("Veuillez renseigner le motif du refus superviseur."))
        self.checklist_id.action_confirm_supervisor_decision(self.decision, self.motif)
        return {"type": "ir.actions.act_window_close"}
