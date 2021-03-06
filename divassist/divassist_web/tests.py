from django.test import TestCase, Client
from django.utils import timezone
from .models import Station, UserProfile, Ride, Tag, Stop, Ride_Review, Station_Review, Ride_Rating, Station_Rating, User, Prediction
from django.db import models

# Create your tests here.

class UserAuthenticationTests(TestCase):
    def set_up(self):
        self.client = Client()

    def test_template_availability(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/register/').status_code, 200)
        # login required pages are not available
        self.assertEqual(self.client.get('/registration/select_home_station/').status_code, 302)
        self.assertEqual(self.client.get('/home_page/').status_code, 302)

    def test_user_creation(self):
        test_client = Client()
        # registration arguments are invalid, page should not redirect
        # if two passwords are not the same
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': 'a@gmail.com', 
                                                   'password1': 'tomtom2', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 200);
        # if email address seems invalid
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': 'a', 
                                                   'password1': 'tomtom', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 200);
        # if any field is empty
        response = test_client.post('/register/', {'username': '', 
                                                   'email': 'a@gmail.com', 
                                                   'password1': 'tomtom', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 200);
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': '', 
                                                   'password1': 'tomtom', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 200);
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': 'a@gmail.com', 
                                                   'password1': '', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 200);
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': 'a@gmail.com', 
                                                   'password1': 'tomtom2', 
                                                   'password2': ''})
        self.assertEqual(response.status_code, 200);

        # page should direct if all arguments are valid
        response = test_client.post('/register/', {'username': 'tom', 
                                                   'email': 'a@gmail.com', 
                                                   'password1': 'tomtom', 
                                                   'password2': 'tomtom'})
        self.assertEqual(response.status_code, 302);
        self.assertRedirects(response, '/registration/select_home_station/')

    def test_login(self):
        # create a user for testing
        user = User()
        user.username = 'test'
        user.set_password('pass')
        user.save()

        test_client = Client()
        # user cannot login with incorrect username-password pair
        response = test_client.post('/', {'username': 'test', 'password': 'notpass'})
        self.assertEqual(response.status_code, 200)
        response = test_client.post('/', {'username': '', 'password': 'notpass'})
        self.assertEqual(response.status_code, 200)
        response = test_client.post('/', {'username': 'test', 'password': ''})
        self.assertEqual(response.status_code, 200)
        # user can login with correct username-password pair
        response = test_client.post('/', {'username': 'test', 'password': 'pass'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home_page/')

    def test_logout(self): 
        # create a user for testing
        user = User()
        user.username = 'test'
        user.set_password('pass')
        user.save()

        test_client = Client()
        test_client.login(username='test', password='pass')
        response = test_client.get('/home_page/')
        self.assertEqual(response.status_code, 200)
        test_client.get('/logout/')
        # client should not be able to access home_page directly after logout
        response = test_client.get('/home_page/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/home_page/')

    def test_change_password(self):
        # create a user for testing
        user = User()
        user.username = 'test'
        user.set_password('pass1')
        user.save()
        self.assertEqual(user.check_password("pass1"), True)
        # login with the correct credentials and navigate to the change password page
        test_client = Client()
        test_client.login(username='test', password='pass1')
        response = test_client.get('/registration/change_password/')
        self.assertEqual(response.status_code, 200)
        # cannot change password if original password is wrong
        response = test_client.post('/registration/change_password/', 
                                    {'old_password': 'wrong', 
                                     'new_password1': 'wrong', 
                                     'new_password2': 'wrong'})
        self.assertEqual(response.status_code, 200)
        # cannot change password if confirmation new password does not match new password
        response = test_client.post('/registration/change_password/', 
                                    {'old_password': 'pass1', 
                                     'new_password1': 'pass2', 
                                     'new_password2': 'wrong'})
        self.assertEqual(response.status_code, 200)
        # correct changes password and is then navigated to the homepage
        response = test_client.post('/registration/change_password/', 
                                    {'old_password': 'pass1', 
                                     'new_password1': 'pass2', 
                                     'new_password2': 'pass2'})
        self.assertEqual(response.status_code, 302)
        # check that password has been changed
        test_client.get('/logout/')
        # old password should not work
        response = test_client.post('/', {'username': 'test', 'password': 'pass1'})
        self.assertEqual(response.status_code, 200)
        # new password should work
        response = test_client.post('/', {'username': 'test', 'password': 'pass2'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home_page/')
        

class RideTests(TestCase):
    def setUp(self):
        self.user = User()
        self.user.username = 'test'
        self.user.set_password('pass')
        self.user.save()

        self.sta = Station(station_name="home", station_address="1642")
        self.sta.save()

        self.user_prof = UserProfile(user=self.user, email="abc@example.com", home_station_1=self.sta, home_station_2=self.sta, home_station_3=self.sta)
        self.user_prof.save()

    def test_ride_creation(self):
        self.user_prof = UserProfile.objects.get(user=self.user)
        # test_ride = Ride(title_text = "The Trip to Grandma's House", desc_text="It's so fun though guys!", s_neighborhood="Hyde Park", e_neighborhood="West Loop", difficulty=10)
        # self.assertIs(Ride(title_text="", desc_text=""), False)
        r = Ride(title_text="Title", desc_text="Description", s_neighborhood="Hyde Park", e_neighborhood="West Loop", pub_date=timezone.now(), owner=self.user, difficulty=9)
        r.save()
        self.assertIs(r.setDifficulty(11), False)
        self.assertIs(r.getDifficulty(), 9)
        self.assertIs(r.setDifficulty(-12), False)
        self.assertIs(r.setTitle(""), False)
        tag1 = Tag(tag='Hilly')
        tag1.save()
        tag1.rides.add(r)
        tagsset = Tag.objects.all()
        tagsset = tagsset.filter(rides__title_text__contains="Title")
        self.assertFalse(Tag.objects.all().filter(rides__title_text__contains='A terrible name for a rei-92u4orifd').exists())
        self.assertTrue(tagsset.exists())
        self.assertIs(Tag.objects.all().filter(rides__title_text__contains='Title').filter(tag__contains='Hilly').exists(), True)
        tag2 = Tag(tag='Scenery')
        tag2.save()
        self.assertIs(Tag.objects.all().filter(rides__title_text__contains='Title').filter(tag__contains='Scenery').exists(), False)
        # test stations
        st = Station.objects.all().first()
        s = Stop(ride=r, number=1, station=st)
        s.save()
        st1 = Station.objects.all().last()
        s2 = Stop(ride=r, number=2, station=st1)
        s2.save()
        stops = Stop.objects.all().filter(ride=r)
        sts = [s, s2]
        for i in range(len(stops)):
            self.assertTrue(stops[i] == sts[i])
        a = Stop(ride=r, number=6, station=st)
        a.save()
        self.assertEqual(Stop.objects.get(ride=r, number=6, station=st), a) # you cannot skip a number
        a = Stop(ride=r, number=3, station=st)
        a.save()
        self.assertEqual(Stop.objects.get(ride=r, number=3, station=st), a) # you can have the same stop multiple times

    
    def test_ride_reviews_and_ratings(self):
        self.user_prof = UserProfile.objects.get(user=self.user)
        r = Ride(title_text="Title", desc_text="Description", s_neighborhood="Hyde Park", e_neighborhood="West Loop", pub_date=timezone.now(), owner=self.user, difficulty=9)
        r.save()
        rr1 = Ride_Review(ride_id = 1, ride=r, comment="This was great", pub_date=timezone.now(), owner=self.user)
        rr1.save()
        a = Ride_Rating(ride=r, rating=11, owner=self.user)
        a.save()
        a = Ride_Rating(ride=r, rating=-1, owner=self.user)
        a.save()
        a = Ride_Rating(ride=r, rating=4, owner=self.user)
        a.save()
        self.assertTrue(Ride_Rating.objects.all().filter(ride=r, rating=11, owner=self.user).exists())
        self.assertTrue(Ride_Rating.objects.all().filter(ride=r, rating=-1, owner=self.user).exists())
        self.assertTrue(Ride_Rating.objects.all().filter(ride=r, rating=4, owner=self.user).exists())
        rating = Ride_Rating(ride=r, rating=4, owner=self.user)
        rating.save()
        ratings = Ride_Rating.objects.all().filter(ride__title_text__contains=r.title_text).values('rating')
        average = 0
        for i in range(len(ratings)):
            average += ratings[i].get('rating')

        self.assertIs(average/(len(ratings)), 4)

    def test_stations(self):
        # Stations are all propogated in the database 
        self.u1 = UserProfile.objects.get(user=self.user)
        station = Station.objects.all().first()
        st = Station_Rating(station=station, rating=8, owner=self.user)
        st.save()
        st1 = Station_Rating(station=station, rating=2, owner=self.user)
        st1.save()
        ratings = Station_Rating.objects.all().filter(station__station_name__contains=station.station_name).values('rating')
        average = 0
        for i in range(len(ratings)):
            average += ratings[i].get('rating')

        self.assertIs(average/(len(ratings)), 5)
        a = Station_Rating(station=station, rating=22, owner=self.user)
        a.save()
        self.assertTrue(Station_Rating.objects.all().filter(station=station, rating=22, owner=self.user).exists())

        # Station Reviews
        st = Station_Review(station=station, comment="LOUSY", pub_date=timezone.now(), owner=self.user)
        st.save()
        st1 = Station_Review(station=station, comment="AMAZING", pub_date=timezone.now(), owner=self.user)
        st1.save()
        b = [st, st1]
        reviews = Station_Review.objects.all().filter(station=station)
        numreviews = len(reviews)
        for i in range(len(reviews)):
            self.assertTrue(reviews[i] == b[i])

        a = Station_Review(station=station, comment="THE BEST", pub_date=timezone.now(), owner=self.user)
        a.save()
        # You can add a new review
        self.assertTrue(Station_Review.objects.all().filter(station=station, comment="THE BEST").exists())

        # It should not overwrite
        reviews = Station_Review.objects.all().filter(station=station)
        self.assertTrue(len(reviews) == (numreviews+1))


class PredictionTests(TestCase):
    def test_prediction_creation(self):
        test_station = Station(station_name="Test Station", station_address="100 Test St.")
        test_station.save()
        # test model initialization and saving
        test_prediction = Prediction(station=test_station, bikes_available=4.87, day_of_week="Mon", start_hour=5)
        test_prediction.save()
        # test setters
        # set day_of_week
        self.assertFalse(test_prediction.set_day_of_week("Mond")) # invalid day
        self.assertTrue(test_prediction.set_day_of_week("Wed")) # valid day
        self.assertIs(test_prediction.day_of_week, "Wed") # check setter worked
        # set start_hour
        self.assertFalse(test_prediction.set_start_hour(24)) # invalid hour
        self.assertFalse(test_prediction.set_start_hour(-1)) # invalid hour
        self.assertTrue(test_prediction.set_start_hour(23)) # valid hour
        self.assertIs(test_prediction.start_hour, 23) # check setter worked
        # set bikes_available
        self.assertFalse(test_prediction.set_bikes_available(-0.1)) # invalid num bikes
        self.assertTrue(test_prediction.set_bikes_available(2.98)) # valid num bikes
        self.assertIs(test_prediction.bikes_available, 2.98) # check setter worked
