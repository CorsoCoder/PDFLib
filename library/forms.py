from django import forms
from django.forms import ModelForm
from .models import Book, Reader, Category
from easy_select2 import Select2, Select2Multiple
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        label='Usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label='Contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'id': 'id_password',
        }),
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Nombre de usuario: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'username',
            'id': 'id_username',
        }),
    )
    name = forms.CharField(
        label='Nombre: ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'name',
            'id': 'id_name',
        }),
    )
    password = forms.CharField(
        label='Contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'password',
            'id': 'id_password',
        }),
    )
    re_password = forms.CharField(
        label='Repetir contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 're_password',
            'id': 'id_re_password',
        }),
    )
    email = forms.EmailField(
        label='E-mail: ',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'name': 'email',
            'id': 'id_email',
        }),
    )
    photo = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        label='Avatar: ',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'name': 'photo',
            'id': 'id_photo',
        }),
        required=False,
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está en uso.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')

        if password and re_password and password != re_password:
            self.add_error('re_password', 'Las contraseñas no coinciden.')

from django.contrib.auth.password_validation import validate_password

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Contraseña actual: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'old_password',
            'id': 'id_old',
        }),
    )
    new_password = forms.CharField(
        label='Contraseña nueva: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'new_password',
            'id': 'id_new',
        }),
    )
    repeat_password = forms.CharField(
        label='Repetir contraseña: ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'name': 'repeat_password',
            'id': 'id_repeat',
        }),
    )

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        validate_password(new_password)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        repeat_password = cleaned_data.get('repeat_password')

        if new_password and repeat_password:
            if new_password != repeat_password:
                raise ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
    
class BookSearchForm(forms.ModelForm):
    query = forms.CharField(label='Buscar', max_length=128, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Categoría', required=False)

    class Meta:
        widgets = {
            'category': Select2Multiple(attrs={'class': 'select2', 'required': 'True'}),
        }
    def __init__(self, *args, **kwargs):
        super(BookSearchForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'select2'})


class BookUpdateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'creation_date', 'paginas', 'description', 'subject', 'pdf_file']     
        class Meta:
            widgets = {
                'category': Select2Multiple(attrs={'class': 'select2', 'required': 'True'}),
            }
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['pdf_file', 'category']
        widgets = {
            'category': Select2Multiple(attrs={'class': 'select2', 'required': 'True'}),
        }

class ReaderForm(ModelForm):
    class Meta:
        model = Reader
        fields = '__all__'
