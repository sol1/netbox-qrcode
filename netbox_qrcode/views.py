from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.urls import reverse

from dcim.filtersets import (
    CableFilterSet,
    DeviceFilterSet,
    LocationFilterSet,
    ModuleFilterSet,
    PowerFeedFilterSet,
    PowerPanelFilterSet,
    RackFilterSet,
)
from dcim.forms import (
    CableFilterForm,
    DeviceFilterForm,
    LocationFilterForm,
    ModuleFilterForm,
    PowerFeedFilterForm,
    PowerPanelFilterForm,
    RackFilterForm,
)
from dcim.models import (
    Cable,
    Device,
    Location,
    Module,
    PowerFeed,
    PowerPanel,
    Rack,
)
from dcim.tables import (
    CableTable,
    DeviceTable,
    LocationTable,
    ModuleTable,
    PowerFeedTable,
    PowerPanelTable,
    RackTable,
)
from netbox.views import generic
from utilities.htmx import htmx_partial

from .template_content import (
    QRCode,
    DeviceQRCode,
    RackQRCode,
    CableQRCode,
    LocationQRCode,
    PowerFeedQRCode,
    PowerPanelQRCode,
    ModuleQRCode,
)
from .grid import GridPosition
from .utilities import to_int, to_float
from .form import PrintSettingsForm

import math

class QRCodePrintBaseView(generic.ObjectListView):
    bulk_url_name = None

    def get_template_name(self):
        return "netbox_qrcode/print.html"

    def get_extra_context(self, request, instance=None):
        context = super().get_extra_context(request, instance)
        context['return_url'] = reverse(
            f'{self.queryset.model._meta.app_label}:{self.queryset.model._meta.model_name}_list'
        )
        print(context['return_url'])
        return context

    def get(self, request):
        queryset = self.filterset(request.GET, self.queryset, request=request).qs

        table = self.get_table(queryset, request)
        table.columns.show('pk')
        table.columns.hide('actions')
        table.configure(request)

        if htmx_partial(request):
            if request.GET.get('embedded', False):
                table.embedded = True
            return render(request, 'htmx/table.html', {
                'table': table,
                'model': queryset.model,
            })

        return render(
            request,
            self.get_template_name(),
            context={
                'model': queryset.model,
                'table': table,
                'filter_form': self.filterset_form(request.GET),
                'template_url': self.get_template_name(),
                'bulk_action_url': reverse(self.bulk_url_name),
                'return_url': reverse(f'{self.queryset.model._meta.app_label}:{self.queryset.model._meta.model_name}_list'),
            },
        )

    def post(self, request):
        selected_pks = request.POST.getlist('pk')
        if not selected_pks:
            messages.error(request, "No objects selected for QR code printing.")
            return redirect(request.path)
        model_name = self.queryset.model._meta.model_name
        preview_url = reverse('plugins:netbox_qrcode:qrcode_print_preview')
        from urllib.parse import urlencode
        query = urlencode({'model': model_name, 'pk': selected_pks}, doseq=True)
        return redirect(f"{preview_url}?{query}")


class DeviceQRCodePrintView(QRCodePrintBaseView):
    queryset = Device.objects.all()
    filterset = DeviceFilterSet
    filterset_form = DeviceFilterForm
    table = DeviceTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_device'
    print_settings_form = PrintSettingsForm


class RackQRCodePrintView(QRCodePrintBaseView):
    queryset = Rack.objects.all()
    filterset = RackFilterSet
    filterset_form = RackFilterForm
    table = RackTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_rack'
    print_settings_form = PrintSettingsForm


class CableQRCodePrintView(QRCodePrintBaseView):
    queryset = Cable.objects.all()
    filterset = CableFilterSet
    filterset_form = CableFilterForm
    table = CableTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_cable'
    print_settings_form = PrintSettingsForm


class LocationQRCodePrintView(QRCodePrintBaseView):
    queryset = Location.objects.all()
    filterset = LocationFilterSet
    filterset_form = LocationFilterForm
    table = LocationTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_location'
    print_settings_form = PrintSettingsForm


class PowerFeedQRCodePrintView(QRCodePrintBaseView):
    queryset = PowerFeed.objects.all()
    filterset = PowerFeedFilterSet
    filterset_form = PowerFeedFilterForm
    table = PowerFeedTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_powerfeed'
    print_settings_form = PrintSettingsForm


class PowerPanelQRCodePrintView(QRCodePrintBaseView):
    queryset = PowerPanel.objects.all()
    filterset = PowerPanelFilterSet
    filterset_form = PowerPanelFilterForm
    table = PowerPanelTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_powerpanel'
    print_settings_form = PrintSettingsForm


class ModuleQRCodePrintView(QRCodePrintBaseView):
    queryset = Module.objects.all()
    filterset = ModuleFilterSet
    filterset_form = ModuleFilterForm
    table = ModuleTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_module'
    print_settings_form = PrintSettingsForm

def extract_mm(value, default):
    try:
        if isinstance(value, str) and value.endswith('mm'):
            return float(value.rstrip('mm'))
        return float(value)
    except (TypeError, ValueError):
        return default

class QRCodePrintPreviewView(TemplateView):
    def get(self, request):
        model_name = request.GET.get('model')
        pk_list = request.GET.getlist('pk')
        if not model_name or not pk_list:
            messages.error(request, "No objects selected for QR code preview.")
            return redirect('/')
        model_map = {
            'device': Device,
            'rack': Rack,
            'cable': Cable,
            'location': Location,
            'powerfeed': PowerFeed,
            'powerpanel': PowerPanel,
            'module': Module,
        }
        extension_map = {
            'device': DeviceQRCode,
            'rack': RackQRCode,
            'cable': CableQRCode,
            'location': LocationQRCode,
            'powerfeed': PowerFeedQRCode,
            'powerpanel': PowerPanelQRCode,
            'module': ModuleQRCode,
        }
        model = model_map.get(model_name)
        extension_class = extension_map.get(model_name)
        plugin_config = settings.PLUGINS_CONFIG.get('netbox_qrcode', {})
        if not model or not extension_class:
            messages.error(request, "Invalid model for QR code preview.")
            return redirect('/')
        objects = list(model.objects.filter(pk__in=pk_list))
        objects_ordered = [next(obj for obj in objects if str(obj.pk) == pk) for pk in pk_list if any(str(obj.pk) == pk for obj in objects)]
        # Generate QR code HTML for each object (only QR code and label, no extra card or controls)
        qr_html_list = []
        for obj in objects_ordered:
            qr_label_html = QRCode.Create_SubPluginContent(
                extension_class(context={'object': obj, 'config': plugin_config, 'request': request}),
                obj.id, template_name='netbox_qrcode/qrcode3_print.html'
            )
            qr_html_list.append(qr_label_html)
        # Use GridMaker for grid positions
        num_objects = len(objects_ordered)
        grid_values = {}
        scales = set()

        # Define field groups
        int_fields = ['page_rows', 'page_columns']
        float_fields = [
            'label_height', 
            'label_width', 
            'page_width', 
            'page_height', 
            'page_top_margin',
            'page_bottom_margin',
            'page_left_margin',
            'page_right_margin',
        ]

        # Process int fields
        for var in int_fields:
            grid_values[var], scale = to_int(plugin_config.get(var))
            if scale is not None:
                scales.add(scale)

        # Process float fields
        for var in float_fields:
            grid_values[var], scale = to_float(plugin_config.get(var))
            if scale is not None:
                scales.add(scale)

        # Check for mixed scales
        if len(scales) > 1:
            raise ValueError(f"Mixed scale exception: {scales}")

        grid = GridPosition(
            rows=grid_values['page_rows'],
            columns=grid_values['page_columns'],
            elements=num_objects,
            element_height=grid_values['label_height'],
            element_width=grid_values['label_width'],
            grid_width=grid_values['page_width'] - (grid_values['page_left_margin'] + grid_values['page_right_margin']),
            grid_height=grid_values['page_height'] - (grid_values['page_top_margin'] + grid_values['page_bottom_margin'])
        )

        # TODO: We shouldn't ever get here as this should be checked when the config is loaded
        if (grid.column_element_offset + grid.element_width) * grid.columns > grid_values['page_width'] \
            or (grid.row_element_offset + grid.element_height) * grid.rows > grid_values['page_height'] \
            or grid.column_element_offset < 0 \
            or grid.row_element_offset < 0:
            raise ValueError(
                f"Labels don't fit on the page: "
                f"grid width created = {(grid.column_element_offset + grid.element_width) * grid.columns}, "
                f"page width = {grid_values['page_width']}, "
                f"grid width offset = {grid.column_element_offset}; "
                f"grid height created = {(grid.row_element_offset + grid.element_height) * grid.rows}, "
                f"page height = {grid_values['page_height']}, "
                f"grid height offset = {grid.row_element_offset}; "
            )
            
        # add blank spaces so start label isn't 1, don't know what html will want to make this work
        blank_spaces = 2
        # Create blank placeholders
        blank_objs = [None] * blank_spaces
        blank_qr = [''] * blank_spaces

        # Prepend blanks
        objects_ordered = blank_objs + objects_ordered
        qr_html_list = blank_qr + qr_html_list

        positions = [grid.getIndexByRow(i+1) for i in range(num_objects + blank_spaces)]
        print(positions)
        # TODO: Multi page printing???
        per_page = grid.rows * grid.columns
        print(per_page)
        # Pass zipped objects, qr_html, and positions to template
        return render(request, 'netbox_qrcode/print_preview.html', {
            'objects': zip(objects_ordered, qr_html_list, positions),            
            'grid': grid,
            'per_page': per_page,
            'page_width': plugin_config.get('page_width'),
            'page_height': plugin_config.get('page_height'),
            'page_top_margin': plugin_config.get('page_top_margin'),
            'page_bottom_margin': plugin_config.get('page_bottom_margin'),
            'page_left_margin': plugin_config.get('page_left_margin'),
            'page_right_margin': plugin_config.get('page_right_margin'),
            'row_range': range(1, grid.rows + 1),
            'col_range': range(1, grid.columns + 1),
            'scale': next(iter(scales)),
            'model': model,  # TODO: what is model?
        })