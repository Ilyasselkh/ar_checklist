/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog";

// Use native relational exports: every table row keeps its own cell values.
function checklistExportFields() {
    const fields = [];
    const add = (name, string, type = "char") => fields.push({ name, string, type });
    const table = (relation, label, columns) => {
        for (const [name, title, type] of columns) {
            add(`${relation}/${name}`, `${label} / ${title}`, type);
        }
    };
    table("operator_presence_ids", "Opérateurs affectés", [
        ["operator_name", "Opérateur"],
    ]);
    for (const [relation, label, item] of [
        ["equipment_line_ids", "Équipements", "equipment_id"],
        ["zone_line_ids", "Zones", "zone_id"],
    ]) {
        table(relation, label, [[item, "Nom", "many2one"], ["state", "État", "selection"], ["comment", "Commentaire", "text"]]);
    }
    for (const [section, label] of [
        ["prep_manuf", "Préparation Manufacturing"],
        ["prep_trad", "Préparation Trading"],
        ["exp_manuf", "Expédition Manufacturing"],
        ["exp_trad", "Expédition Trading"],
        ["att_exp_manuf", "Attente Expédition Manufacturing"],
        ["att_exp_trad", "Attente Expédition Trading"],
        ["alim_tri", "Alimentation Tri"],
        ["dechargement", "Déchargement"],
        ["prolongement", "Prolongement"],
    ]) {
        const columns = section === "prolongement"
            ? [["reference", "Référence"], ["of", "OF"]]
            : section === "alim_tri"
                ? [["reference", "Référence"]]
                : [[section === "dechargement" ? "dechargement_dossier_id/referenceID" : "dossier_id/referenceID", "N° dossier"],
                    ["client_name", section === "dechargement" ? "Fournisseurs" : "Client"]];
        columns.push(["quantity", section === "prolongement" ? "Carton/Qte" : "Nb palettes", "float"]);
        table(`${section}_line_ids`, label, columns);
        add(`total_${section}`, `Total ${label}`, "float");
    }
    for (const [name, label] of [
        ["nb_palettes_sol", "Nb Palettes Sol"], ["nb_palettes_rci", "Nb Palettes RCI"],
        ["nb_emp_vides_fg", "Nb Emp Vides FG"], ["nb_test", "Nb de palettes réceptionnées"],
    ]) {
        add(name, label, "integer");
    }
    return fields;
}

class ChecklistListController extends ListController {
    getExportableFields() {
        const fields = super.getExportableFields();
        if (!this.props.context.ar_checklist_archive_export) {
            return fields;
        }
        const names = new Set(fields.map((field) => field.name));
        return [...fields, ...checklistExportFields().filter((field) => !names.has(field.name))];
    }
}

registry.category("views").add("ar_checklist_list", {
    ...listView,
    Controller: ChecklistListController,
});

patch(ExportDataDialog.prototype, {
    async setDefaultExportList() {
        if (this.props.root.resModel === "ar.checklist" &&
            this.props.context?.ar_checklist_archive_export && !this.isCompatible) {
            // The native dialog initially knows root fields only. Load the
            // relational children before it resolves the default column list.
            for (const field of this.props.defaultExportList) {
                const parts = field.name.split("/");
                for (let depth = 1; depth < parts.length; depth++) {
                    const parent = parts.slice(0, depth).join("/");
                    if (this.knownFields[parent] && !this.expandedFields[parent]) {
                        await this.loadFields(parent);
                    }
                }
            }
        }
        return super.setDefaultExportList(...arguments);
    },
});
