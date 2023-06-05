from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views import generic
from .models import ProdukItem, OrderProdukItem, Order, AlamatPengiriman
from .forms import UserLoginForm, UserRegistrationForm, CheckoutForm

# Create your views here.

# View
def HomeListView(request):
    product_list = ProdukItem.objects.all()
    paginator = Paginator(product_list, 8)  # Menentukan jumlah item per halaman
    page = request.GET.get('page')  # Mengambil nomor halaman dari parameter GET
    products = paginator.get_page(page)  # Mendapatkan objek halaman produk

    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

def ShopView(request):
    products = 1
    return render(request, 'shop.html', {'products': products})

def ContactView(request):
    return render(request, 'contact.html')

def OrderCartView(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
            'keranjang': order
        }
        template_name = 'order_summary.html'
        return render(request, template_name, context)
    except ObjectDoesNotExist:
        messages.error(request, 'Tidak ada pesanan yang aktif')
        return redirect('/')

def ProductDetailView(request, slug):
    products = get_object_or_404(ProdukItem, slug=slug)
    context = {
        'products': products,
        'slug': slug,
    }

    return render(request, 'product_detail.html', context)

# Checkout
class CheckoutView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.produk_items.count() == 0:
                messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        context = {
            'form': form,
            'keranjang': order,
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                alamat_1 = form.cleaned_data.get('alamat_1')
                alamat_2 = form.cleaned_data.get('alamat_2')
                negara = form.cleaned_data.get('negara')
                kode_pos = form.cleaned_data.get('kode_pos')
                opsi_pembayaran = form.cleaned_data.get('opsi_pembayaran')
                alamat_pengiriman = AlamatPengiriman(
                    user=self.request.user,
                    alamat_1=alamat_1,
                    alamat_2=alamat_2,
                    negara=negara,
                    kode_pos=kode_pos,
                )

                alamat_pengiriman.save()
                order.alamat_pengiriman = alamat_pengiriman
                order.save()
                if opsi_pembayaran == 'P':
                    return redirect('toko:payment', payment_method='paypal')
                else:
                    return redirect('toko:payment', payment_method='stripe')

            messages.warning(self.request, 'Gagal checkout')
            return redirect('toko:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('toko:order-summary')
# User
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

# Cart 
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
            cart_item = OrderProdukItem.objects.create(user=request.user, slug=slug)
    else:
        return redirect('toko:login')

def remove_from_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_query = Order.objects.filter(
            user=request.user, ordered=False
        )
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                try: 
                    order_produk_item = OrderProdukItem.objects.filter(
                        produk_item=produk_item,
                        user=request.user,
                        ordered=False
                    )[0]
                    
                    order.produk_items.remove(order_produk_item)
                    order_produk_item.delete()

                    pesan = f"Produk sudah dihapus"
                    messages.info(request, pesan)
                    return redirect('toko:order-summary')
                except ObjectDoesNotExist:
                    print('Error: order Produk sudah tidak ada')
            else:
                messages.info(request, 'Produk tidak ada')
                return redirect('toko:order-summary')
        else:
            messages.info(request, 'Produk tidak ada order yang aktif')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')