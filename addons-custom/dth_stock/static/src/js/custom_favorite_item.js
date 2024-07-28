/** @odoo-module **/

import { CustomFavoriteItem } from "@web/search/custom_favorite_item/custom_favorite_item";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(CustomFavoriteItem.prototype, {
	setup() {
		super.setup(...arguments);
		this.dialogService = useService("dialog");
		let description = '';
		if (this.env.searchModel.resModel == 'dth.kho.sim.warehouse') {
			description = document.querySelector('.o_favorite_tab_name').value;
		}
		else {
			description = this.env.config.getDisplayName();
		}
        this.state = useState({
            description: description,
            isDefault: false,
            isShared: false,
        });
    },
    saveFavorite(ev) {
    	super.saveFavorite(ev);
    	location.reload();
    },
    
    deleteAllFavorite(ev) {
    	const favorites = this.env.searchModel.getSearchItems(
            (searchItem) => searchItem.type === "favorite"
        );
        const dialogProps = {
            title: "Cảnh báo",
            body: "Bạn có chắc muốn xóa tất cả bộ lọc yêu thích?",
            confirmLabel: "Xóa",
            confirm: () => this.deleteAllFavorites(favorites),
            cancel: () => {},
        };
        this.dialogService.add(ConfirmationDialog, dialogProps);
    },
    
    deleteAllFavorites(favorites) {
        for (const favorite of favorites) {
        	this.env.searchModel.deleteFavorite(favorite.id);
        }
    }   
});
