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

    async setState(record, state) {
        if (this.props.readonly) {
            return;
        }
        await record.update({ state });
    }
}

registry.category("fields").add("ar_equipment_cards", {
    component: ArEquipmentCardsField,
    supportedTypes: ["one2many"],
});
