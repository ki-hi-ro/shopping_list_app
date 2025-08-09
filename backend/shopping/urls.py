from django.urls import path, include
from rest_framework import routers
from .views import ListViewSet, SectionViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register(r'lists', ListViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]