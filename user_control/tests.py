from rest_framework.test import APITestCase
from .views import get_random,get_access_token, get_refresh_token
# Create your tests here.
from .models import CustomUser,UserProfile
from message_control.tests import create_image,SimpleUploadedFile

class TestGenericFunctions(APITestCase):

    def test_get_random(self):
        rand1=get_random(10)
        rand2=get_random(10)
        rand3=get_random(15)

        self.assertTrue(rand1)

        self.assertNotEqual(rand1,rand2)

        self.assertEqual(len(rand1),10)
        self.assertEqual(len(rand3),15)

    def test_get_access_token(self):
        payload={
            'id':1
        }
        token=get_access_token(payload) 
        self.assertTrue(token)

    def test_get_refresh_token(self):

        token=get_refresh_token() 
        self.assertTrue(token)

class TestAuth(APITestCase):
    login_url='/user/login'
    register_url='/user/register'
    refresh_url='/user/refresh'

    def test_register(self):
        payload={
            'username':'rohit',
            'password':'1234'
        }
        response= self.client.post(self.register_url,data=payload)

        self.assertEqual(response.status_code,201)


    def test_login(self):
        payload={
            'username':'rohit',
            'password':'1234'
        }
        self.client.post(self.register_url,data=payload)
        response=self.client.post(self.login_url,data=payload)
        result=response.json()

        self.assertEqual(response.status_code,200)

        self.assertTrue(result['access'])
        self.assertTrue(result['refresh'])

    def test_refresh(self):
        payload={
            'username':'rohit',
            'password':'1234'
        }
        self.client.post(self.register_url,data=payload)
        response=self.client.post(self.login_url,data=payload)
        refresh=response.json()['refresh']

        response=self.client.post(self.refresh_url,data={'refresh':refresh})
        result=response.json()

        self.assertEqual(response.status_code,200)

        self.assertTrue(result['access'])
        self.assertTrue(result['refresh'])



class TestUserInfo(APITestCase):
    profile_url='/user/profile'
    file_upload_url="/message/file-upload"

    def setUp(self):
        self.user=CustomUser.objects._create_user(username='rohit',password='1234')
        self.client.force_authenticate(user=self.user)
    
    def test_post_user_profile(self):
        payload={
            'user_id':self.user.id,
            'first_name':'rohit',
            'last_name':'singh',
            'caption':'yoyo',
            'about':'kjhhkh'
        }
        response=self.client.post(self.profile_url,data=payload)
        result=response.json()
        self.assertEqual(response.status_code,201)
        self.assertEqual(result['first_name'],'rohit')
        self.assertEqual(result['last_name'],'singh')
        self.assertEqual(result['user']['username'],'rohit')
    
    def test_post_user_profile_with_profile_picture(self):


        avatar=create_image(None,'avatar.png')
        avatar_file=SimpleUploadedFile('front2.png',avatar.getvalue())
        data={
            'file_upload':avatar_file
        }

        response=self.client.post(self.file_upload_url,data=data)
        result=response.json()


        payload={
            'user_id':self.user.id,
            'first_name':'rohit',
            'last_name':'singh',
            'caption':'yoyo',
            'about':'kjhhkh',
            'profile_picture_id':result['id']
        }
        response=self.client.post(self.profile_url,data=payload)
        result=response.json()
        self.assertEqual(response.status_code,201)
        self.assertEqual(result['first_name'],'rohit')
        self.assertEqual(result['last_name'],'singh')
        self.assertEqual(result['user']['username'],'rohit')
        self.assertEqual(result['profile_picture']['id'],1)



    def test_update_user_profile(self):

        payload={
            'user_id':self.user.id,
            'first_name':'rohit',
            'last_name':'singh',
            'caption':'yoyo',
            'about':'kjhhkh'
        }

        response=self.client.post(self.profile_url,data=payload)
        result=response.json()

        payload={
            'first_name':'roh',
            'last_name':'si'
        }
        response=self.client.patch(self.profile_url+f"/{result['id']}",data=payload)
        result=response.json()

        self.assertEqual(response.status_code,200)
        self.assertEqual(result['first_name'],'roh')
        self.assertEqual(result['last_name'],'si')
        self.assertEqual(result['user']['username'],'rohit')

    def test_user_search(self):
        UserProfile.objects.create(user=self.user,first_name='rohitdd',last_name='singh',caption='sef',about='ljhl')
        self.user=CustomUser.objects._create_user(username='ttt',password='1234')
        UserProfile.objects.create(user=self.user,first_name='rottt',last_name='aah',caption='sefadff',about='ljafadhl')
        url=self.profile_url+'?keyword=rohit'

        response=self.client.get(url)
        result=response.json()['results']

        self.assertEqual(response.status_code,200)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['user']['username'],'rohit')
        self.assertEqual(result[0]['message_count'],0)

