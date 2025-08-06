from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from netbox.plugins import PluginTemplateExtension
from packaging import version

from .template_content_functions import (config_for_modul, create_QRCode,
                                         create_text, create_url)

# ******************************************************************************************
# Contains the main functionalities of the plugin and thus creates the content for the 
# individual modules, e.g: Device, Rack etc.
# ******************************************************************************************

##################################
# Class for creating the plugin content
class QRCode(PluginTemplateExtension):

    ##################################          
    # Creates a plug-in view for a label.
    # --------------------------------
    # Parameter:
    #   labelDesignNo: Which label design should be loaded.
    def Create_SubPluginContent(self, labelDesignNo):
        
        thisSelf = self

        obj = self.context['object'] # An object of the type Device, Rack etc.

        # Config suitable for the module
        config = config_for_modul(thisSelf, labelDesignNo)

        # Abort if no config data. 
        if config is None: 
            return '' 

        # Get URL for QR code
        url = create_url(thisSelf, config, obj)

        # Create a QR code
        qrCode = create_QRCode(url, config)

        # Create the text for the label if required.
        text = create_text(config, obj, qrCode)

        # Create plugin using template
        try:
            if version.parse(settings.RELEASE.version).major >= 3:

                render = self.render(
                    'netbox_qrcode/qrcode3.html', extra_context={
                                                                    'title': config.get('title'),
                                                                    'labelDesignNo': labelDesignNo,
                                                                    'qrCode': qrCode, 
                                                                    'with_text': config.get('with_text'),
                                                                    'text': text,
                                                                    'text_location': config.get('text_location'),
                                                                    'text_align_horizontal': config.get('text_align_horizontal'),
                                                                    'text_align_vertical': config.get('text_align_vertical'),
                                                                    'font': config.get('font'),
                                                                    'font_size': config.get('font_size'),
                                                                    'font_weight': config.get('font_weight'),
                                                                    'font_color': config.get('font_color'),
                                                                    'with_qr': config.get('with_qr'),
                                                                    'label_qr_width': config.get('label_qr_width'),
                                                                    'label_qr_height': config.get('label_qr_height'),
                                                                    'label_qr_text_distance': config.get('label_qr_text_distance'),
                                                                    'label_width': config.get('label_width'),
                                                                    'label_height': config.get('label_height'), 
                                                                    'label_edge_top': config.get('label_edge_top'),
                                                                    'label_edge_left': config.get('label_edge_left'),
                                                                    'label_edge_right': config.get('label_edge_right'),
                                                                    'label_edge_bottom': config.get('label_edge_bottom')
                                                                }

                )
            
                return render
            else:
                # Versions 1 and 2 are no longer supported.
                return self.render(
                    'netbox_qrcode/qrcode.html', extra_context={'image': qrCode}
                )
        except ObjectDoesNotExist:
            return ''

    ##################################
    # Create plugin content
    # - First, a plugin view is created for the first label.
    # - If there are further configuration entries for the object/model (e.g. device, rack etc.),
    #   further label views are also created as additional plugin views.
    def Create_PluginContent(self):

        # First Plugin Content
        pluginContent = QRCode.Create_SubPluginContent(self, 1) 

        # Check whether there is another configuration for the object, e.g. device, rack, etc.
        # Support up to 10 additional label configurations (objectName_2 to ..._10) per object (e.g. device, rack, etc.).

        config = self.context['config'] # Django configuration

        for i in range(2, 11):

            configName = self.models[0].replace('dcim.', '') + '_' + str(i)
            obj_cfg = config.get(configName) # Load configuration for additional label if possible.

            if(obj_cfg):
                pluginContent += QRCode.Create_SubPluginContent(self, i) # Add another plugin view
            else:
                break
        
        return pluginContent

##################################
# The following section serves to integrate the plugin into Netbox Core.
        
# Class for creating a QR code for the model: Device
class DeviceQRCode(QRCode):
    models = ('dcim.device',)

    def right_page(self):
        return self.Create_PluginContent()

# Class for creating a QR code for the model: Rack
class RackQRCode(QRCode):
    models = ('dcim.rack',)

    def right_page(self):
        return self.Create_PluginContent()

# Class for creating a QR code for the model: Cable
class CableQRCode(QRCode):
    models = ('dcim.cable',)

    def left_page(self):
        return self.Create_PluginContent()

# Class for creating a QR code for the model: Location
class LocationQRCode(QRCode):
    models = ('dcim.location',)

    def left_page(self):
        return self.Create_PluginContent()

# Class for creating a QR code for the model: Power Feed
class PowerFeedQRCode(QRCode):
    models = ('dcim.powerfeed',)

    def right_page(self):
        return self.Create_PluginContent()

# Class for creating a QR code for the model: Power Panel
class PowerPanelQRCode(QRCode):
    models = ('dcim.powerpanel',)

    def right_page(self):
        return self.Create_PluginContent()

# Class for dcim.module
class ModuleQRCode(QRCode):
    models = ('dcim.module',)

    def right_page(self):
        return self.Create_PluginContent()

##################################
# Other plugins support

# Commenting out (for now) - make this work on core models first.
# Class for creating a QR code for the Plugin: Netbox-Inventory (https://github.com/ArnesSI/netbox-inventory)
class Plugin_Netbox_Inventory(QRCode):
   models = ('netbox_inventory.asset',) # Info for Netbox in which model the plugin should be integrated.

   def right_page(self):
       return self.Create_PluginContent()

# Connects Netbox Core with the plug-in classes
# Removed , Plugin_Netbox_Inventory]

###################################
# List button for printing QR codes

class PrintQRCodesButton(PluginTemplateExtension):
    models = (
        'dcim.device',
        'dcim.rack',
        'dcim.cable',
        'dcim.location',
        'dcim.powerfeed',
        'dcim.powerpanel',
        'dcim.module',
    )

    def list_buttons(self):
        request = self.context.get('request')
        if request and request.resolver_match.view_name.startswith('plugins:netbox_qrcode:qrcode_print_'):
            return ''
        model_to_url = {
            'dcim.device': 'plugins:netbox_qrcode:qrcode_print_device',
            'dcim.rack': 'plugins:netbox_qrcode:qrcode_print_rack',
            'dcim.cable': 'plugins:netbox_qrcode:qrcode_print_cable',
            'dcim.location': 'plugins:netbox_qrcode:qrcode_print_location',
            'dcim.powerfeed': 'plugins:netbox_qrcode:qrcode_print_powerfeed',
            'dcim.powerpanel': 'plugins:netbox_qrcode:qrcode_print_powerpanel',
            'dcim.module': 'plugins:netbox_qrcode:qrcode_print_module',
            'netbox_inventory.asset': 'plugins:netbox_qrcode:qrcode_print_asset',
        }
        model = None
        if self.context.get('object'):
            model = self.context['object'].__class__
        if not model:
            return ''
        model_label = f"{model._meta.app_label}.{model._meta.model_name}"
        print_url_name = model_to_url.get(model_label)
        if not print_url_name:
            return ''
        return self.render('netbox_qrcode/inc/print_qrcodes_button.html', extra_context={
            'print_url': reverse(print_url_name)
        })

template_extensions = [
    DeviceQRCode,
    ModuleQRCode,
    RackQRCode,
    CableQRCode,
    LocationQRCode,
    PowerFeedQRCode,
    PowerPanelQRCode,
    Plugin_Netbox_Inventory,
    PrintQRCodesButton,
]