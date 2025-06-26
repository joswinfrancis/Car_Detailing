from odoo import models, fields


class ServiceStaff(models.Model):
    _name = 'service.staff'
    _description = 'employees working'
    _inherit = ['mail.thread']
    _rec_name = 'staff_name'

    staff_name = fields.Char(string="Staff Name")
    staff_address = fields.Char(string="Address")
    staff_mobile_no = fields.Char(string="Contact")
    staff_email = fields.Char(string="Email")
    position_id = fields.Many2one('staff.position', string="Position")
