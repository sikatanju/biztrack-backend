from django.shortcuts import render
from django.db.models import Sum, Count

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Customer, Category, Product, Invoice, ProductImage
from .serializers import CustomerSerializer, CreateCustomerSerializer, CategorySerializer, CreateCategorySerializer, \
    ProductSerializer, CreateProductSerializer, InvoiceSerializer, CreateInvoiceSerializer, ProductImageSerializer

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
        return Product.objects.filter(user=self.request.user).prefetch_related('image')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateProductSerializer
        
        return ProductSerializer
    
    def get_serializer_context(self):
        return {'user': self.request.user}
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


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
        