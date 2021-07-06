odoo.define("pos_access_right.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var posmodel_super = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        get_cashier: function () {
            const pos_cashier = posmodel_super.get_cashier.apply(this);
            const cashier = this.env.pos.users.find(
                (user) => user.id === pos_cashier.user_id[0]
            );

            pos_cashier.employee_with_negative =false;
            const cashierwithnegative = this.config.employee_ids_with_neqative_rights ;

            if(typeof pos_cashier !== 'undefined'){
            if(typeof pos_cashier.id !== 'undefined'){

            //alert(pos_cashier.id);

             if (cashierwithnegative.length > 0 ){
                     if(cashierwithnegative.includes(pos_cashier.id)){
                        pos_cashier.employee_with_negative =true;

                    }
                    else {
                        pos_cashier.employee_with_negative=false;
                    }



            }
                }
                }
            pos_cashier.hasGroupNegativeQty =
                cashier &&
                cashier.groups_id.includes(
                    this.env.pos.config.group_negative_qty_id[0]
                );
            return pos_cashier;
        },
    });
});
