from rest_framework import serializers
from djoser.serializers import UserSerializer, SendEmailResetSerializer
from djoser.conf import settings
from django.contrib.auth import get_user_model
from .models import Store
# Permission
import random
import string
# from .tasks import send_password_email_task


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
            'is_staff', 'is_superuser', 'is_active', 'fullname', "store", "last_login", 
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
        
        user.grant_permission(validated_data["permissions"], granted_by=request.user)
        
        send_password_email_task.delay(
            email=user.email,
            password=password,
            fullname=user.fullname,
            store_id=user.store.id
        )
        return user
    