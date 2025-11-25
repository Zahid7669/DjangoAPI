from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from storage.models import Organization, UploadedFile, Download


class TestStorageAPI(TestCase):
    def setUp(self):
        User = get_user_model()
        self.org1 = Organization.objects.create(name='Org1')
        self.org2 = Organization.objects.create(name='Org2')
        self.alice = User.objects.create_user('alice', password='password', organization=self.org1)
        self.bob = User.objects.create_user('bob', password='password', organization=self.org2)
        self.user_no_org = User.objects.create_user('no_org_user', password='password', organization=None)
        self.client = APIClient()
        self.client.force_authenticate(user=self.alice)

    def _list_results(self, resp):
        data = resp.data
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        return data

    def test_upload_and_download_recorded(self):
        f = SimpleUploadedFile('hello.txt', b'hello world')
        resp = self.client.post('/api/files/', {'file': f}, format='multipart')
        self.assertEqual(resp.status_code, 201)
        file_id = resp.data['id']
        uf = UploadedFile.objects.get(pk=file_id)
        self.assertEqual(uf.organization, self.alice.organization)

        # Download the file and ensure Download record created
        resp2 = self.client.get(f'/api/files/{file_id}/download/')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Download.objects.filter(file=uf, user=self.alice).count(), 1)

        # File list includes download_count
        resp3 = self.client.get('/api/files/')
        items = self._list_results(resp3)
        found = [i for i in items if i['id'] == file_id]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['download_count'], 1)

    def test_organization_total_downloads_and_filters(self):
        # Upload a file by alice
        f = SimpleUploadedFile('a.txt', b'a')
        resp = self.client.post('/api/files/', {'file': f}, format='multipart')
        file_id = resp.data['id']

        # alice downloads twice
        self.client.get(f'/api/files/{file_id}/download/')
        self.client.get(f'/api/files/{file_id}/download/')

        # bob downloads once
        self.client.force_authenticate(user=self.bob)
        self.client.get(f'/api/files/{file_id}/download/')

        # Check organization totals
        self.client.force_authenticate(user=self.alice)
        resp = self.client.get('/api/organizations/')
        self.assertEqual(resp.status_code, 200)
        orgs = self._list_results(resp)
        org = next(o for o in orgs if o['id'] == self.org1.id)
        self.assertEqual(org['total_downloads'], 3)

        # Downloads by user
        resp = self.client.get(f'/api/downloads/?user={self.alice.id}')
        self.assertEqual(resp.status_code, 200)
        dl = self._list_results(resp)
        self.assertTrue(len(dl) >= 2)

        # Downloads for file
        resp = self.client.get(f'/api/downloads/?file={file_id}')
        self.assertEqual(resp.status_code, 200)
        dl_file = self._list_results(resp)
        self.assertEqual(len(dl_file), 3)


class TestExceptionHandling(TestCase):
    def setUp(self):
        User = get_user_model()
        self.org1 = Organization.objects.create(name='Org1')
        self.user_with_org = User.objects.create_user('with_org', password='password', organization=self.org1)
        self.user_no_org = User.objects.create_user('no_org', password='password', organization=None)
        self.client = APIClient()

    def test_upload_without_organization(self):
        """Test that uploading without an organization returns proper error"""
        self.client.force_authenticate(user=self.user_no_org)
        f = SimpleUploadedFile('test.txt', b'test content')
        resp = self.client.post('/api/files/', {'file': f}, format='multipart')
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn('organization', resp.data)
        self.assertIn('must belong to an organization', str(resp.data['organization']))

    def test_upload_without_file(self):
        """Test that uploading without a file returns proper error"""
        self.client.force_authenticate(user=self.user_with_org)
        resp = self.client.post('/api/files/', {}, format='multipart')
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn('file', resp.data)

    def test_download_nonexistent_file(self):
        """Test downloading a file that doesn't exist returns 404"""
        self.client.force_authenticate(user=self.user_with_org)
        resp = self.client.get('/api/files/99999/download/')
        
        self.assertEqual(resp.status_code, 404)

    def test_invalid_user_id_filter(self):
        """Test that invalid user ID in filter returns proper error"""
        self.client.force_authenticate(user=self.user_with_org)
        resp = self.client.get('/api/downloads/?user=invalid_id')
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user', resp.data)
        self.assertIn('Invalid user ID', str(resp.data['user']))

    def test_invalid_file_id_filter(self):
        """Test that invalid file ID in filter returns proper error"""
        self.client.force_authenticate(user=self.user_with_org)
        resp = self.client.get('/api/downloads/?file=not_a_number')
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn('file', resp.data)
        self.assertIn('Invalid file ID', str(resp.data['file']))
