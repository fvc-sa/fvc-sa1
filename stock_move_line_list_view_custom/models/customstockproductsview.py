# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import traceback
import json
import requests
from odoo import api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _
from requests.structures import CaseInsensitiveDict
from logging import getLogger
from odoo.http import request
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.depends('qty_done','location_id.minus_values','location_dest_id.minus_values')
    def _compute_real_qty(self):
        for each in self:
            if each.location_id.minus_values or each.location_dest_id.minus_values:
                each.real_qty = -each.qty_done
            else :
                each.real_qty = each.qty_done

    real_qty  = fields.Float('Real Qty',compute="_compute_real_qty",store=True, digits='Product Unit of Measure')


class StockLocation(models.Model):
    _inherit = 'stock.location'

    minus_values=fields.Boolean(default=False,
                                string=' Minus Valus Product Moves ')
