/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class FloatPriorityField extends Component {
    static template = "dth_stock.FloatPriorityField";
    static props = {
        ...standardFieldProps,
    };
}

export const floatPriorityField = {
    component: FloatPriorityField,
    displayName: "Priority",
    supportedTypes: ["float"],
};

registry.category("fields").add("float_priority", floatPriorityField);
