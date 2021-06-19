odoo.define("pos_access_right.NumpadWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");

    const PosNumpadWidget = (NumpadWidget) =>
        class extends NumpadWidget {

            get hasMinusControlRights() {
                if (this.env.pos.get_cashier().hasGroupNegativeQty) {
                    return true;
                }
                return false;
            }
        };

    Registries.Component.extend(NumpadWidget, PosNumpadWidget);

    return NumpadWidget;
});
