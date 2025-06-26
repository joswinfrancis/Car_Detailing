from odoo import models, fields

class VehicleTag(models.Model):
    _name = 'vehicle.tag'
    _description = 'Vehicle Tags'
    _inherit = ['mail.thread']

    name = fields.Char(string="Vehicle Tag Name")

