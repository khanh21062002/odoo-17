/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";
import { formatDateTime } from "@web/core/l10n/dates";
import { RelativeTime } from "@mail/core/common/relative_time";

const { DateTime } = luxon;

export class DatetimeStringField extends Component {
    static template = "dth_stock.DatetimeStringField";
    static props = {
        ...standardFieldProps,
    };
    static components = {
        RelativeTime,
    };
    
    get datetime() {
    	return formatDateTime(this.props.record.data[this.props.name], { format: 'dd/MM/yy HH:mm' });
    }
    
}

export const datetimeStringField = {
    component: DatetimeStringField,
    displayName: "Date & Time",
    supportedTypes: ["datetime"],
};

registry.category("fields").add("datetime_string", datetimeStringField);
