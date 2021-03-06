from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Station(models.Model):
    station_name = models.CharField(max_length=36)
    station_address = models.CharField(max_length=200)
    station_lat = models.FloatField(default=0)
    station_long = models.FloatField(default=0)
    def __str__(self):
        return self.station_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    home_station_1 = models.ForeignKey(Station, related_name='h1',  blank=True, null=True)
    home_station_2 = models.ForeignKey(Station, related_name='h2', blank=True, null=True)
    home_station_3 = models.ForeignKey(Station, related_name='h3', blank=True, null=True)
    
    def __str__(self):
        return self.user
    
class Ride(models.Model):
    title_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    desc_text = models.TextField('description')
    s_neighborhood = models.CharField('start neighborhood', max_length=200)
    e_neighborhood = models.CharField('end neighborhood', max_length=200)
    difficulty = models.IntegerField()
    # owner = models.ForeignKey(UserProfile)
    owner = models.ForeignKey(User)
    # @classmethod
    # def create(cls, title, desc_text, s_neighborhood, e_neighborhood, difficulty):
        # ride = cls(title=title, pub_date=datetime.now(), desc_text=desc_text, s_neighborhood=s_neighborhood, e_neighborhood=e_neighborhood, difficulty=difficulty)
        # return ride
    
    def getDifficulty(self):
        return self.difficulty

    def setDifficulty(self, n):
        if n <= 0 or n > 10:
            return False
        else:
            self.difficulty = n

    def setTitle(self, st):
        if len(st) == 0:
            return False
        else:
            self.title_text = st

# A ride can have many tags
# A tag can be associated with many rides
class Tag(models.Model):
    rides = models.ManyToManyField(Ride)
    tag = models.CharField(max_length=20)

# A ride has a sequence of stations
class Stop(models.Model):
    ride = models.ForeignKey(Ride)
    number = models.IntegerField()
    station = models.ForeignKey(Station)

# A review has a comment an owner and a date
class Ride_Review(models.Model):
    ride = models.ForeignKey(Ride)
    comment = models.TextField()
    pub_date = models.DateTimeField('date commented')
    owner = models.ForeignKey(User)

# A review has a comment an owner and a date
class Station_Review(models.Model):
    station = models.ForeignKey(Station)
    comment = models.TextField()
    pub_date = models.DateTimeField('date commented')
    owner = models.ForeignKey(User)

# Every user should only rate once
# Each should be associated with one ride
class Ride_Rating(models.Model):
    ride = models.ForeignKey(Ride)
    rating = models.IntegerField(default=0)
    owner = models.ForeignKey(User)

# Every user should only rate once
# Each should be associated with one ride
class Station_Rating(models.Model):
    station = models.ForeignKey(Station)
    rating = models.IntegerField(default=0)
    owner = models.ForeignKey(User)

# A prediction belongs to a single station
# A station can have many predictions (based on days / times)
class Prediction(models.Model):
    bikes_available = models.FloatField() # the prediction
    day_of_week = models.CharField(max_length=3) # 3-letter days
    start_hour = models.IntegerField() # start hour of the prediction NOTE: this implementation assumes predictions are 1 hour windows
    station = models.ForeignKey(Station) # station that this prediction is for

    # setter functions
    def set_day_of_week(self, day):
        if day not in {'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'}:
            return False
        self.day_of_week = day
        return True

    def set_start_hour(self, hour):
        if hour < 0 or hour > 23:
            return False
        self.start_hour = hour
        return True

    def set_bikes_available(self, bikes):
        if bikes < 0:
            return False
        self.bikes_available = bikes
        return True
