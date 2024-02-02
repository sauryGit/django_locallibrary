from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# Create your views here.


# function based view
@login_required
def index(request):
  """View function for home page of site."""

  # Generate counts of some of the main objets
  num_books = Book.objects.all().count()
  num_instances = BookInstance.objects.all().count()

  # Abailable books (status = 'a')
  num_instances_available = BookInstance.objects.filter(status__exact='a').count()

  # The 'all()' is implied by default.
  num_authors = Author.objects.count()

  num_genres = Genre.objects.count()

  num_books_contain_whowho = Book.objects.filter(title__contains="누구누구").order_by('title')

  num_visits = request.session.get('num_visits', 0)
  request.session['num_visits'] = num_visits + 1
  request.session.set_expiry(10000)

  context = {
      'num_books': num_books,
      'num_instances': num_instances,
      'num_instances_available': num_instances_available,
      'num_authors': num_authors,
      'num_genres': num_genres,
      'num_books_contain_whowho': num_books_contain_whowho,
      'num_visits': num_visits,
  }

  # Render the HTML template index.html with the data in the context variable
  return render(request, 'index.html', context=context)


# class based view
class BookListView(LoginRequiredMixin, generic.ListView):
  
  model = Book

  context_object_name = 'book_list'
  # queryset = Book.objects.filter(title__icontains='har')[:5]
  template_name = 'catalog/book_list.html'
  paginate_by = 30

class BookDetailView(LoginRequiredMixin, generic.DetailView):
  model = Book

  template_name = 'catalog/book_detail.html'

class AuthorListView(LoginRequiredMixin, generic.ListView):
  model = Author

  context_object_name = 'author_list'
  template_name = 'catalog/author_list.html'
  paginate_by = 30

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
  model = Author
  # login_url = '/login/'
  # redirect_field_name = 'redirect_to'
  template_name = 'catalog/author_detail.html'
  

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
  """Generic class-based view listing books on loan to current user."""
  model = BookInstance
  template_name = 'catalog/bookinstance_list_borrowed_user.html'
  paginate_by = 30

  def get_queryset(self):
    return (
      BookInstance.objects.filter(borrower=self.request.user)
      .filter(status__exact='o')
      .order_by('due_back')
    )

class BorrowedBooks(PermissionRequiredMixin, generic.ListView):
  """All borrowed books"""
  model = Book
  template_name = 'catalog/all_borrowed_list.html'
  paginated_by = 30
  context_object_name = 'borrowedlist'
  permission_required = 'catalog.can_mark_returned'