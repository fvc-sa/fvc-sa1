from odoo import fields, models ,api


class PosConfig(models.Model):
    _inherit = "pos.config"

    group_negative_qty_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_groups",
        string="Point of Sale - Allow Negative Quantity",
        help="This field is there to pass the id of the 'PoS - Allow Negative"
        " Quantity' Group to the Point of Sale Frontend.",
    )

    employee_ids_with_neqative_rights = fields.Many2many(
        'hr.employee',
        'hr_employees_with_pos_rights',
        string='Allowed Employees with Negative Quantity',
        compute='_compute_employee_ids_with_negative_qty',
        help='Allowed Employees with Negative Quantity',
    )

  
    def _compute_groups(self):
        self.update(
            {
                "group_negative_qty_id": self.env.ref(
                    "pos_negative_quantity.group_negative_qty"
                ).id,
            }
        )

