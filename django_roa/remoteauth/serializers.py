from rest_framework import serializers
from .models import Group, Permission, User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
