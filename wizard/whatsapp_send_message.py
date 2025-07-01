# -*- coding: utf-8 -*-
#############################################################################
from odoo import fields, models

class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'whatsapp.send.message'
    _description = "Whatsapp Wizard"

    customer_id = fields.Many2one('register.customer', string="Customer")
    mobile = fields.Char(related='customer_id.mobile_no', required=True)
    message = fields.Text(string="Message", required=True)

    def action_send_message(self):
        """This method is called to send the WhatsApp message using the
         provided details."""
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone=" +
                       self.customer_id.mobile_no + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
