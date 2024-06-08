from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.conf import settings
import os
import uuid
from django.core.validators import FileExtensionValidator


@deconstructible
class UploadToPathAndRename(object):
    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            filename = '{}.{}'.format(str(instance.pk)+'_'+str(uuid.uuid4().hex), ext)
        else:
            filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        return os.path.join(self.sub_path, filename)


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', unique=True)
    name = models.CharField(max_length=16, verbose_name='Nombres')
    photo = models.ImageField(blank=True, upload_to=UploadToPathAndRename(os.path.join(settings.MEDIA_ROOT, 'profile')), verbose_name='Avatar')
    email = models.EmailField(max_length=255, verbose_name='E-mail')

    STATUS_CHOICES = [
        (0, 'normal'),
        (-1, 'overdue')
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    class Meta:
        verbose_name = 'Lector'
        verbose_name_plural = 'Lectores'
        permissions = [
            ("create_book", "Puede crear libros"),
            ("delete_book", "Puede borrar libros"),
            ("update_book", "Puede cambiar la información mostrada sobre los libros"),
        ]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.SlugField(max_length=255, verbose_name='Nombre')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('index')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Book(models.Model):
    category = models.ManyToManyField(Category, verbose_name='Categoría', blank=True)
    fav = models.ManyToManyField(Reader, related_name='fav', default='none', blank=True)

    title = models.CharField(max_length=128, verbose_name='Título',default="titulo",null=True)
    author = models.CharField(max_length=128, verbose_name='Autor',default="desconocido")
    creation_date = models.CharField(max_length=128, verbose_name='Editorial',default="¿?",null=True)
    paginas = models.IntegerField(verbose_name='N° de paginas', default=0,null=True)
    description = models.CharField(max_length=1024, default='', verbose_name='Descripción', blank=True,null=True)
    subject = models.CharField(max_length=1024, default='', verbose_name='Asunto', blank=True,null=True)

    pdf_file = models.FileField(upload_to=UploadToPathAndRename(os.path.join(settings.MEDIA_ROOT, 'pdf_files')), verbose_name='Archivo PDF', validators=[FileExtensionValidator(['pdf'])], blank=True)


    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'

    def __str__(self):
        return self.title


class Favourite(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Libro')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return self.book.title
