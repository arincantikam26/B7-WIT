# Women In Tech Program
## B7-Brilliant Legacy (E-Commerce)
### Persiapan awal
1. Clone project
2. Buka project yang sudah di clone
3. Buat file .env dan copy paste isi file .template.env
4. Buat environment baru, aktifkan dan install library
5. Buat database postgre : ecommerce_b7 dan restore

### Running Program
1. Migrasi database 
```
$ python manage.py makemigrations toko
$ python manage.py migrate
```
2. Jalankan program
```
$ python manage.py runserver
```
