from django.shortcuts import render, HttpResponse
from .models import Category
# Create your views here.

def index(request):
    categories = Category.objects.all()
    count = categories.count()
    return render(request, "index.html", {'categories': categories, 'count': count})