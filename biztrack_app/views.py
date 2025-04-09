from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Customer
from .serializers import CustomerSerializer, CreateCustomerSerializer

# Create your views here.
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCustomerSerializer
        else:
            return CustomerSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}
    