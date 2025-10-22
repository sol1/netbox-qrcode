from netbox.plugins import PluginConfig
from .version import __version__ as version


class QRCodeConfig(PluginConfig):
    name = 'netbox_qrcode'
    verbose_name = 'qrcode'
    description = 'Generate QR codes for the objects'
    version = version
    author = 'Nikolay Yuzefovich'
    author_email = 'mgk.kolek@gmail.com'
    required_settings = []
    min_version = '4.3.0'
    max_version = '4.3.99'
    default_settings = {
	
        ################################## 
        # General Plugin
        'title': '',
        
        ################################## 
        # Text content
        'with_text': True,
        'text_location': 'right',
        'text_align_horizontal': 'left',
        'text_align_vertical': 'middle',
        
        # Text source (Option A)
        'text_fields': ['name', 'serial'],
        'custom_text': None,
        
        # Text source (Option B)
        'text_template': None,
        
        ################################## 
        # Font
        'font': 'TahomaBold',
        'font_size': '3mm',
        'font_weight': 'normal',
        'font_color': 'black',
        
        ################################## 
        # QR-Code
        'with_qr': True,
        
        # QR-Code alternative source
        'url_template': None,
        
        # QR-Code Image File
        'qr_version': 1,
        'qr_error_correction': 0,
        'qr_box_size': 4,
        'qr_border': 0,
        
        ################################## 
        # Label Layout
        
        # Label dimensions
        'label_qr_width': '12mm',
        'label_qr_height': '12mm',
        
        # Label edge
        'label_edge_top': '0mm',
        'label_edge_left': '1.5mm',
        'label_edge_right': '1.5mm',
        'label_edge_bottom': '0mm',    
        
        # Label QR code positioning
        'label_width': '64mm',
        'label_height': '32mm',
        'label_qr_text_distance': '1mm',

        # Print multiple labels per page 
        # page size
        'page_width': '210mm',
        'page_height': '297mm',
        'page_top_margin': '14mm',
        'page_bottom_margin': '14mm',
        'page_left_margin': '6mm',
        'page_right_margin': '6mm',
        'page_columns': 3,
        'page_rows': 9,
        # TODO: Do we need seperate label sizes for multi page printing?

        # Module-dependent configuration
        'device': {
            'text_fields': ['name', 'serial']
        },
        
        'rack': {
            'text_fields': ['name']
        },
        
        'cable': {
            'text_fields': [
                '_termination_a_device',
                'termination_a',
                '_termination_b_device',
                'termination_b',
                'a_terminations.device',
                'a_terminations',
                'b_terminations.device',
                'b_terminations'
                ]
        },
        
        'location': {
            'text_fields': ['name']
        },
        
        'powerfeed': {
            'text_fields': ['name']
        },
        
        'powerpanel': {
            'text_fields': ['name']
        },   

        'module': {
        },   
        'logo': '',
    }

config = QRCodeConfig # noqa E305
