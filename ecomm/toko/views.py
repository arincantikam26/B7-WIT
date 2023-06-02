from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import ProdukItem
from django.contrib import messages
from django.utils import timezone

# Create your views here.
def HomeListView(request):
    product_list = ProdukItem.objects.order_by('id')
    paginator = Paginator(product_list, 12)  # Menentukan jumlah item per halaman
    page = request.GET.get('page')  # Mengambil nomor halaman dari parameter GET
    products = paginator.get_page(page)  # Mendapatkan objek halaman produk
    return render(request, 'home.html', {'products': products})

def ShopView(request):
    products = 1
    return render(request, 'shop.html', {'products': products})

def ContactView(request):
    item = 1
    return render(request, 'contact.html', {'item': item})

def ProductDetailView(request, slug):
    products = get_object_or_404(ProdukItem, slug=slug)
    return render(request, 'product_detail.html', {'products': products, 'slug': slug})


