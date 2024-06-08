#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from io import BytesIO
from datetime import date, timedelta, datetime

import PyPDF2
from PIL import Image
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from .forms import BookForm, LoginForm, RegisterForm, ResetPasswordForm, BookUpdateForm
from .models import Book, Category, Favourite, Reader


@csrf_exempt
def delete_category_ajax(request):
    if request.method == 'POST':
        category_id = request.POST.get('id')
        try:
            category = Category.objects.get(pk=category_id)
            category.delete()
            return JsonResponse({'success': 'Category deleted'}, status=200)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category does not exist'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def create_category_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        if name:
            category, created = Category.objects.get_or_create(name=name)
            if created:
                return JsonResponse({'id': category.id, 'name': category.name}, status=201)
            else:
                return JsonResponse({'error': 'Category already exists'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def check_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True



def is_valid_email(email):
    """
    Check if the email address is valid.
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


def handle_uploaded_image(photo):
    """
    Handle uploaded image file.
    """
    image = Image.open(photo)
    image = image.convert("RGB")
    image.thumbnail((300, 300))
    thumbnail_io = BytesIO()
    image.save(thumbnail_io, format='JPEG')
    return thumbnail_io


def extract_pdf_metadata(pdf_file):
    """
    Extract metadata from the uploaded PDF file.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        description = ""
        for page in pdf_reader.pages:
            description += page.extract_text().strip() + " "
            if len(description) >= 200:
                break

        title = metadata.title.strip() if metadata.title else os.path.splitext(pdf_file.name)[0]
        author = metadata.author.strip() if metadata.author else "desconocido"
        creation_date = metadata.creation_date if hasattr(metadata, 'creation_date') else None
        if creation_date:
            formatted_date = datetime.datetime.strftime(creation_date, "%Y-%m-%d %H:%M:%S")
        else:
            formatted_date = "¡?"
        subject = metadata.subject.strip() if metadata.subject else "No subject"
        num_pages = len(pdf_reader.pages)

        return title, author, creation_date, subject, description[:150], num_pages

    except Exception as e:
        print("Error processing PDF file:", str(e))
        raise


def page_not_found_view(request, exception=None):
    """
    Handle page not found errors.
    """
    context = {}
    return render(request, 'error/404.html', context)



def list_categories(request):
    """
    List all categories along with the count of books in each category.
    """
    categories = Category.objects.all().annotate(book_count=Count('book')).order_by('name')
    context = {'categories': categories}
    return render(request, 'categories/list_categories.html', context)




def view_book_detail(request, id):
    """
    View details of a specific book.
    """
    try:
        book = get_object_or_404(Book, id=id)
    except Book.DoesNotExist:
        return HttpResponse('The book does not exist')

    reader = None
    if request.user.is_authenticated and not request.user.is_superuser:
        reader = get_object_or_404(Reader, user=request.user)

    fav = None
    if reader:
        fav = Favourite.objects.filter(book=book, user=request.user).first() 

    context = {
        'book': book,
        'fav': fav,  
    }
    return render(request, 'CRUD/book_detail.html', context)

@staff_member_required
def update_book_view(request, id):
    """
    View for updating book details (requires staff permissions).
    """
    try:
        book = get_object_or_404(Book, pk=id)
    except:
        return HttpResponse('No book exists with that ID.')

    if request.method == 'POST':
        form = BookUpdateForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            return redirect('detail_book', id=book.id)
    else:
        form = BookUpdateForm(instance=book)

    context = {
        'form': form,
    }
    return render(request, 'CRUD/update_view.html', context)


@staff_member_required
def delete_book_view(request, id):
    """
    View for deleting a book (requires staff permissions).
    """
    context = {}

    if not id:
        return HttpResponse('No ID provided.')

    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return HttpResponse('No book exists with this ID')

    obj = get_object_or_404(Book, pk=id)
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect(reverse("search_books"))

    return render(request, "CRUD/delete_view.html", context)


from django.db.models import Q
from django.shortcuts import render
from .models import Book, Category

def search_books(request):
    """
    Search for books based on query parameters.
    """
    query = request.GET.get('q')
    category = request.GET.get('category')
    categories = Category.objects.all()
    user = request.user

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__icontains=query)
        )
        if category:
            books = books.filter(category__name=category)

    elif category:
        books = Book.objects.filter(category__name=category)
    else:
        books = Book.objects.all()

    for book in books:
        fav = Favourite.objects.filter(user=user).select_related('book')
        print(fav)
        

    context = {
        'books': books,
        'query': query,
        'category': category,
        'categories': categories,
        'fav': fav,
    }
    return render(request, 'generic/book_list.html', context)



@staff_member_required
def create_book_view(request):
    """
    View for creating a new book (requires staff permissions).
    """
    if not request.user.is_superuser and not request.user.groups.filter(permissions__codename='create_book').exists():
        return redirect('/')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)

            if 'pdf_file' in request.FILES:
                pdf_file = request.FILES['pdf_file']
                try:
                    title, author, creation_date, subject, description, num_pages = extract_pdf_metadata(pdf_file)
                    book.description = description
                    book.title = title
                    book.author = author
                    book.creation_date = creation_date
                    book.subject = subject
                    book.pages = num_pages

                except Exception as e:
                    print("Error processing the PDF file:", str(e))
                    return HttpResponse("Error processing the PDF file: {}".format(str(e)), status=500)

            book.save()
            form.save_m2m()

            return redirect('/book/detail_book/' + str(book.id))
    else:
        form = BookForm()

    context = {'form': form}
    return render(request, "CRUD/create_view.html", context)


def about(request):
    """
    View for the about page.
    """
    context = {}
    return render(request, "generic/about.html", context)


def index(request):
    """
    View for the home page.
    """
    reader = None
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            try:
                reader = Reader.objects.get(user=request.user)
            except Reader.DoesNotExist:
                pass
    context = {
        'reader': reader,
    }
    return render(request, 'generic/index.html', context)


class CustomLoginView(LoginView):
    """
    Customized login view.
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile')

    def form_invalid(self, form):
        messages.error(self.request, 'Incorrect username or password.')
        return super().form_invalid(form)


def user_register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')

    register_form = RegisterForm()

    if request.method == 'POST':
        register_form = RegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            password = register_form.cleaned_data['password']
            repeat_password = register_form.cleaned_data['re_password']
            email = register_form.cleaned_data['email']
            username = register_form.cleaned_data['username']
            name = register_form.cleaned_data['name']
            photo = register_form.cleaned_data['photo']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username already exists.')
            elif not photo.name.lower().endswith(('jpg', 'png', 'jpeg', 'gif')):
                messages.error(request, 'Only photos in "png, jpg, jpeg, or gif" format are accepted.')
            elif password != repeat_password:
                messages.error(request, 'Passwords do not match.')
            else:
                new_user = User.objects.create(username=username, email=email)
                new_user.set_password(password)
                new_user.save()

                new_reader = Reader.objects.create(user=new_user, name=name, email=email)

                if photo:
                    thumbnail_io = handle_uploaded_image(photo)
                    thumbnail_file = InMemoryUploadedFile(thumbnail_io, None, photo.name, 'image/jpeg',
                                                           thumbnail_io.tell(), None)
                    new_reader.photo.save(photo.name, thumbnail_file, save=False)

                new_reader.save()
                messages.success(request, 'Registration successful.')
                login(request, new_user)
                return HttpResponseRedirect('/profile')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    return render(request, 'registration/register.html', {'register_form': register_form})


@login_required
def change_password(request):
    """
    View for changing user password.
    """
    user = request.user

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user)

    context = {
        'resetPasswordForm': form,
    }
    return render(request, 'registration/change_password.html', context)


@login_required
def user_logout(request):
    """
    User logout view.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')


@login_required
def profile(request):
    """
    User profile view.
    """
    reader = None
    try:
        reader = Reader.objects.get(user=request.user)
    except Reader.DoesNotExist:
        pass

    context = {
        'state': request.GET.get('state', None),
        'reader': reader,
    }
    return render(request, 'registration/profile.html', context)


def favourite_view(request):
    """
    View for displaying user's favorite books.
    """
    if request.user.is_authenticated:
        user = request.user
        favorites = Favourite.objects.filter(user=user).select_related('book')
        return render(request, "favourite/favourite.html", {"favorites": favorites})
    return redirect("user_login")



def add_to_favourites(request, id):
    """
    View for adding a book to user's favorites.
    """
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite()
        fav.user = request.user
        fav.book = book
        fav.save()
        return redirect("favourite")
    return redirect("user_login")



def remove_favourite(request, id):
    """
    View for removing a book from user's favorites.
    """
    if request.user.is_authenticated:
        book = Book.objects.filter(pk=id).first()
        fav = Favourite.objects.filter(user=request.user, book=book)
        fav.delete()
        return redirect("favourite")
    return redirect("user_login")

        
