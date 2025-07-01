# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = 'create sale order'

    vehicle_name_id = fields.Many2one('detailing.vehicle', string='Vehicle Name', help='Vehicle details',
                                      tracking=True, required=True)

    internal_service_id = fields.Many2many('internal.services', string='Internal Services')
    external_service_id = fields.Many2many('external.services', string='External Services')
    job_card_id = fields.Many2one('register.customer', string='Job Card')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    def action_view_job_card(self):
        self.ensure_one()

        return {
            'name': 'Job Card',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'register.customer',
            'res_id': self.job_card_id.id,
            'target': 'current',
        }

    @api.model
    def action_confirm(self, *args, **kwargs):

        result = super().action_confirm()

        if not self.job_card_id:
            # Create Job Card automatically
            job_card = self.env['register.customer'].create({
                'partner_id': self.partner_id.id,
                'customer_name': self.partner_id.name,
                'mobile_no': self.partner_id.phone or '',
                'email': self.partner_id.email or '',
                'vehicle_name_id': self.vehicle_name_id.id,
                'internal_service_id': [(6, 0, self.internal_service_id.ids)],
                'external_service_id': [(6, 0, self.external_service_id.ids)],
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


    def write(self, vals):
        for order in self:
            old_internal_services = order.internal_service_id
            old_external_services = order.external_service_id

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

            if 'internal_service_id' in vals or 'external_service_id' in vals:

                was_sale = order.state == 'sale'

                if was_sale:
                    order.action_cancel()
                    order.state = 'draft'

                def get_line_domain(service):
                    return [
                        ('order_id', '=', order.id),
                        ('product_id', '=', service.product_id.id),
                        ('name', '=', service.service_description),
                        ('price_unit', '=', service.total_service_cost),
                    ]

                # Handle removed internal services
                removed_internal = old_internal_services - order.internal_service_id
                for removed in removed_internal:
                    line = self.env['sale.order.line'].search(get_line_domain(removed), limit=1)
                    if line:
                        line.unlink()

                # Handle removed external services
                removed_external = old_external_services - order.external_service_id
                for removed in removed_external:
                    line = self.env['sale.order.line'].search(get_line_domain(removed), limit=1)
                    if line:
                        line.unlink()

                def add_service_line_if_not_exists(service):
                    domain = [
                        ('order_id', '=', order.id),
                        ('product_id', '=', service.product_id.id),
                        ('name', '=', service.service_description),
                        ('price_unit', '=', service.total_service_cost),
                    ]
                    existing_line = self.env['sale.order.line'].search(domain, limit=1)

                    if not existing_line:
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': service.product_id.id,
                            'name': service.service_description,
                            'product_uom_qty': 1,
                            'price_unit': service.total_service_cost,
                            'product_uom': service.product_id.uom_id.id,
                        })

                # Internal services
                for service in order.internal_service_id:
                    add_service_line_if_not_exists(service)

                # External services
                for service in order.external_service_id:
                    add_service_line_if_not_exists(service)

                if was_sale:
                    order.action_confirm()

        return res



# class SaleOrderLineInherit(models.Model):
#
#     _inherit = 'sale.order.line'
#     _description = 'sale order line'
#
#
#     sale_order_id = fields.Many2one('sale.order', string='order reference', required=True)
#     internal_service_line_id = fields.Many2one('internal.services', string="Internal Service Line")
#     external_service_line_id = fields.Many2one('external.services', string="External Service Line")
#
#     @api.model
#     def create(self, vals):
#         line = super().create(vals)
#
#         # Skip if it's being created from internal/external service logic
#         if self.env.context.get('from_service_sync'):
#             return line
#
#         sale_order = line.order_id
#         service_domain = [
#             ('product_id', '=', line.product_id.id),
#             ('service_description', '=', line.name),
#             ('total_service_cost', '=', line.price_unit),
#         ]
#
#         # Check if matches internal service
#         internal_service = self.env['internal.services'].search(
#             service_domain + [('id', 'in', sale_order.internal_service_id.ids)], limit=1
#         )
#         if not internal_service:
#             internal_service = self.env['internal.services'].create({
#                 'product_id': line.product_id.id,
#                 'service_description': line.name,
#                 'total_service_cost': line.price_unit,
#             })
#             sale_order.with_context(from_sale_order_line=True).write({
#                 'internal_service_id': [(4, internal_service.id)],
#             })
#             line.internal_service_line_id = internal_service.id
#
#         return line
#
#     def unlink(self):
#         for line in self:
#             sale_order = line.order_id
#
#             # Remove internal service link
#             if line.internal_service_line_id:
#                 sale_order.with_context(from_sale_order_line=True).write({
#                     'internal_service_id': [(3, line.internal_service_line_id.id)],
#                 })
#
#             # Remove external service link
#             if line.external_service_line_id:
#                 sale_order.with_context(from_sale_order_line=True).write({
#                     'external_service_id': [(3, line.external_service_line_id.id)],
#                 })
#
#         return super().unlink()


