from django.db import models

class List(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Section(models.Model):
    list = models.ForeignKey(List, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.title} ({self.list.name})"

class Item(models.Model):
    section = models.ForeignKey(Section, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    qty = models.CharField(max_length=50, blank=True, default="")
    position = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.name