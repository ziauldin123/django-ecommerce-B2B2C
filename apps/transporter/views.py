from django.http import request
from django.shortcuts import render
from django.views.generic import TemplateView

from apps import transporter
from apps.vendor.models import Transporter
from apps.ordering.models import TransporterOrder
# Create your views here.
def TransporterAccount(request):

    transporter= Transporter.objects.get(email=request.user)
    orders=TransporterOrder.objects.filter(transporter=transporter)
    for i in orders:
        print(i.product.vendor)
    

    return render(request,'transporter_admin.html',{'transporter':transporter,'orders':orders})
      
  