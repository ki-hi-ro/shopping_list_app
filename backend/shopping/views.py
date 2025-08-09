from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import List, Section, Item
from .serializers import ListSerializer, SectionSerializer, ItemSerializer

class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all().order_by("-created_at")
    serializer_class = ListSerializer

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    @action(detail=True, methods=["post"])
    def reorder(self, request, pk=None):
        # Body: { "item_ids": [3,1,2] } to set new positions within a section
        section = self.get_object()
        ids = request.data.get("item_ids", [])
        for idx, item_id in enumerate(ids):
            Item.objects.filter(id=item_id, section=section).update(position=idx)
        return Response({"status": "ok"})

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        # mark completed and optionally delete
        item = self.get_object()
        hard_delete = request.data.get("hard_delete", False)
        if hard_delete:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.completed = not item.completed
        item.save()
        return Response(ItemSerializer(item).data)