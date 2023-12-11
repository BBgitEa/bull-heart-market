from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    preview = models.ImageField(upload_to ='uploads/previews/', blank=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="No description")
    price = models.FloatField(blank=True, default=0)
    wiki_link = models.TextField(blank=True, default="No wiki link")

    def __str__(self):
        return self.name
