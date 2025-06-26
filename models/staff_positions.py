from odoo import models, fields

class StaffPosition(models.Model):
    _name = 'staff.position'
    _description = 'working staff positions'
    _inherit = ['mail.thread']

    name = fields.Char(string="Staff Position")

