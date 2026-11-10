from odoo import api, fields, models
from odoo.exceptions import ValidationError


ANALYSIS_DOMAIN = [
    ('active', '=', False), ('workflow_state', '=', 'archive'),
    ('supervisor_decision', '!=', 'refused'),
]
FLOW_FIELDS = (
    'total_prep_manuf', 'total_prep_trad', 'total_exp_manuf', 'total_exp_trad',
    'total_alim_tri', 'total_dechargement', 'total_prolongement',
)


class ArChecklistAnalysis(models.Model):
    _inherit = 'ar.checklist'

    analysis_staff_total = fields.Integer(
        string='Effectif comptabilisé', compute='_compute_analysis_staff', store=True)
    analysis_available = fields.Integer(
        string='Disponibles', compute='_compute_analysis_staff', store=True)
    analysis_unavailable = fields.Integer(
        string='Indisponibles', compute='_compute_analysis_staff', store=True)

    @api.depends('chef_id', 'chef_id.employee_id', 'operator_presence_ids',
                 'operator_presence_ids.available', 'operator_presence_ids.employee_id',
                 'operator_presence_ids.operator_id')
    def _compute_analysis_staff(self):
        for rec in self:
            extra = int(bool(rec.chef_id) and not rec._has_chef_in_operator_lines())
            rec.analysis_staff_total = len(rec.operator_presence_ids) + extra
            rec.analysis_available = len(rec.operator_presence_ids.filtered('available')) + extra
            rec.analysis_unavailable = rec.analysis_staff_total - rec.analysis_available

    @api.model
    def get_analysis_dashboard(self, date_from=False, date_to=False, equipe=False, chef_id=False):
        domain = list(ANALYSIS_DOMAIN)
        if date_from and date_to and fields.Date.to_date(date_from) > fields.Date.to_date(date_to):
            raise ValidationError('La date de début doit précéder la date de fin.')
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if equipe:
            domain.append(('equipe', '=', equipe))
        if chef_id:
            domain.append(('chef_id', '=', int(chef_id)))
        # Keep ordinary ORM access checks and record rules for all analytics.
        records = self.with_context(active_test=False).search(domain, order='date desc, heure desc, id desc')
        shifts = dict(self._fields['equipe']._description_selection(self.env))
        result = []
        for shift, label in shifts.items():
            rows = records.filtered(lambda rec: rec.equipe == shift)
            total = sum(rows.mapped('analysis_staff_total'))
            available = sum(rows.mapped('analysis_available'))
            latest = rows[:1]
            result.append({
                'key': shift, 'label': label, 'count': len(rows),
                'total': total, 'available': available,
                'unavailable': total - available, 'absent': sum(rows.mapped('nb_absents')),
                'rate': round(100 * available / total, 1) if total else None,
                'flows': {name: sum(rows.mapped(name)) for name in FLOW_FIELDS},
                'waiting_manuf': latest.total_att_exp_manuf if latest else 0,
                'waiting_trad': latest.total_att_exp_trad if latest else 0,
                'latest_id': latest.id if latest else False,
                'latest_name': latest.name if latest else '',
                'latest_date': str(latest.date) if latest else '',
            })
        total = sum(row['total'] for row in result)
        available = sum(row['available'] for row in result)
        choices = self.with_context(active_test=False).search(ANALYSIS_DOMAIN).mapped('chef_id')
        return {
            'domain': domain, 'shifts': result, 'count': len(records),
            'total': total, 'available': available,
            'absent': sum(row['absent'] for row in result),
            'rate': round(100 * available / total, 1) if total else None,
            'flows': {name: sum(row['flows'][name] for row in result) for name in FLOW_FIELDS},
            'chefs': [{'id': chef.id, 'name': chef.display_name} for chef in choices.sorted('name')],
        }
