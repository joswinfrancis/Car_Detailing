# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Inherit config settings for adding journal field """
    _inherit = 'res.config.settings'

    invoice_journal_id = fields.Many2one('account.journal',
                                         string="Car Detailing Service Journal",
                                         config_parameter='car_detailing_service.invoice_journal_type',
                                         help='Set a journal for service')
