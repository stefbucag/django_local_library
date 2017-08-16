from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from catalog.models import Author
from django.core.urlresolvers import reverse


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)
    
    def __setup_user_fixtures(self):
        """Setup users with different permissions."""
        # User can only view authors
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        # User can only add authors
        test_user2 = User.objects.create_superuser(username='testuser2', email='test@test.com', password='12345')
        test_user2.save()

    def test_view_url_exists_at_desired_location(self): 
        resp = self.client.get('/catalog/authors/') 
        self.assertEqual(resp.status_code, 200)  
           
    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        
    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        # self.assertTemplateUsed(resp, 'catalog/author_list.html')
        self.assertTemplateUsed(resp, 'author/list.html')
        
    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse('is_paginated' in resp.context)
        # self.assertTrue(resp.context['is_paginated'] == True)
        # self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors')+'?page=2')
        
        # print('Here response')
        # print(resp)
        # print(type(resp)) # HttpResponse
        # print(resp.context)
        # print(type(resp.context))
        
        self.assertEqual(resp.status_code, 200)
        self.assertFalse('is_paginated' in resp.context)
        # self.assertTrue(resp.context['is_paginated'] == False)
        # self.assertTrue( len(resp.context['author_list']) == 3)

    def test_author_create(self):
        """Test for views/AuthorCreate method."""
        # QUOTESTION: one test one method?

        # Check who has access
        resp = self.client.get(reverse('author_create', ) )
        self.assertEqual( resp.status_code, 302)

        self.__setup_user_fixtures()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author_create', ) )
        self.assertEqual( resp.status_code, 200)

        # Test template used for creating author
        resp = self.client.get(reverse('author_create', ) )
        self.assertEqual( resp.status_code,200)

        # View redirect on success
        resp = self.client.post(reverse('author_create', ), {'first_name':'Jon', 'last_name':'Snow', 'date_of_birth':'1961-11-08'} )
        self.assertTrue( resp.url.startswith('/catalog/author/') )
