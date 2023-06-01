from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import ProdukItem

# Create your views here.
def HomeListView(request):
    product_list = ProdukItem.objects.order_by('id')
    paginator = Paginator(product_list, 4)  # Menentukan jumlah item per halaman
    page = request.GET.get('page')  # Mengambil nomor halaman dari parameter GET
    products = paginator.get_page(page)  # Mendapatkan objek halaman produk
    return render(request, 'home.html', {'products': products})

def ShopView(request):
    products = 1
    return render(request, 'shop.html', {'products': products})

def ContactView(request):
    item = 1
    return render(request, 'contact.html', {'item': item})

