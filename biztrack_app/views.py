from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Customer, Category
from .serializers import CustomerSerializer, CreateCustomerSerializer, CategorySerializer, CreateCategorySerializer

# Create your views here.
class CustomerViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCustomerSerializer

        return CustomerSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}
    

class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCategorySerializer
    
        return CategorySerializer
    
    def get_serializer_context(self):
        return {'user': self.request.user}
    