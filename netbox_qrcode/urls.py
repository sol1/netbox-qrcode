from django.urls import path

from . import views

urlpatterns = (
    path('print/devices/', views.DeviceQRCodePrintView.as_view(), name='qrcode_print_device'),
    path('print/racks/', views.RackQRCodePrintView.as_view(), name='qrcode_print_rack'),
    path('print/cables/', views.CableQRCodePrintView.as_view(), name='qrcode_print_cable'),
    path('print/locations/', views.LocationQRCodePrintView.as_view(), name='qrcode_print_location'),
    path('print/power-feeds/', views.PowerFeedQRCodePrintView.as_view(), name='qrcode_print_powerfeed'),
    path('print/power-panels/', views.PowerPanelQRCodePrintView.as_view(), name='qrcode_print_powerpanel'),
    path('print/modules/', views.ModuleQRCodePrintView.as_view(), name='qrcode_print_module'),
    path('print/assets/', views.AssetQRCodePrintView.as_view(), name='qrcode_print_asset'),

    path('print/preview/', views.QRCodePrintPreviewView.as_view(), name='qrcode_print_preview'),
)