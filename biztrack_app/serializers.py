from rest_framework import serializers

from .models import Customer, Category, Product, Invoice, InvoiceItem, ProductImage


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone']

class CreateCustomerSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()   

    def save(self, **kwargs):
        name = self.validated_data['name']
        email = self.validated_data['email']
        phone = self.validated_data['phone']
        customer = Customer.objects.create(name=name, email=email, phone=phone, user=self.context['user'])
        return customer
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class CreateCategorySerializer(serializers.Serializer):
    title = serializers.CharField()

    def save(self, **kwargs):
        title = self.validated_data['title']
        category = Category.objects.create(title=title, user=self.context['user'])
        return category


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        if ProductImage.objects.filter(product_id=product_id).exists():
            raise serializers.ValidationError("This product already has an image.")
        
        return ProductImage.objects.create(product_id=product_id, **validated_data)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    image = ProductImageSerializer(many=False, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'unit', 'category', 'image', 'created_at', 'updated_at']



class CreateProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    unit = serializers.IntegerField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    def save(self, **kwargs):
        title = self.validated_data['title']
        price = self.validated_data['price']
        unit = self.validated_data['unit']
        category = self.validated_data['category']
        return Product.objects.create(title=title, price=price, unit=unit, category=category, user=self.context['user'])


class SimpleProductSerializer(serializers.ModelSerializer):
    # image = ProductImageSerializer(many=False, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'category']


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'sale_price']


class CreateInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'sale_price']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    customer = CustomerSerializer()
    class Meta:
        model = Invoice
        fields = ['id', 'total', 'vat', 'discount', 'payable', 'customer', 'items', 'created_at', 'updated_at']


class CreateInvoiceSerializer(serializers.ModelSerializer):
    items = CreateInvoiceItemSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ['id', 'total', 'vat', 'discount', 'payable', 'customer', 'items', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        invoice = Invoice.objects.create(user=user, **validated_data)
        
        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)

        return invoice