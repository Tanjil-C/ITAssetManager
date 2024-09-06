from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Asset

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']

class AssetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Asset model.
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    assigned_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Asset
        fields = ['id', 'name', 'purchase_date', 'asset_id', 'category', 'assigned_user', 'status']
