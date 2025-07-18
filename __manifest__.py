# -*- coding: utf-8 -*-
###############################################################################
{
    'name': 'Car Detailing Shop',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'A Complete Vehicle Detailing Service Operations & Reports',
    'description': """This module helps to manage vehicle detailing services with
     great ease. Keep track of everything, like vehicle owner details,
     Works assigned, Bill details of service provided, etc.""",
    'author': 'Jo',
    'company': 'Jo',
    'maintainer ': 'Jo',
    'depends': ['stock', 'account', 'sale'],
    'data': [
        'security/car_detailing_service.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'report/report.xml',
        'report/customer_job_card_report.xml',
        'views/menus.xml',
        'views/register_customer_views.xml',
        'views/service_feedback_views.xml',
        'views/inherit_sale_order_view.xml',
        'views/external_services_views.xml',
        'views/internal_services_views.xml',
        'views/service_products_views.xml',
        'views/res_config_settings_views.xml',
        'views/service_staff_views.xml',
        'views/staff_positions_views.xml',
        'views/detailing_vehicle_views.xml',
        'views/vehicle_tag_views.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'wizard/whatsapp_send_message_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'car_detailing_service/static/src/js/image_preview_widget.js',
            'car_detailing_service/static/src/xml/widget_image_preview.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
