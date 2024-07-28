/** @odoo-module **/
import { registry } from "@web/core/registry";

export function openCopyBoardAction(env, action) {
    document.querySelector('.copy-board-container').style.display = 'block';
    document.querySelector('.copy-board').value = document.querySelector('.copy-board').value + action.params.content;
}

registry.category("actions").add("display_copy_board", openCopyBoardAction);

