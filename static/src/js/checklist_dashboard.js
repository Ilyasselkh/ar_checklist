/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ChecklistDashboard extends Component {
    static template = "ar_checklist.Dashboard";
    static props = ["*"];
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({data: null, loading: false, from: "", to: "", shift: "", chef: ""});
        this.flowLabels = [
            ["total_prep_manuf", "Préparé Manufacturing"], ["total_prep_trad", "Préparé Trading"],
            ["total_exp_manuf", "Expédié Manufacturing"], ["total_exp_trad", "Expédié Trading"],
            ["total_alim_tri", "Alimentation Tri"], ["total_dechargement", "Déchargement"],
        ];
        onWillStart(() => this.load());
    }
    async load() {
        this.state.loading = true;
        try {
            this.state.data = await this.orm.call("ar.checklist", "get_analysis_dashboard", [], {
                date_from: this.state.from || false, date_to: this.state.to || false,
                equipe: this.state.shift || false, chef_id: this.state.chef || false,
            });
        } finally {
            this.state.loading = false;
        }
    }
    number(value) { return new Intl.NumberFormat("fr-FR", {maximumFractionDigits: 2}).format(value); }
    rate(value) { return value === null ? "—" : `${this.number(value)} %`; }
    bar(value, key) {
        const max = Math.max(1, ...this.state.data.shifts.map(row => row[key]));
        return `width: ${Math.max(0, value / max * 100)}%`;
    }
    async openAnalysis(kind) {
        const action = await this.action.loadAction(`ar_checklist.action_analysis_${kind}`);
        return this.action.doAction({...action, domain: this.state.data.domain});
    }
    openChecklists(shift) {
        const domain = [...this.state.data.domain];
        if (shift) domain.push(["equipe", "=", shift]);
        return this.action.doAction({type: "ir.actions.act_window", name: "Checklists analysées",
            res_model: "ar.checklist", views: [[false, "list"], [false, "form"]],
            domain, context: {active_test: false}});
    }
    openLatest(id) {
        return this.action.doAction({type: "ir.actions.act_window", res_model: "ar.checklist",
            res_id: id, views: [[false, "form"]], context: {active_test: false}});
    }
}
registry.category("actions").add("ar_checklist.dashboard", ChecklistDashboard);
