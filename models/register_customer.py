# -*- coding: utf-8 -*-
###############################################################################
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import date


class RegisterCustomer(models.Model):
    """Model for registering customer"""
    _name = 'register.customer'
    _description = "customer details"
    _inherit = ['mail.thread']
    _rec_name = 'customer_name'

    reference = fields.Char(default='New')
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    customer_name = fields.Char(string="Customer", required=True)
    address = fields.Char(string="Address")
    mobile_no = fields.Char(string="Contact Number")
    email = fields.Char(string="Email")

    note = fields.Text(string='Additional Notes')


    state = fields.Selection([
        ('draft', 'draft'),
        ('registered', 'Registered'),
        ('work_started', 'Work Started'),
        ('work_in_progress', 'Work In Progress'),
        ('work_done', 'Work Done'),
        ('delivered', 'Vehicle Delivered'),
        ('feedback_updated', 'Feedback Updated'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    vehicle_name_id = fields.Many2one('detailing.vehicle', string='Vehicle', help='Vehicle details',
                               tracking=True, required=True)

    meter_reading = fields.Integer(string="Meter Reading(km)")
    manufacturing_year = fields.Integer(string="Manufacturing Year")

    vehicle_plate = fields.Char(string="Plate Number")

    vehicle_images_ids = fields.One2many('vehicle.image', 'register_id',
                                         string='Vehicle Condition Photos')

    assigned_to_id = fields.Many2one('service.staff', string="Assigned To")
    starting_date = fields.Date(string="Starting Date")
    ending_date = fields.Date(string="Expected Delivery Date")
    service_notes = fields.Text(string="Service Note")
    sub_total = fields.Monetary(compute='_compute_sub_total', string="Sub Total", store=True)
    total_internal_service_cost = fields.Monetary(compute='_compute_total_internal_service_cost', string="Total Internal Service Cost")
    total_external_service_cost = fields.Monetary(compute='_compute_total_external_service_cost', string="Total External Service Cost")
    internal_service_id = fields.Many2many('internal.services', string='Internal Services')
    external_service_id = fields.Many2many('external.services', string='External Services')
    discount = fields.Integer(string="Discount")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.ref('base.INR'))
    sale_order_id = fields.Many2one('sale.order', string='order reference', required=True)



    @api.depends('internal_service_id', 'external_service_id')
    def _compute_sub_total(self):
        for record in self:
            record.sub_total = (sum(cost.total_service_cost for cost in record.internal_service_id) +
                                sum(cost.total_service_cost for cost in record.external_service_id))

    @api.depends('internal_service_id')
    def _compute_total_internal_service_cost(self):
        for record in self:
            record.total_internal_service_cost = sum(cost.total_service_cost for cost in record.internal_service_id)


    @api.depends('external_service_id')
    def _compute_total_external_service_cost(self):
        for record in self:
            record.total_external_service_cost = sum(cost.total_service_cost for cost in record.external_service_id)


    def action_register(self):
        self.state = 'registered'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_start_work(self):
        self.state = 'work_started'

    def action_work_in_progress(self):
        self.state = 'work_in_progress'

    def action_work_done(self):
        self.state = 'work_done'


    def action_delivered(self):
        self.ensure_one()

        if not self.sale_order_id:
            raise UserError("No Sale Order linked to this record.")

        # Get valid (not cancelled) customer invoices from the sale order
        invoice = self.sale_order_id.invoice_ids.filtered(
            lambda inv: inv.move_type == 'out_invoice' and inv.state != 'cancel'
        )

        if not invoice:
            raise UserError("Cannot mark as delivered: Invoice not created.")

        # Get the posted invoice(s)
        posted_invoice = invoice.filtered(lambda inv: inv.state == 'posted')

        if not posted_invoice:
            raise UserError("Cannot mark as delivered: Invoice not confirmed (posted).")

        # Check for pending payment
        unpaid_invoice = posted_invoice.filtered(lambda inv: inv.amount_residual > 0)

        if unpaid_invoice:
            raise UserError("Cannot mark as delivered: Invoice payment is still pending.")

        self.state = 'delivered'

    def action_get_feedback(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Feedback',
            'res_model': 'service.feedback',
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.reference == 'New':
                record.reference = self.env['ir.sequence'].next_by_code('register.customer')
        return records

    def action_create_invoice(self):
        self.ensure_one()

        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_view_quotation(self):
        self.ensure_one()

        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def write(self, vals):
        res = super().write(vals)
        for job_card in self:
            if job_card.sale_order_id and not self.env.context.get('from_sale_order'):
                update_vals = {}
                if 'partner_id' in vals:
                    update_vals['partner_id'] = job_card.partner_id.id
                    update_vals['customer_name'] = job_card.partner_id.name
                    update_vals['mobile_no'] = job_card.partner_id.phone or ''
                    update_vals['email'] = job_card.partner_id.email or ''
                if 'vehicle_name_id' in vals:
                    update_vals['vehicle_name_id'] = job_card.vehicle_name_id.id
                if 'internal_service_id' in vals:
                    update_vals['internal_service_id'] = job_card.internal_service_id
                if 'external_service_id' in vals:
                    update_vals['external_service_id'] = job_card.external_service_id
                if 'currency_id' in vals:
                    update_vals['currency_id'] = job_card.currency_id.id

                if update_vals:
                    job_card.sale_order_id.with_context(from_job_card=True).write(update_vals)
        return res
