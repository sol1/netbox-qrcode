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

class QRPrintConfigValue:
    """Represents a single print config field with layered sources (config, request)."""
    def __init__(self, name: str, field_type: type, config: str | None = None, request: str | None = None):
        self.name = name
        self.type = field_type
        self.config = config
        self.request = request
        self.grid = None
        self.scale = None

        self.__set_grid()

    @property
    def value(self):
        """Return the best (highest priority) value."""
        if self.request is not None:
            return self.request
        else:
            return self.config

    def __set_grid(self):
        if self.value is not None:
            if self.type == int:
                self.grid, self.scale = to_int(self.value)
            elif self.type == float:
                self.grid, self.scale = to_float(self.value)

    def __repr__(self):
        """Debug-friendly representation."""
        return f"<QRConfigValue {self.name}={self.value!r}>"

class QRPrintConfig:
    """Print configuration where only grid values are type-cast."""
    field_types: dict[str, type] = {
        'page_rows': int,
        'page_columns': int,
        'label_height': float,
        'label_width': float,
        'page_width': float,
        'page_height': float,
        'page_top_margin': float,
        'page_bottom_margin': float,
        'page_left_margin': float,
        'page_right_margin': float,
    }    

    def __init__(self, plugin_config: dict, request_get: dict):
        self._plugin_config = plugin_config
        self._request = request_get

        for name, ftype in self.field_types.items():
            plugin_value = plugin_config.get(name, None)
            request_value = self._request.get(name, None)
            config_value = QRPrintConfigValue(name, ftype, config=plugin_value, request=request_value)
            setattr(self, name, config_value)

    @property
    def scales(self):
        """Return a set of all detected scales in the config."""
        scales = set()
        for name in self.field_types:
            value: QRPrintConfigValue = getattr(self, name)
            if value.scale is not None:
                scales.add(value.scale)
        return scales

    def as_dict(self):
        return {name: getattr(self, name).value for name in self.field_types}

class QRCodePrintPreviewView(TemplateView):
    def get(self, request):
        # Get form config
        model_name = request.GET.get('model')
        pk_list = request.GET.getlist('pk')
        blank_spaces = int(request.GET.get('blank_spaces', 0))
        if not model_name or not pk_list:
            messages.error(request, "No objects selected for QR code preview.")
            return redirect('/')

        # Get plugin/form config
        plugin_config = settings.PLUGINS_CONFIG.get('netbox_qrcode', {})
        print_config = QRPrintConfig(plugin_config, request.GET)

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
                labelDesignNo=obj.id, 
                template_name='netbox_qrcode/qrcode3_print.html',
                label_width=print_config.label_width.value,
                label_height=print_config.label_height.value,
            )
            qr_html_list.append(qr_label_html)
        # Use GridMaker for grid positions
        num_objects = len(objects_ordered)


        # Check for mixed scales
        if len(print_config.scales) > 1:
            raise ValueError(f"Mixed scale exception: {print_config.scales}")

        grid = GridPosition(
            rows=print_config.page_rows.grid,
            columns=print_config.page_columns.grid,
            elements=num_objects,
            element_height=print_config.label_height.grid,
            element_width=print_config.label_width.grid,
            grid_width=print_config.page_width.grid - (print_config.page_left_margin.grid + print_config.page_right_margin.grid),
            grid_height=print_config.page_height.grid - (print_config.page_top_margin.grid + print_config.page_bottom_margin.grid)
        )

        # TODO: We shouldn't ever get here as this should be checked when the config is loaded
        if (grid.column_element_offset + grid.element_width) * grid.columns > print_config.page_width.grid \
            or (grid.row_element_offset + grid.element_height) * grid.rows > print_config.page_height.grid \
            or grid.column_element_offset < 0 \
            or grid.row_element_offset < 0:
            raise ValueError(
                f"Labels don't fit on the page: "
                f"grid width created = {(grid.column_element_offset + grid.element_width) * grid.columns}, "
                f"page width = {print_config.page_width.grid}, "
                f"grid width offset = {grid.column_element_offset}; "
                f"grid height created = {(grid.row_element_offset + grid.element_height) * grid.rows}, "
                f"page height = {print_config.page_height.grid}, "
                f"grid height offset = {grid.row_element_offset}; "
            )
            
        # add blank spaces so start label isn't 1, don't know what html will want to make this work
        # Create blank placeholders
        blank_objs = [None] * blank_spaces
        blank_qr = [''] * blank_spaces

        # Prepend blanks
        objects_ordered = blank_objs + objects_ordered
        qr_html_list = blank_qr + qr_html_list

        positions = [grid.getIndexByRow(i+1) for i in range(num_objects + blank_spaces)]
        # TODO: Multi page printing???
        per_page = grid.rows * grid.columns
        # Pass zipped objects, qr_html, and positions to template
        context = {
            'objects': zip(objects_ordered, qr_html_list, positions),            
            'grid': grid,
            'per_page': per_page,
            'page_rows': print_config.page_rows.value,
            'page_columns': print_config.page_columns.value,
            'page_width': print_config.page_width.value,
            'page_height': print_config.page_height.value,
            'page_top_margin': print_config.page_top_margin.value,
            'page_bottom_margin': print_config.page_bottom_margin.value,
            'page_left_margin': print_config.page_left_margin.value,
            'page_right_margin': print_config.page_right_margin.value,
            'label_height': print_config.label_height.value,
            'label_width': print_config.label_width.value,
            'row_range': range(1, grid.rows + 1),
            'col_range': range(1, grid.columns + 1),
            'scale': next(iter(print_config.scales)),
            'model': model,  # TODO: what is model?
            'blank_spaces': blank_spaces,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'netbox_qrcode/inc/preview_grid.html', context)
        
        return render(request, 'netbox_qrcode/print_preview.html', context)