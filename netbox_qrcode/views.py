from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from dcim.filtersets import DeviceFilterSet
from dcim.forms import DeviceFilterForm
from dcim.models import Device
from dcim.tables import DeviceTable
from netbox.views import generic
from utilities.htmx import htmx_partial


class QRCodePrintBaseView(generic.ObjectListView):
    bulk_url_name = None

    def get_template_name(self):
        return "netbox_qrcode/print.html"

    def get_extra_context(self, request, instance=None):
        context = super().get_extra_context(request, instance)
        context['return_url'] = reverse(
            f'{self.queryset.model._meta.app_label}:{self.queryset.model._meta.model_name}_list'
        )
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
        objects = self.queryset.model.objects.filter(pk__in=selected_pks)
        if not objects:
            messages.error(request, "No objects selected for QR code printing.")
            return redirect(request.path)
        # Implement QR code printing logic here
        messages.success(request, f"Prepared {objects.count()} objects for QR code printing.")
        return redirect(reverse(f'{self.queryset.model._meta.app_label}:{self.queryset.model._meta.model_name}_list'))


class DeviceQRCodePrintView(QRCodePrintBaseView):
    queryset = Device.objects.all()
    filterset = DeviceFilterSet
    filterset_form = DeviceFilterForm
    table = DeviceTable
    bulk_url_name = 'plugins:netbox_qrcode:qrcode_print_device'