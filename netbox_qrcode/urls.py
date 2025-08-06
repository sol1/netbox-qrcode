from django.urls import path

from . import views

urlpatterns = (
    path('print/devices/', views.DeviceQRCodePrintView.as_view(), name='qrcode_print_device'),
)