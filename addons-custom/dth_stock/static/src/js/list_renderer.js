/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
	getCellTitle(column, record) {
        const fieldType = this.fields[column.name].type;
        if (fieldType == 'html') {
        	return '';
        }
        else {
        	return super.getCellTitle(column, record)
        }
    }
});

