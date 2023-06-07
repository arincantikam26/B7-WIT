from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape
from paypal.standard.forms import PayPalPaymentsForm
from .forms import CheckoutForm, CommentForm, ContactForm
from .models import ProdukItem, OrderProdukItem, Order, AlamatPengiriman, Payment, ProdukImage
from django.http import HttpResponseRedirect
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect


class HomeListView(generic.ListView):
    model = ProdukItem
    template_name = 'home.html'
    paginate_by = 8
    queryset = ProdukItem.objects.all()
    @csrf_exempt
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query  = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('kategori')

        if search_query:
            queryset = ProdukItem.objects.filter(nama_produk__icontains=search_query)

        if category_filter and category_filter != 'all':
            queryset = queryset.filter(kategori=category_filter)

        return queryset.order_by('nama_produk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for pItem in context['object_list']:
            pItem.rating = range(pItem.rating)  # Ubah menjadi range
        return context

class ProductDetailView(FormMixin, generic.DetailView):
    template_name = 'product_detail.html'
    queryset = ProdukItem.objects.all()
    form_class = CommentForm
    success_url = '.' 
    
    @csrf_exempt
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['object']
        product.rating = range(product.rating)  # Ubah menjadi range
        if 'comment_form' not in context:
            context['comment_form'] = CommentForm(initial={'object': product})  # Menginisialisasi dengan product
        else:
            context['comment_form'].instance = CommentForm(initial={'object': product})  # Update instance dengan product
        return context
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.product = self.object
        comment.user = self.request.user
        comment.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('toko:produk-detail', kwargs={'slug': self.object.slug})



class CheckoutView(LoginRequiredMixin, generic.FormView):
    @csrf_exempt
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
    
    @csrf_exempt
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
            messages.info(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('toko:order-summary')

class PaymentView(LoginRequiredMixin, generic.FormView):
    @csrf_exempt
    def get(self, *args, **kwargs):
        template_name = 'payment.html'
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            paypal_data = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': order.get_total_harga_order,
                'item_name': f'Pembayaran belajanan order: {order.id}',
                'invoice': f'{order.id}-{timezone.now().timestamp()}' ,
                'currency_code': 'USD',
                'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': self.request.build_absolute_uri(reverse('toko:paypal-return')),
                'cancel_return': self.request.build_absolute_uri(reverse('toko:paypal-cancel')),
            }
        
            qPath = self.request.get_full_path()
            isPaypal = 'paypal' in qPath
        
            form = PayPalPaymentsForm(initial=paypal_data)
            context = {
                'paypalform': form,
                'order': order,
                'is_paypal': isPaypal,
            }
            return render(self.request, template_name, context)

        except ObjectDoesNotExist:
            return redirect('toko:checkout')

class OrderSummaryView(LoginRequiredMixin, generic.TemplateView):
    @csrf_exempt
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'keranjang': order,
            }
            template_name = 'order_summary.html'
            return render(self.request, template_name, context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('/')
        
@login_required
@csrf_exempt
def add_to_cart(request, slug):
    if request.user.is_authenticated:
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
                pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                messages.info(request, pesan)
                return redirect('toko:produk-detail', slug = slug)
            else:
                order.produk_items.add(order_produk_item)
                messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
                return redirect('toko:produk-detail', slug = slug)
        else:
            tanggal_order = timezone.now()
            order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
            order.produk_items.add(order_produk_item)
            messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
            return redirect('toko:produk-detail', slug = slug)
    else:
        return redirect('/accounts/login')
    
@login_required    
@csrf_exempt
def min_to_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                try:
                    order_produk_item = OrderProdukItem.objects.get(
                        produk_item=produk_item,
                        user=request.user,
                        ordered=False
                    ) 
                    if order_produk_item.quantity > 1 :
                        order_produk_item.quantity -= 1
                        order_produk_item.save()
                        pesan = f"ProdukItem sudah dikurangi menjadi: { order_produk_item.quantity }"
                        messages.info(request, pesan)
                        return redirect('toko:produk-detail', slug = slug)
                    else:
                        order.produk_items.remove(order_produk_item)
                        order_produk_item.delete()
                        pesan = f"ProdukItem sudah dihapus"
                        messages.info(request, pesan)
                        return redirect('toko:produk-detail',slug = slug)

                except ObjectDoesNotExist:
                    print('Error: order ProdukItem sudah tidak ada')
            else:
                messages.info(request, 'ProdukItem tidak ada')
                return redirect('toko:produk-detail',slug = slug)
        else:
            messages.info(request, 'ProdukItem tidak ada order yang aktif')
            return redirect('toko:produk-detail',slug = slug)
    else:
        return redirect('/accounts/login')
    
@login_required    
@csrf_exempt
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

                    pesan = f"ProdukItem sudah dihapus"
                    messages.info(request, pesan)
                    return redirect('toko:order-summary')
                except ObjectDoesNotExist:
                    print('Error: order ProdukItem sudah tidak ada')
            else:
                messages.info(request, 'ProdukItem tidak ada')
                return redirect('toko:order-summary')
        else:
            messages.info(request, 'ProdukItem tidak ada order yang aktif')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')
    
@login_required
@csrf_exempt
def paypal_return(request):
    if request.user.is_authenticated:
        try:
            print('paypal return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'P' # paypal kalai 'S' stripe
            payment.charge_id = f'{order.id}-{timezone.now()}'
            payment.timestamp = timezone.now()
            payment.save()
            
            order_produk_item = OrderProdukItem.objects.filter(user=request.user,ordered=False)
            order_produk_item.update(ordered=True)
            
            order.payment = payment
            order.ordered = True
            order.save()

            messages.info(request, 'Pembayaran sudah diterima, terima kasih')
            return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            messages.error(request, 'Periksa kembali pesananmu')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')

@csrf_exempt
def paypal_cancel(request):
    messages.error(request, 'Pembayaran dibatalkan')
    return redirect('toko:order-summary')

@csrf_exempt
def ContactView(request):
    return render(request, 'contact.html')

def contact(request):
    
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ["arincantikam@gmail.com"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            messages.info(request, 'Thankyou, Pesan berhasil terkirim!')
    return render(request, "contact.html", {"form": form})


class ContactView(generic.FormView):
    @csrf_exempt
    def get(self, *args, **kwargs):
        form = ContactForm()
        context = {
            'form': form,
        }
        template_name = 'contact.html'
        return render(self.request, template_name, context)
    
    @csrf_exempt
    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            from_email = form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            try:
                send_mail(subject, message, from_email, ["arincantikam@gmail.com"])
            except BadHeaderError:
                messages.error(self.request, 'Pesan gagal dikirim!')
                return redirect('toko:contact')
            messages.info(self.request, 'Thankyou, Pesan berhasil terkirim!')
            return redirect('toko:contact')

      