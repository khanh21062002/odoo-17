{
    'name': "Quản lý Kho Sim Thăng Long",
    'summary': """
        Quản lý kho Sim Thăng Long""",

    'description': """

    """,

    'author': "DTH",
    'website': "https://dth.com.vn/",
    'live_test_url': "https://dth.com.vn/",
    'category': 'Warehouse',
    'version': '0.1.1',
    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        #data
        'data/province.xml',
        'data/district.xml',
        'data/ward.xml',
        'data/installment_period.xml',
        'data/prepay_amount.xml',
        'data/telecom_supplier.xml',
        'data/sim_categoty.xml',
        'data/service_cron.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sim_maker_views.xml',
        'views/res_config_settings_views.xml',
        'views/mobile_package_views.xml',
        'views/telecom_supplier_views.xml',
        'views/sim_category_views.xml',
        'views/sim_warehouse_views.xml',
        'report_models/sim_search_history_views.xml',
        'report_models/sim_number_upload_history_views.xml',
        'report_models/sim_number_upload_history_detail_views.xml',
        'report_models/sim_number_upload_monthly_views.xml',
        'report_models/report_expired_license_plates_views.xml',
        'report_models/report_competitor_comparison_views.xml',
        'report_models/report_low_quality_numbers_views.xml',
        'views/comment_history_views.xml',
        'views/sim_upload_history_views.xml',
        'views/res_users_views.xml',
        'views/configuration_satellite_web_views.xml',
        'views/information_sim_views.xml',
        'views/menu.xml',
        'views/sim_warehouse_spa_templates.xml',
        'wizard/sim_maker_rating_views.xml',
        'wizard/change_status_sim_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            'dth_stock/static/src/fields/**/*',
            'dth_stock/static/src/scss/*.scss',
            'dth_stock/static/src/js/*.js',
            'dth_stock/static/src/xml/*.xml',
        ],
        'dth_stock.assets_backend': [
            'dth_stock/static/src/assets/*.js',
            'dth_stock/static/src/assets/*.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
