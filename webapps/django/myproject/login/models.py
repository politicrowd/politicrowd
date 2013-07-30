from django.db import models
from django.contrib.auth.models import User 
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import USStateField
from geopy import geocoders
from pygeocoder import Geocoder, GeocoderError


# Create your models here.
	
	
class Location(models.Model):
	first = models.CharField(max_length=100, blank=True, null=True)
	last = models.CharField(max_length=100, blank=True, null=True)
	tag = models.CharField(max_length=100, blank=True, null=True) #ex: professor of law at Columbia
	verified = models.BooleanField(default=False)#have we verified that this account is who they say they are
	public = models.BooleanField(default=False)#certain public figures/users may want to show their full name
	user = models.ForeignKey(User)
	address = models.TextField(blank=True, null=True)
	city = models.CharField(max_length=100)
	state = USStateField(choices=STATE_CHOICES)
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)
	def __unicode__(self):
		return self.user.username
		
	def save(self):
		if not (self.latitude and self.longitude):
			geocoder = geocoders.GoogleV3()
			geocoding_results = None

			if self.address:
				try:
					query = '%(address)s, %(city)s, %(state)s' % self.__dict__
					g = Geocoder()
					if g.geocode(query).valid_address:
						geocoding_results = list(geocoder.geocode(query, exactly_one=False))
     					if geocoding_results:
						place, (latitude, longitude) = geocoding_results[0]
						self.latitude = latitude
						self.longitude = longitude
						super(Location, self).save()
					else:
						self.latitude = 0
						self.longitude = 0
						super(Location, self).save()
						self.delete()
						return 'address'
				except GeocoderError:
					return 'address'
		else:
			super(Location, self).save()
     