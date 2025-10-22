from netbox.plugins import PluginMenu, PluginMenuItem

from .utilities import plugin_inventory_installed

menu_items = [
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_device',
        link_text='Devices',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_rack',
        link_text='Racks',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_cable',
        link_text='Cables',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_location',
        link_text='Locations',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_powerfeed',
        link_text='Power Feeds',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_powerpanel',
        link_text='Power Panels',
    ),
    PluginMenuItem(
        link='plugins:netbox_qrcode:qrcode_print_module',
        link_text='Modules',
    ),
]

menu = PluginMenu(
    label='QR Code',
    groups=(('QR Code Bulk Printing', menu_items),),
    icon_class='mdi mdi-qrcode',
)

if plugin_inventory_installed():
    menu_items.append(
        PluginMenuItem(
            link='plugins:netbox_qrcode:qrcode_print_asset',
            link_text='Assets',
        )
    )