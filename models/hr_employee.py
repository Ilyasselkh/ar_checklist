from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    team_leader_id = fields.Many2one(
        "hr.employee",
        string="Opérateur polyvalant",
        tracking=True,
        index=True,
    )
