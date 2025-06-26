from odoo import models, fields

class VehicleImage(models.Model):
    _name = 'vehicle.image'
    _description = 'Vehicle Condition Image'

    image = fields.Image(string='Photo', required=True)
    description = fields.Char(string='Description (e.g., Front View, Left Side)')
    register_id = fields.Many2one('register.customer', string='Customer Registration')

