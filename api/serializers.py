from rest_framework import serializers
from djoser.serializers import UserSerializer, SendEmailResetSerializer
from djoser.conf import settings
from django.contrib.auth import get_user_model
from .models import Store, Product, StockEntry, StockExit, StockEntryItem, StockExitItem, Supplier, Warehouse, Customer, Account
# Permission
import random
import string
# from .tasks import send_password_email_task
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    username_field = 'username'
    token_class = RefreshToken
    store_name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        store_name = attrs.get('store_name')
        
        user = authenticate(username=username, password=password, store_name=store_name)

        if not user:
            raise serializers.ValidationError(_('No active account found with the given credentials'))

        if not user.is_active:
            raise serializers.ValidationError(_('no_active_account'))

        refresh =self.get_token(user)
        access = refresh.access_token 

        print(f"""For DebugPurpose in apps/authentications/serializers
                refrseh: {refresh}
                access: {access}
                user: {user}
              """)
        if not refresh or not access:
            raise serializers.ValidationError(_('Token generation failed'))

        return {
            'refresh': str(refresh),
            'access': str(access),
            'user': user
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if not token:
            raise ValueError("Token generation failed")
        token['phone'] = user.phone  # Custom claim
        return token

class SotoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', "description"]
 
# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = ["code", "label", "description"]
        
User = get_user_model()
class CustomUserSerializer(UserSerializer):
    # permissions = PermissionSerializer(many=True)
    store = SotoreSerializer(many=False)
    # store_contexts = UserSotoreSerializer(many=True)
    # current_store_id = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'is_staff', 'is_superuser', 'is_active', 'fullname', "store", "email", "phone", "last_login", 
            # 'permissions'
        )


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    fullname = serializers.CharField()
    # permissions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.store:
            raise serializers.ValidationError("Vous devez être lié à un store pour créer un utilisateur.")
        
        # if not attrs.get("email") and not attrs.get("phone_number"):
        #     raise serializers.ValidationError("Email ou numéro de téléphone requis.")
        # return attrs
    
    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(random.choice(characters) for _ in range(length))

    def create(self, validated_data):
        request = self.context['request']
        store = request.user.store

        password=self.generate_random_password()
        
        user = User.objects.create_user(
            store=store,
            email=validated_data['email'],
            phone_number=validated_data['phone'],
            fullname=validated_data.get('fullname', ''),
            password=password,
        )
        
        # user.grant_permission(validated_data["permissions"], granted_by=request.user)
        
        # send_password_email_task.delay(
        #     email=user.email,
        #     password=password,
        #     fullname=user.fullname,
        #     store_id=user.store.id
        # )
        return user


# Serializers pour les modèles de gestion de stock
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['store']


class ProductSerializer(serializers.ModelSerializer):
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        exclude = ['store']
        
    
    def get_total_stock(self, obj):
        # Calculer le stock total basé sur les entrées et sorties
        from django.db.models import Sum
        entries = StockEntryItem.objects.filter(product=obj).aggregate(
            total=Sum('quantity'))['total'] or 0
        exits = StockExitItem.objects.filter(product=obj).aggregate(
            total=Sum('quantity'))['total'] or 0
        return entries - exits


class StockEntryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockEntryItem
        fields = ['id', 'product', 'product_name', 'quantity', 'purchase_price', 'total_price']


class StockEntrySerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.fullname', read_only=True)
    items = StockEntryItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockEntry
        fields = '__all__'


class StockExitItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockExitItem
        fields = ['id', 'product', 'product_name', 'quantity', 'sale_price', 'total_price']


class StockExitSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.fullname', read_only=True)
    items = StockExitItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StockExit
        fields = '__all__'
    
    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.name
        return obj.customer_name or 'Client anonyme'


# Serializers pour les formulaires
class StockEntryFormSerializer(serializers.Serializer):
    supplier = serializers.IntegerField()
    warehouse = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class StockExitFormSerializer(serializers.Serializer):
    customer = serializers.IntegerField(required=False)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    warehouse = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'balance', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_name(self, value):
        """Vérifier l'unicité du nom du compte par magasin"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.store:
            if Account.objects.filter(
                name=value, 
                store=request.user.store
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise serializers.ValidationError("Un compte avec ce nom existe déjà.")
        return value
    