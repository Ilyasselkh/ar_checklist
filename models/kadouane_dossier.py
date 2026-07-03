from odoo import api, models
from odoo.osv import expression


class KadouaneDossier(models.Model):
    _inherit = "kadouane.kadouane"

    @api.depends("referenceID", "name")
    def _compute_display_name(self):
        if not self.env.context.get("ar_checklist_reference_display"):
            return super()._compute_display_name()
        for record in self:
            record.display_name = record.referenceID or record.name or str(record.id)

    @api.model
    def _name_search(self, name="", domain=None, operator="ilike", limit=None, order=None):
        if not self.env.context.get("ar_checklist_reference_display") or not name:
            return super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
        search_domain = expression.OR([
            [("referenceID", operator, name)],
            [("client_id.name", operator, name)],
        ])
        return self._search(expression.AND([domain or [], search_domain]), limit=limit, order=order)

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        if not self.env.context.get("ar_checklist_reference_display") or not name:
            return super().name_search(name=name, domain=domain, operator=operator, limit=limit)
        base_domain = domain or []
        records = self.search(
            expression.AND([base_domain, [("referenceID", operator, name)]]),
            limit=limit,
        )
        remaining = None if limit is None else max(limit - len(records), 0)
        if remaining:
            extra_records = self.search(
                expression.AND([
                    base_domain,
                    [("id", "not in", records.ids)],
                    [("client_id.name", operator, name)],
                ]),
                limit=remaining,
            )
            records |= extra_records
        return [(record.id, record.display_name) for record in records]
