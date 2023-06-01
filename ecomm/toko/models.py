from django.db import models
from django.urls import reverse

# Create your models here.

PILIHAN_KATEGORI = (
    ('S', 'Sepatu'),
    ('T', 'Tas'),
    ('B', 'Baju')
)

PILIHAN_LABEL = (
    ('NEW', 'primary'),
    ('SALE', 'info'),
    ('BEST', 'danger'),
)

PILIHAN_PEMBAYARAN = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
)

class ProdukItem(models.Model):
    nama_produk = models.CharField(max_length=100)
    harga = models.FloatField()
    harga_diskon = models.FloatField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    deskripsi = models.TextField()
    gambar = models.ImageField(upload_to='product_pics')
    label = models.CharField(choices=PILIHAN_LABEL, max_length=4)
    kategori = models.CharField(choices=PILIHAN_KATEGORI, max_length=2)

    def __str__(self):
        return f"{self.nama_produk} - ${self.harga}"
    
    class Meta:
        verbose_name_plural = "ProdukItem"

