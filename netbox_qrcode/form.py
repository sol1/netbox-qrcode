from django import forms
from django.conf import settings
from utilities.forms.rendering import FieldSet



class PrintSettingsForm(forms.Form):
    plugin_config = settings.PLUGINS_CONFIG.get('netbox_qrcode', {})
    fieldsets = (
        FieldSet(
                "page_width",
                "page_height",
                name="Page Size"
        ),
        FieldSet(
                "page_top_margin",
                "page_bottom_margin",
                "page_left_margin",
                "page_right_margin",
                name="Page Margins"
        ),
        FieldSet(
                "page_columns",
                "page_rows",
                "start_position",
                name="Labels"
        ),
    )

    page_width = forms.CharField(
        label="Page Width",
        initial=plugin_config.get('page_width', ''),
        required=False,
        type=str
        help_text="Width of the page for printing QR codes."
    )
    page_height = forms.CharField(
        label="Page Height",
        initial=plugin_config.get('page_height', ''),
        required=False,
        type=str
        help_text="Height of the page for printing QR codes."
    )
    page_top_margin = forms.CharField(
        label="Top Margin",
        initial=plugin_config.get('page_top_margin', ''),
        required=False,
        type=str
        help_text="Top margin of the page for printing QR codes."
    )
    page_bottom_margin = forms.CharField(
        label="Bottom Margin",
        initial=plugin_config.get('page_bottom_margin', ''),
        required=False,
        type=str
        help_text="Bottom margin of the page for printing QR codes."
    )
    page_left_margin = forms.CharField(
        label="Left Margin",
        initial=plugin_config.get('page_left_margin', ''),
        required=False,
        type=str,
        help_text="Left margin of the page for printing QR codes."
    )
    page_right_margin = forms.CharField(
        label="Right Margin",
        initial=plugin_config.get('page_right_margin', ''),
        required=False,
        type=str,
        help_text="Right margin of the page for printing QR codes."
    )
    page_columns = forms.CharField(
        label="Columns",
        initial=plugin_config.get('page_columns', ''),
        required=False,
        type=int,
        help_text="Number of columns of QR code labels per page."
    )
    page_rows = forms.CharField(
        label="Rows",
        initial=plugin_config.get('page_rows', ''),
        required=False,
        type=int,
        help_text="Number of rows of QR code labels per page."
    )
    start_position = forms.CharField(
        label="Start Position",
        initial=plugin_config.get('start_position', ''),
        required=False,
        type=int,
        help_text="Starting position for QR code labels on the page."
    )
