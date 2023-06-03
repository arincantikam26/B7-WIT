from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import ProdukItem, OrderProdukItem, Order
from django.contrib import messages
from django.utils import timezone
from .forms import UserLoginForm, UserRegistrationForm

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

def OrderCartView(request):
    item = 1
    return render(request, 'order_summary.html', {'item': item})

def ProductDetailView(request, slug):
    products = get_object_or_404(ProdukItem, slug=slug)
    return render(request, 'product_detail.html', {'products': products, 'slug': slug})

def RegisterView(request):
    return HttpResponse('haloga')

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('toko:home-produk-list')
    else:
        form = UserLoginForm(request)

    return render(request, 'login.html', {'form': form})


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('toko:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/') 


def add_to_cart(request, slug):
    if request.user.is_authenticated:
        try:
            produk_item = get_object_or_404(ProdukItem, slug=slug)
            order_produk_item, _ = OrderProdukItem.objects.get_or_create(
                produk_item=produk_item,
                user=request.user,
                ordered=False
            )
            order_query = Order.objects.filter(user=request.user, ordered=False)
        
            if order_query.exists():
                order = order_query[0]
                if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                    order_produk_item.quantity += 1
                    order_produk_item.save()
                    pesan = f"Produk sudah diupdate menjadi: { order_produk_item.quantity }"
                    messages.info(request, pesan)
                    return redirect('toko:produk-detail', slug = slug)
                else:
                    order.produk_items.add(order_produk_item)
                    messages.success(request, 'Produk pilihanmu sudah ditambahkan')
                    return redirect('toko:produk-detail', slug = slug)
            else:
                tanggal_order = timezone.now()
                order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
                order.produk_items.add(order_produk_item)
                messages.success(request, 'Produk pilihanmu sudah ditambahkan')
                return redirect('toko:produk-detail', slug = slug)

        except OrderProdukItem.DoesNotExist:
            cart_item = OrderProdukItem.objects.create(user=request.user, slug=slug, quantity=quantity)
    else:
        return redirect('toko:login')
