from odoo import models, fields

class DetailingVehicle(models.Model):
    _name = 'detailing.vehicle'
    _description = 'Vehicles'
    _inherit = ['mail.thread']
    _rec_name = 'model_name'


    model_name = fields.Char(string="Vehicle Model")
    manufacturer = fields.Char(string="Manufacturer")
    vehicle_name = fields.Char(string="Vehicle Name")
    vehicle_type_id = fields.Many2one('vehicle.tag', string="Type")


