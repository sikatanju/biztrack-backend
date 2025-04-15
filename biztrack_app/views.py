from django.shortcuts import render
from django.db.models import Sum, Count

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Customer, Category, Product, Invoice, InvoiceItem
from .serializers import CustomerSerializer, CreateCustomerSerializer, CategorySerializer, CreateCategorySerializer, \
    ProductSerializer, CreateProductSerializer, InvoiceSerializer, CreateInvoiceSerializer

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
    
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
    #     return super().perform_create(serializer)
    

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
    

class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductSerializer
        
        return ProductSerializer
    
    def get_serializer_context(self):
        return {'user': self.request.user}


class InvoiceViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).select_related('customer').prefetch_related('items__product').all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateInvoiceSerializer 
        
        return InvoiceSerializer

    def perform_create(self, serializer):
        serializer.save()


@api_view()
def summary_view(request):
    product_count = Product.objects.filter(user=request.user).count()
    category_count = Category.objects.filter(user=request.user).count()
    customer_count = Customer.objects.filter(user=request.user).count()
    invoice = Invoice.objects.filter(user=request.user).aggregate(count=Count('id'), total_sum=Sum('total'), vat_sum=Sum('vat'), payable_sum=Sum('payable'))
    return Response(
        {'product': product_count,
         'category': category_count,
         'customer': customer_count,
         'invoice': invoice['count'],
         'total': '{0:.2f}'.format(invoice['total_sum']),
         'vat': '{0:.2f}'.format(invoice['vat_sum']),
         'payable': '{0:.2f}'.format(invoice['payable_sum']) 
        }
    )
        