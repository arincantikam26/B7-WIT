from django.contrib import admin
from .models import ProdukItem
# Register your models here.

class ProdukItemAdmin(admin.ModelAdmin):
    list_display = ['nama_produk','harga', 'harga_diskon', 'slug',
                    'deskripsi', 'gambar', 'label', 'kategori']

admin.site.register(ProdukItem, ProdukItemAdmin)