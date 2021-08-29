
from odoo import fields, models
class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_print_session_summary = fields.Boolean("Print Session Summary", default=1)