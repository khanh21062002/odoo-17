/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class Many2oneImgageField extends Component {
    static template = "dth_stock.Many2oneImageField";
    static props = {
        ...standardFieldProps,
    };
    
    get relation() {
        return this.props.relation || this.props.record.fields[this.props.name].relation;
    }
}

export const many2oneImgageField = {
    component: Many2oneImgageField,
    supportedTypes: ["many2one"],
};

registry.category("fields").add("many2one_image", many2oneImgageField);
