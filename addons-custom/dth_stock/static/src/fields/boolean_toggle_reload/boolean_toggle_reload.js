/** @odoo-module */

import { registry } from '@web/core/registry';
import { ListBooleanToggleField, listBooleanToggleField } from "@web/views/fields/boolean_toggle/list_boolean_toggle_field";

export class ListBooleanToggleReloadField extends ListBooleanToggleField {
    async onChange(value) {
        await super.onChange(value);
        return this.env.model.load();
    }
}

export const listBooleanToggleReloadField = {
    ...listBooleanToggleField,
    component: ListBooleanToggleReloadField,
};

registry.category("fields").add("boolean_toggle_reload", listBooleanToggleReloadField);
