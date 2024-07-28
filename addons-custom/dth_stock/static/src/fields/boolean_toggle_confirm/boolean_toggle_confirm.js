/** @odoo-module */

import { registry } from '@web/core/registry';
import { booleanToggleField, BooleanToggleField } from "@web/views/fields/boolean_toggle/boolean_toggle_field";
import { useBus, useService } from "@web/core/utils/hooks";
import {
    deleteConfirmationMessage,
    ConfirmationDialog,
} from "@web/core/confirmation_dialog/confirmation_dialog";

export class BooleanToggleConfirmField extends BooleanToggleField {
	static props = {
        ...BooleanToggleField.props,
        field_name: { type: String, optional: '' },
    };
	
	setup() {
        super.setup();
        this.dialogService = useService("dialog");
    }
    
	async onChange(value) {
		let message = ''
		if (this.props.field_name == 'priority_wh') {
			if (value === true) {
				message = 'Bạn chắc chắn muốn ưu tiên kho thợ đã chọn?';
			}
			else {
				message = 'Bạn chắc chắn muốn hủy ưu tiên kho thợ đã chọn?';
			}
		}
		else if (this.props.field_name == 'increase_show') {
			if (value === true) {
				message = 'Bạn chắc chắn muốn tăng hiển thị cho thợ đã chọn trên hệ thống bán hàng?';
			}
			else {
				message = 'Bạn chắc chắn muốn giảm hiển thị cho thợ đã chọn trên hệ thống bán hàng?';
			}
		}
		else if (this.props.field_name == 'keep_price') {
			if (value === true) {
				message = 'Bạn chắc chắn muốn giữ nguyên giá bán của thợ đã chọn?';
			}
			else {
				message = 'Bạn chắc chắn muốn hủy giữ nguyên giá bán của thợ đã chọn?';
			}
		}
		else if (this.props.field_name == 'auto_sms') {
			if (value === true) {
				message = 'Bạn có muốn bật tự động gửi SMS khi có khách đặt mua số sim mà thợ này có?';
			}
			else {
				message = 'Bạn có muốn tắt tự động gửi SMS khi có khách đặt mua số sim mà thợ này có?';
			}
		}
		else if (this.props.field_name == 'monopoly_wh') {
			if (value === true) {
				message = 'Bạn có chắc chắn muốn thiết lập kho đã chọn là kho độc quyền?';
			}
			else {
				message = 'Bạn có chắc chắn muốn bỏ thiết lập kho đã chọn là kho độc quyền?';
			}
		}
		else if (this.props.field_name == 'dth_wh') {
			if (value === true) {
				message = 'Bạn có chắc chắn muốn thiết lập kho đã chọn là kho nhà?';
			}
			else {
				message = 'Bạn có chắc chắn muốn bỏ thiết lập kho đã chọn là kho nhà?';
			}
		}
		else if (this.props.field_name == 'mapping_wh') {
			if (value === true) {
				message = 'Bạn có chắc chắn muốn thiết lập kho đã chọn là kho ánh xạ?';
			}
			else {
				message = 'Bạn có chắc chắn muốn bỏ thiết lập kho đã chọn là kho ánh xạ?';
			}
		}
		this.dialogService.add(ConfirmationDialog, {
            title: "Xác nhận",
            body: message,
            confirm: async () => {
                await super.onChange(value);
            },
            cancel: () => {
				return this.env.model.load();
			},
        });
    }
}

export const booleanToggleConfirmField = {
    ...booleanToggleField,
    component: BooleanToggleConfirmField,
    extractProps({ options }, dynamicInfo) {
        return {
			field_name: "field_name" in options ? options.field_name: '',
            autosave: "autosave" in options ? Boolean(options.autosave) : true,
            readonly: dynamicInfo.readonly,
        };
    },
};

registry.category("fields").add("boolean_toggle_confirm", booleanToggleConfirmField);