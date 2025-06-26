from odoo import models, fields, api
from datetime import date


class ServiceFeedback(models.Model):
    _name = 'service.feedback'
    _description = 'Customer Feedback for Car Detailing'
    _inherit = ['mail.thread']
    _rec_name = 'customer_id'


    customer_id = fields.Many2one('register.customer', string="Registered Customer", required=True, tracking=True)
    address = fields.Char(related="customer_id.address", string="Address")
    mobile_no = fields.Char(related="customer_id.mobile_no", string="Contact Number")
    email = fields.Char(related="customer_id.email", string="Email")
    feedback_date = fields.Date(string="Feedback Date", default=fields.Date.context_today, readonly=True)
    overall_rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ], string='Rating', required=True, tracking=True)

    rating_staff = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ], string='Rating', required=True, tracking=True)

    rating_pricing = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ], string='Rating', required=True, tracking=True)
    recommend = fields.Selection([
        ('recommend', 'Definitely Recommend'),
        ('not_recommend', 'Will Never Recommend'),
    ])

    comments = fields.Text(string='Customer Comments')

    def action_feedback_updated(self):
        self.customer_id.state = 'feedback_updated'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Register Customer',
            'res_model': 'register.customer',
            'view_mode': 'form',
            'res_id': self.customer_id.id,
            'target': 'current',
        }
