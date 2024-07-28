/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { formatMonetary } from "@web/views/fields/formatters";
import { parseMonetary } from "@web/views/fields/parsers";
import { useInputField } from "@web/views/fields/input_field_hook";
import { useNumpadDecimal } from "@web/views/fields/numpad_decimal_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component } from "@odoo/owl";
import { getCurrency } from "@web/core/currency";

export class MonetaryPriceField extends Component {
    static template = "web.MonetaryPriceField";
    static props = {
        ...standardFieldProps,
        currencyField: { type: String, optional: true },
        inputType: { type: String, optional: true },
        useFieldDigits: { type: Boolean, optional: true },
        hideSymbol: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
    };
    static defaultProps = {
        hideSymbol: false,
        inputType: "text",
    };

    setup() {
        useInputField(this.inputOptions);
        useNumpadDecimal();
    }

    get inputOptions() {
        return {
            getValue: () => this.formattedValue,
            refName: "numpadDecimal",
            parse: parseMonetary,
        };
    }

    get currencyId() {
        const currencyField =
            this.props.currencyField ||
            this.props.record.fields[this.props.name].currency_field ||
            "currency_id";
        const currency = this.props.record.data[currencyField];
        return currency && currency[0];
    }
    get currency() {
        if (!isNaN(this.currencyId)) {
            return getCurrency(this.currencyId) || null;
        }
        return null;
    }

    get currencySymbol() {
        return this.currency ? this.currency.symbol : "";
    }

    get currencyDigits() {
        if (this.props.useFieldDigits) {
            return this.props.record.fields[this.props.name].digits;
        }
        if (!this.currency) {
            return null;
        }
        return getCurrency(this.currencyId).digits;
    }

    get value1() {
        return this.props.record.data['sell_price_s'];
    }
    
    get value2() {
        return this.props.record.data['buy_price_s'];
    }

    get price1FormattedValue() {
        return formatMonetary(this.value1, {
            digits: this.currencyDigits,
            currencyId: this.currencyId,
            noSymbol: !this.props.readonly || this.props.hideSymbol,
        });
    }
    
    get price2FormattedValue() {
        return formatMonetary(this.value2, {
            digits: this.currencyDigits,
            currencyId: this.currencyId,
            noSymbol: !this.props.readonly || this.props.hideSymbol,
        });
    }
}

export const monetaryPriceField = {
    component: MonetaryPriceField,
    supportedOptions: [
        {
            label: _t("Hide symbol"),
            name: "no_symbol",
            type: "boolean",
        },
        {
            label: _t("Currency"),
            name: "currency_field",
            type: "field",
            availableTypes: ["many2one"],
        },
    ],
    supportedTypes: ["monetary", "float"],
    displayName: _t("Monetary"),
    extractProps: ({ attrs, options }) => ({
        currencyField: options.currency_field,
        inputType: attrs.type,
        useFieldDigits: options.field_digits,
        hideSymbol: options.no_symbol,
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("monetary_price", monetaryPriceField);
