from django.conf.urls import url

from . import views
from catalog.views import AuthorListView
from catalog.views import AuthorDetailView
from catalog.views import BookDetailView
from catalog.views import BookListView
from catalog.views import CatalogHomeView
from catalog.views import LoanedBooksByUserListView
from catalog.views import LoanedBooksListView

urlpatterns = [
    # url(r'^$', CatalogHomeView.as_view(), name='home'),
    url(r'^$', views.index, name='index'),
    url(r'^books/$', BookListView.as_view(), name='books'),
    url(r'^book/(?P<pk>\d+)$', BookDetailView.as_view(), name='book-detail'),
    url(r'^authors/$', AuthorListView.as_view(), name='authors'),
    url(r'^author/(?P<pk>\d+)$', AuthorDetailView.as_view(), name='author-detail'),
    url(r'^mybooks/$', LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    url(r'^borrowed/$', LoanedBooksListView.as_view(), name='borrowed'),
    url(r'^book/(?P<pk>[-\w]+)/renew/$', views.renew_book_librarian, name='renew-book-librarian'),
]

# Author URLS
urlpatterns += [  
    url(r'^author/create/$', views.AuthorCreate.as_view(), name='author_create'),
    url(r'^author/(?P<pk>\d+)/update/$', views.AuthorUpdate.as_view(), name='author_update'),
    url(r'^author/(?P<pk>\d+)/delete/$', views.AuthorDelete.as_view(), name='author_delete'),
]

# Books
urlpatterns += [
    url(r'^book/create/$', views.BookCreate.as_view(), name='book_create'),
    url(r'^book/(?P<pk>\d+)/update/$', views.BookUpdate.as_view(), name='book_update'),
    url(r'^book/(?P<pk>\d+)/delete/$', views.BookDelete.as_view(), name='book_delete'),    
]
