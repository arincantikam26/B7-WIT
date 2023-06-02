from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from PIL import Image

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
    gambar = models.ImageField(upload_to='product_pics', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    label = models.CharField(choices=PILIHAN_LABEL, max_length=4)
    kategori = models.CharField(choices=PILIHAN_KATEGORI, max_length=2)
    
    def __str__(self):
        return f"{self.nama_produk} - ${self.harga}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.gambar.path)
        max_size = (260, 260)
        if img.height > max_size[1] or img.width > max_size[0]:
            img.thumbnail(max_size)
            img.save(self.gambar.path)

    def get_absolute_url(self):
        return reverse("toko:produk-detail", kwargs={
            "slug": self.slug
        })
    
    class Meta:
        verbose_name_plural = "ProdukItem"
