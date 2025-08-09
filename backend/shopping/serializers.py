from rest_framework import serializers
from .models import List, Section, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "section", "name", "qty", "position", "completed", "created_at"]

class SectionSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "list", "title", "position", "items"]

class ListSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ["id", "name", "created_at", "sections"]