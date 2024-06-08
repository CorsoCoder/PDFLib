from django.contrib import admin
from library.models import Book, Reader, Favourite, Category
from django import forms
from easy_select2 import Select2, Select2Multiple
from admin_auto_filters.filters import AutocompleteFilter


class ReaderFilter(AutocompleteFilter):
    title = 'Usuarios'
    field_name = 'user'


class ReaderAdminForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = '__all__'


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    search_fields = ('email', 'user__username', 'name')
    list_display = ('user', 'email', 'status')
    list_filter = [ReaderFilter, 'status']
    form = ReaderAdminForm


class FavouriteFilterUser(AutocompleteFilter):
    title = 'Usuarios'
    field_name = 'user'


class FavouriteFilterBook(AutocompleteFilter):
    title = 'Libro'
    field_name = 'book'


class FavouriteAdminForm(forms.ModelForm):
    class Meta:
        model = Favourite
        fields = '__all__'
        widgets = {
            'book': Select2(),
            'user': Select2(),
        }


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    search_fields = ("book__title", "user__username")
    list_display = ('book', 'user')
    list_filter = [FavouriteFilterUser, FavouriteFilterBook]
    form = FavouriteAdminForm


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    form = CategoryAdminForm


class BookFilterCategory(AutocompleteFilter):
    title = 'Categorías'
    field_name = 'category'


class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'category': Select2Multiple(),
        }


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    search_fields = ("title", "author")
    list_display = ("title", "author", 'creation_date', 'subject', 'get_categories_display')
    list_filter = [BookFilterCategory]
    form = BookAdminForm

    def get_categories_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])

    get_categories_display.short_description = 'Categorías'

admin.site.site_title = 'Panel de administración'
admin.site.site_header = 'Panel de administración'
