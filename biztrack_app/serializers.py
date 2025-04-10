from rest_framework import serializers

from .models import Customer, Category


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