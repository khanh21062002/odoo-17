/** @odoo-module **/

import { SearchBar } from "@web/search/search_bar/search_bar";
import { patch } from "@web/core/utils/patch";

patch(SearchBar.prototype, {
   async selectItem(item) {
   		super.selectItem(item);
   		const model = this.env.searchModel.resModel;
		const orm = this.env.services.orm;
   		if (model == 'dth.kho.sim.warehouse' && item.searchItemDescription == 'Số sim') {
   			document.querySelector('.o_favorite_tab_name').value = item.value;
			if (/^0\d{9}$/.test(item.value)) {
				try {
					await orm.create("dth.kho.sim.search.history", [{ "sim_search": item.value }]);
				} catch (error) {
					console.error("Failed to save sim lookup:", error);
				}
			}
   		}
    }
});
