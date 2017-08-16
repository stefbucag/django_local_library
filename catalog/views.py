import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre


class CatalogHomeView(TemplateView):
    """Catalog Home View module."""

    def get(self, request):
        return HttpResponse("site index!")


def index(request):
    """View for Catalog home."""
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_genres = Genre.objects.all().count()

    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Books with specific words
    word_python_count = Book.objects.filter(summary__contains='python').count()
    word_summary_count = Book.objects.filter(summary__contains='summary').count()

    # Session
    # Number of visitss to this view, as counted in the session value
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books':num_books,
                 'num_instances':num_instances,
                 'num_instances_available':num_instances_available,
                 'num_authors':num_authors,
                 'num_genres': num_genres,
                 'python_count': word_python_count,
                 'summary_count': word_summary_count,
                 'num_visits': num_visits,
                 },
    )


class BookListView(ListView):
    model = Book
    # paginate_by = 2

    context_object_name = 'book_list'   # your own name for the list as a template variable
    queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    template_name = 'catalog/book_list.html'  # Specify your own template name/location

    def get_queryset(self):
        """Override the get_queryset function."""
        queryset = Book.objects.all()

        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookListView, self).get_context_data(**kwargs)

        # Get the blog from id and add it to the context
        # context['some_data'] = 'This is just some data'
        return context

        # return render(request, self.template_name, {'book_list': queryset})


class BookDetailView(DetailView):
    model = Book

    def book_detail_view(request, pk):
        try:
            book_id=Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")

        #book_id=get_object_or_404(Book, pk=pk)
        
        return render(
            request,
            'catalog/book_detail.html',
            context={'book':book_id,}
        )

class AuthorListView(ListView):
    """View module to list authors."""

    model = Author
    template_name = 'author/list.html'

    def get_authors(self):
        """Query authors."""
        """
        try:
            authors = Author.objects.all()
        except:
            raise
        """

        return Author.objects.all()

    """
    NOTE: If method name is changed, author list is empty.
    """
    def get(self, request):
        """Show author list."""
        authors = Author.objects.all()
        data = {'authors': self.get_authors()}
        # data = {'authors': authors}
        
        return render(request, self.template_name, data)

'''
class AuthorDetailView(DetailView):
    """View module for Author details."""

    model = Author

    def get(request, pk):
        try:
            author_id=Author.model.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404("Author does not exist")

        return render(
            request,
            'author/author_detail.html',
            context={'author':author_id,}
        )
'''

class AuthorDetailView(DetailView):
    """
    Generic class-based detail view for an author.
    """
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, ListView):
    """View of all Borrowed books."""
    model = BookInstance
    permission_required = ('catalog.can_mark_returned')

    template_name = 'catalog/bookinstance_list_borrowed_all.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class RenewLoanedBookView(TemplateView):
    """View to allow renewal of loaned book."""

    model = BookInstance

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed') )

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(LoginRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    # initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

# Books
class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    # fields = ['first_name','last_name','date_of_birth','date_of_death']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
