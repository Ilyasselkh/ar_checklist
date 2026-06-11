from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ArChecklist(models.Model):
    _name = "ar.checklist"
    _description = "Check-list de passation de changement d'équipe"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Reference", default="Nouveau", readonly=True, copy=False, tracking=True)
    name_display = fields.Char(string="Reference", compute="_compute_name_display")
    active = fields.Boolean(default=True, tracking=True)
    workflow_state = fields.Selection(
        [
            ("signature_1", "Signature 1"),
            ("signature_2", "Signature 2"),
        ],
        string="État",
        default="signature_1",
        required=True,
        tracking=True,
    )
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, tracking=True)
    date_display = fields.Char(string="Date", compute="_compute_date_display")
    equipe = fields.Selection(
        [
            ("shift_1", "Shift 1"),
            ("shift_2", "Shift 2"),
            ("shift_3", "Shift 3"),
        ],
        string="Équipe",
        required=True,
        tracking=True,
    )
    heure = fields.Float(string="Heure", default=lambda self: self._default_heure(), tracking=True)
    next_chef_id = fields.Many2one("res.users", string="Chef d'équipe suivant", tracking=True)
    is_next_chef = fields.Boolean(compute="_compute_is_next_chef")
    signature_1_user_id = fields.Many2one("res.users", string="Signé 1 par", readonly=True, copy=False)
    signature_1_date = fields.Datetime(string="Date signature 1", readonly=True, copy=False)
    signature_2_user_id = fields.Many2one("res.users", string="Signé 2 par", readonly=True, copy=False)
    signature_2_date = fields.Datetime(string="Date signature 2", readonly=True, copy=False)
    chef_id = fields.Many2one("res.users", string="Chef d'équipe", default=lambda self: self.env.user, tracking=True)
    operator_presence_ids = fields.One2many(
        "ar.checklist.operator.line",
        "checklist_id",
        string="Présence des opérateurs",
        default=lambda self: self._default_operator_presence_commands(),
    )
    equipment_line_ids = fields.One2many(
        "ar.checklist.equipment.line",
        "checklist_id",
        string="Équipements",
        default=lambda self: self._default_equipment_line_commands(),
    )
    nb_absents = fields.Integer(string="Nombre d'absence", compute="_compute_nb_absents", store=True)

    prep_manuf_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Préparation Manufacturing",
        domain=[("section", "=", "prep_manuf")],
        context={"default_section": "prep_manuf"},
    )
    prep_trad_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Préparation Trading",
        domain=[("section", "=", "prep_trad")],
        context={"default_section": "prep_trad"},
    )
    exp_manuf_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Expédition Manufacturing",
        domain=[("section", "=", "exp_manuf")],
        context={"default_section": "exp_manuf"},
    )
    exp_trad_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Expédition Trading",
        domain=[("section", "=", "exp_trad")],
        context={"default_section": "exp_trad"},
    )
    att_exp_manuf_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Attente Expédition Manuf",
        domain=[("section", "=", "att_exp_manuf")],
        context={"default_section": "att_exp_manuf"},
    )
    att_exp_trad_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Attente Expédition Trad",
        domain=[("section", "=", "att_exp_trad")],
        context={"default_section": "att_exp_trad"},
    )
    alim_tri_line_ids = fields.One2many(
        "ar.checklist.line",
        "checklist_id",
        string="Alimentation Tri",
        domain=[("section", "=", "alim_tri")],
        context={"default_section": "alim_tri"},
    )
    line_ids = fields.One2many("ar.checklist.line", "checklist_id", string="Toutes les lignes")

    total_prep_manuf = fields.Float(string="TOTAL PREP MANUF", compute="_compute_totals", store=True)
    total_prep_trad = fields.Float(string="TOTAL PREP TRAD", compute="_compute_totals", store=True)
    total_exp_manuf = fields.Float(string="TOTAL EXP MANUF", compute="_compute_totals", store=True)
    total_exp_trad = fields.Float(string="TOTAL EXP TRAD", compute="_compute_totals", store=True)
    total_att_exp_manuf = fields.Float(string="TOTAL Att Exp Manuf", compute="_compute_totals", store=True)
    total_att_exp_trad = fields.Float(string="TOTAL Att Exp Trad", compute="_compute_totals", store=True)
    total_alim_tri = fields.Float(string="TOTAL Alim Tri", compute="_compute_totals", store=True)

    nb_palettes_sol = fields.Integer(string="Nb Palettes Sol", tracking=True)
    nb_palettes_rci = fields.Integer(string="Nb Palettes RCI", tracking=True)
    nb_emp_vides_fg = fields.Integer(string="Nb Emp Vides FG", tracking=True)
    observations = fields.Text(string="Commentaire général", tracking=True)

    def _default_heure(self):
        now = fields.Datetime.context_timestamp(self, datetime.utcnow())
        return now.hour + (now.minute / 60.0)

    @api.depends("next_chef_id")
    def _compute_is_next_chef(self):
        current_user = self.env.user
        for rec in self:
            rec.is_next_chef = rec.next_chef_id == current_user

    @api.depends("name")
    def _compute_name_display(self):
        for rec in self:
            parts = (rec.name or "").split("/")
            if len(parts) == 3 and parts[0] == "CHK" and parts[1].isdigit() and len(parts[1]) == 4:
                rec.name_display = f"{parts[0]}/{parts[2]}"
            else:
                rec.name_display = rec.name

    @api.depends("date")
    def _compute_date_display(self):
        months = {
            1: "janvier",
            2: "février",
            3: "mars",
            4: "avril",
            5: "mai",
            6: "juin",
            7: "juillet",
            8: "août",
            9: "septembre",
            10: "octobre",
            11: "novembre",
            12: "décembre",
        }
        for rec in self:
            rec.date_display = ""
            if rec.date:
                rec.date_display = f"{rec.date.day} {months[rec.date.month]} {rec.date.year}"

    @api.onchange("chef_id")
    def _onchange_chef_id(self):
        self.operator_presence_ids = self._prepare_operator_presence_commands(self.chef_id)

    @api.depends("operator_presence_ids", "operator_presence_ids.present")
    def _compute_nb_absents(self):
        for rec in self:
            rec.nb_absents = len(rec.operator_presence_ids.filtered(lambda line: not line.present))

    @api.depends(
        "prep_manuf_line_ids.quantity",
        "prep_trad_line_ids.quantity",
        "exp_manuf_line_ids.quantity",
        "exp_trad_line_ids.quantity",
        "att_exp_manuf_line_ids.quantity",
        "att_exp_trad_line_ids.quantity",
        "alim_tri_line_ids.quantity",
    )
    def _compute_totals(self):
        for rec in self:
            rec.total_prep_manuf = sum(rec.prep_manuf_line_ids.mapped("quantity"))
            rec.total_prep_trad = sum(rec.prep_trad_line_ids.mapped("quantity"))
            rec.total_exp_manuf = sum(rec.exp_manuf_line_ids.mapped("quantity"))
            rec.total_exp_trad = sum(rec.exp_trad_line_ids.mapped("quantity"))
            rec.total_att_exp_manuf = sum(rec.att_exp_manuf_line_ids.mapped("quantity"))
            rec.total_att_exp_trad = sum(rec.att_exp_trad_line_ids.mapped("quantity"))
            rec.total_alim_tri = sum(rec.alim_tri_line_ids.mapped("quantity"))

    @api.onchange(
        "prep_manuf_line_ids",
        "prep_manuf_line_ids.quantity",
        "prep_trad_line_ids",
        "prep_trad_line_ids.quantity",
        "exp_manuf_line_ids",
        "exp_manuf_line_ids.quantity",
        "exp_trad_line_ids",
        "exp_trad_line_ids.quantity",
        "att_exp_manuf_line_ids",
        "att_exp_manuf_line_ids.quantity",
        "att_exp_trad_line_ids",
        "att_exp_trad_line_ids.quantity",
        "alim_tri_line_ids",
        "alim_tri_line_ids.quantity",
    )
    def _onchange_totals(self):
        self._compute_totals()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = self.env["ir.sequence"].next_by_code("ar.checklist") or "Nouveau"
        records = super().create(vals_list)
        for rec in records:
            if rec.chef_id and not rec.operator_presence_ids:
                rec.operator_presence_ids = rec._prepare_operator_presence_commands(rec.chef_id)
            rec._sync_equipment_lines()
        return records

    def write(self, vals):
        if vals and any(not rec.active for rec in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        if vals and not self.env.context.get("ar_checklist_workflow_write"):
            protected_fields = set(vals) - {"active"}
            locked = self.filtered(lambda rec: rec.workflow_state == "signature_2")
            if locked and protected_fields:
                raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))
        result = super().write(vals)
        if "chef_id" in vals and "operator_presence_ids" not in vals:
            for rec in self:
                rec.operator_presence_ids = rec._prepare_operator_presence_commands(rec.chef_id)
        return result

    def _default_operator_presence_commands(self):
        return self._prepare_operator_presence_commands(self.env.user)

    def _prepare_operator_presence_commands(self, chef_employee):
        chef_employee = self._employee_for_chef_user(chef_employee)
        if not chef_employee:
            return [(5, 0, 0)]
        operators = self.env["hr.employee"].sudo().search([
            ("team_leader_id", "=", chef_employee.id),
            ("active", "=", True),
        ], order="name")
        return [(5, 0, 0)] + [
            (0, 0, {"operator_id": operator.user_id.id or False, "operator_name": operator.name, "present": True})
            for operator in operators
        ]

    def _employee_for_chef_user(self, chef_user):
        chef_user = chef_user.exists()
        if not chef_user:
            return self.env["hr.employee"]
        employee = chef_user.employee_id
        if not employee:
            employee = self.env["hr.employee"].sudo().search([("user_id", "=", chef_user.id)], limit=1)
        return employee

    def _default_equipment_line_commands(self):
        return [
            (0, 0, {"equipment_id": equipment.id})
            for equipment in self.env["ar.checklist.equipment"].search([("active", "=", True)], order="sequence, name")
        ]

    def _sync_equipment_lines(self):
        equipment_model = self.env["ar.checklist.equipment"]
        for checklist in self:
            existing_equipment = checklist.equipment_line_ids.mapped("equipment_id")
            missing_equipment = equipment_model.search([("active", "=", True)], order="sequence, name") - existing_equipment
            for equipment in missing_equipment:
                self.env["ar.checklist.equipment.line"].create({
                    "checklist_id": checklist.id,
                    "equipment_id": equipment.id,
                })

    def action_archive(self):
        self.write({"active": False})

    def action_save_checklist(self):
        return True

    def action_signature_1(self):
        for rec in self:
            if not rec.active:
                raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
            if rec.workflow_state != "signature_1":
                continue
            if not rec.next_chef_id:
                raise ValidationError(_("Veuillez renseigner le Chef d'équipe suivant avant la Signature 1."))
            rec.with_context(ar_checklist_workflow_write=True).write({
                "workflow_state": "signature_2",
                "signature_1_user_id": self.env.user.id,
                "signature_1_date": fields.Datetime.now(),
            })
        return True

    def action_signature_2(self):
        for rec in self:
            if not rec.active:
                raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
            if rec.workflow_state != "signature_2" or rec.signature_2_user_id:
                continue
            if rec.next_chef_id != self.env.user:
                raise ValidationError(_("Seul le Chef d'équipe suivant peut valider la Signature 2."))
            rec.with_context(ar_checklist_workflow_write=True).write({
                "signature_2_user_id": self.env.user.id,
                "signature_2_date": fields.Datetime.now(),
                "active": False,
            })
        return True


class ArChecklistLine(models.Model):
    _name = "ar.checklist.line"
    _description = "Ligne Check-list de passation"
    _order = "sequence, id"

    checklist_id = fields.Many2one("ar.checklist", string="Checklist", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    section = fields.Selection(
        [
            ("prep_manuf", "Préparation Manufacturing"),
            ("prep_trad", "Préparation Trading"),
            ("exp_manuf", "Expédition Manufacturing"),
            ("exp_trad", "Expédition Trading"),
            ("att_exp_manuf", "Attente Expédition Manuf"),
            ("att_exp_trad", "Attente Expédition Trad"),
            ("alim_tri", "Alimentation Tri"),
        ],
        required=True,
    )
    client_line_id = fields.Many2one("ar.checklist.client.line", string="Client / Reference")
    quantity = fields.Float(string="Nb de palettes")

    def _check_signature_editable(self):
        if any(line.checklist_id.workflow_state == "signature_2" for line in self):
            raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))

    @api.model_create_multi
    def create(self, vals_list):
        checklist_ids = [vals.get("checklist_id") for vals in vals_list if vals.get("checklist_id")]
        if checklist_ids:
            locked_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: rec.workflow_state == "signature_2")
            if locked_checklists:
                raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))
        if checklist_ids:
            archived_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: not rec.active)
            if archived_checklists:
                raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().create(vals_list)

    def write(self, vals):
        if vals:
            self._check_signature_editable()
        if vals and any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().write(vals)

    def unlink(self):
        self._check_signature_editable()
        if any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().unlink()


class ArChecklistEquipmentLine(models.Model):
    _name = "ar.checklist.equipment.line"
    _description = "État équipement Check-list"
    _order = "sequence, id"

    checklist_id = fields.Many2one("ar.checklist", string="Checklist", required=True, ondelete="cascade")
    equipment_id = fields.Many2one("ar.checklist.equipment", string="Équipement", required=True, ondelete="restrict")
    sequence = fields.Integer(related="equipment_id.sequence", store=True)
    state = fields.Selection([("ok", "OK"), ("nok", "NOK"), ("abs", "ABS")], string="État")

    def _check_signature_editable(self):
        if any(line.checklist_id.workflow_state == "signature_2" for line in self):
            raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))

    @api.model_create_multi
    def create(self, vals_list):
        checklist_ids = [vals.get("checklist_id") for vals in vals_list if vals.get("checklist_id")]
        if checklist_ids:
            locked_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: rec.workflow_state == "signature_2")
            if locked_checklists:
                raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))
        if checklist_ids:
            archived_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: not rec.active)
            if archived_checklists:
                raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().create(vals_list)

    def write(self, vals):
        if vals and any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        if vals:
            self._check_signature_editable()
        if "equipment_id" in vals:
            raise ValidationError(_("Vous pouvez modifier uniquement l'état des équipements."))
        return super().write(vals)

    def _set_state(self, state):
        self.write({"state": state})
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_set_ok(self):
        return self._set_state("ok")

    def action_set_nok(self):
        return self._set_state("nok")

    def action_set_abs(self):
        return self._set_state("abs")

    def unlink(self):
        self._check_signature_editable()
        if any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().unlink()


class ArChecklistOperatorLine(models.Model):
    _name = "ar.checklist.operator.line"
    _description = "Présence opérateur Check-list de passation"
    _order = "id"

    checklist_id = fields.Many2one("ar.checklist", string="Checklist", required=True, ondelete="cascade")
    operator_id = fields.Many2one("res.users", string="Utilisateur opérateur")
    operator_name = fields.Char(string="Opérateur", compute="_compute_operator_name", store=True, readonly=False)
    present = fields.Boolean(string="Présence", default=True)
    def _check_signature_editable(self):
        if any(line.checklist_id.workflow_state == "signature_2" for line in self):
            raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))

    @api.depends("operator_id")
    def _compute_operator_name(self):
        for line in self:
            if not line.operator_name:
                line.operator_name = line.operator_id.name or ""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("operator_id") and not vals.get("operator_name"):
                raise ValidationError(_("Les opérateurs affectés sont générés automatiquement depuis le paramétrage. Vous ne pouvez pas ajouter une ligne vide."))
        checklist_ids = [vals.get("checklist_id") for vals in vals_list if vals.get("checklist_id")]
        if checklist_ids:
            locked_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: rec.workflow_state == "signature_2")
            if locked_checklists:
                raise ValidationError(_("Cette check-list est en Signature 2. Elle n'est plus modifiable."))
        if checklist_ids:
            archived_checklists = self.env["ar.checklist"].browse(checklist_ids).filtered(lambda rec: not rec.active)
            if archived_checklists:
                raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().create(vals_list)

    def write(self, vals):
        if vals and any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        if vals:
            self._check_signature_editable()
        if "operator_id" in vals or "operator_name" in vals:
            raise ValidationError(_("Vous pouvez modifier uniquement la présence des opérateurs."))
        return super().write(vals)

    def unlink(self):
        self._check_signature_editable()
        if any(not line.checklist_id.active for line in self):
            raise ValidationError(_("Cette check-list est archivée. Vous devez la désarchiver avant de la modifier."))
        return super().unlink()
