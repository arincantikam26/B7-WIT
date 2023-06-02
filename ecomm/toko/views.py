from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import ProdukItem
from .forms import RegistrationForm

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


def LoginUser(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # berhasil login -> home yang sudah bisa belanja
            form.save()
            return redirect('login')  # Ganti dengan URL halaman login yang sesuai
    else:
        # kalo belum maka ulangi halaman form
        form = RegistrationForm()
    
    return render(request, 'loginuser.html', {'form': form})

def TestView(request):
    item = 1
    return render(request, 'test.html', {'item': item})

