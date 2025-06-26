from odoo import models, fields, api


class InternalServices(models.Model):
    _name = 'internal.services'
    _description = 'internal services we offer'
    _inherit = ['mail.thread']
    _rec_name = 'service_name'

    service_name = fields.Char(string="Service Name")
    service_description = fields.Text(string="Service Description")
    product_id = fields.Many2many('service.products', string="Materials Used", required=True)
    service_charge = fields.Monetary(string="Service Charge")
    total_service_cost = fields.Monetary(compute='_compute_total_cost', string="Total Service Cost")
    product_total_price = fields.Monetary(compute='_compute_product_total_price', string="Total Product Price")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.ref('base.INR'))

    @api.depends('product_id')
    def _compute_product_total_price(self):
        for record in self:
            record.product_total_price = sum(product.product_price for product in record.product_id)

    @api.depends('service_charge', 'product_total_price')
    def _compute_total_cost(self):
        for record in self:
            record.total_service_cost = record.service_charge + record.product_total_price
