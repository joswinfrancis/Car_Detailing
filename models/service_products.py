from odoo import models, fields, api

class ServiceProducts(models.Model):
    _name = 'service.products'
    _description = 'products used in service'
    _inherit = ['mail.thread']
    _rec_name = 'product_name'


    product_code = fields.Char(default='New')
    product_name = fields.Char(string="Product Price")
    product_price = fields.Monetary(string="Product Price")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.ref('base.INR'))


    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.product_code == 'New':
                record.product_code = self.env['ir.sequence'].next_by_code('service.products')
        return records




