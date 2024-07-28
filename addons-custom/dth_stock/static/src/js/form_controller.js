/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useSetupView } from "@web/views/view_hook";
patch(FormController.prototype, {
/* Patch FormController to restrict auto save in form views */
   setup(){
      super.setup(...arguments);
      useSetupView({
          beforeLeave: () => this.beforeLeave(),
          beforeUnload: (ev) => this.beforeUnload(ev),
      });
   },
   async beforeLeave() {
   /* function will work before leave the form */
      if(this.model.root.dirty){
          this.discard();
      }
   },
   beforeUnload: async (ev) => {
       ev.preventDefault();
   }
});
