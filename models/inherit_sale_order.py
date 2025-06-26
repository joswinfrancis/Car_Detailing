from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = 'create sale order'

    vehicle_name_id = fields.Many2one('detailing.vehicle', string='Vehicle Name', help='Vehicle details',
                                      tracking=True, required=True)

    internal_service_id = fields.Many2many('internal.services', string='Internal Services')
    external_service_id = fields.Many2many('external.services', string='External Services')
    job_card_id = fields.Many2one('register.customer', string='Job Card')

    @api.model
    def action_confirm(self, *args, **kwargs):
        result = super().action_confirm()

        if not self.job_card_id:
            # Create Job Card automatically
            job_card = self.env['register.customer'].create({
                'partner_id':self.partner_id.id,
                'customer_name': self.partner_id.name,
                'mobile_no': self.partner_id.phone or '',
                'email': self.partner_id.email or '',
                'vehicle_name_id': self.vehicle_name_id.id,
                'internal_service_id':self.internal_service_id,
                'external_service_id':self.external_service_id,
                'note': 'Generated from Sale Order %s' % self.name,
                'currency_id': self.currency_id.id,
                'sale_order_id': self.id,
            })
            self.job_card_id = job_card.id

        # Redirect to job card form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'register.customer',
            'view_mode': 'form',
            'res_id': self.job_card_id.id,
            'target': 'current',
        }

        return result

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if order.job_card_id and not self.env.context.get('from_job_card'):
                update_vals = {}
                if 'partner_id' in vals:
                    update_vals['partner_id'] = order.partner_id.id
                    update_vals['customer_name'] = order.partner_id.name
                    update_vals['mobile_no'] = order.partner_id.phone or ''
                    update_vals['email'] = order.partner_id.email or ''
                if 'vehicle_name_id' in vals:
                    update_vals['vehicle_name_id'] = order.vehicle_name_id.id
                if 'internal_service_id' in vals:
                    update_vals['internal_service_id'] = order.internal_service_id
                if 'external_service_id' in vals:
                    update_vals['external_service_id'] = order.external_service_id
                if 'currency_id' in vals:
                    update_vals['currency_id'] = order.currency_id.id

                if update_vals:
                    order.job_card_id.with_context(from_sale_order=True).write(update_vals)
        return res