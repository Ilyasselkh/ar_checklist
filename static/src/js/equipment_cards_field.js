/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class ArEquipmentCardsField extends Component {
    static template = "ar_checklist.EquipmentCardsField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.setState = this.setState.bind(this);
        this.updateComment = this.updateComment.bind(this);
    }

    get records() {
        return this.props.record.data[this.props.name]?.records || [];
    }

    equipmentName(record) {
        const value = record.data.equipment_id;
        if (Array.isArray(value)) {
            return value[1] || "";
        }
        return value?.display_name || value?.name || "";
    }

    isActive(record, state) {
        return record.data.state === state;
    }

    needsComment(record) {
        return ["nok", "abs"].includes(record.data.state);
    }

    async setState(record, state) {
        if (this.props.readonly) {
            return;
        }
        const values = { state };
        if (state === "ok") {
            values.comment = "";
        }
        await record.update(values);
    }

    async updateComment(record, comment) {
        if (this.props.readonly) {
            return;
        }
        await record.update({ comment });
    }
}

registry.category("fields").add("ar_equipment_cards", {
    component: ArEquipmentCardsField,
    supportedTypes: ["one2many"],
});
