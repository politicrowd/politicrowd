from django.db import modelsfrom datetime import datetime, timedeltafrom django.contrib.auth.models import User from django.db.models.query import QuerySet
from uuslug import uuslug as slugify
from math import sqrt

from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import USStateField


class Tag(models.Model): #grabs the top tags from openletters targeting congress
	tag = models.CharField(max_length=60) #system generated based on most popular key words have list of banned tags too
	frequency = models.IntegerField()
	rank_trending = models.IntegerField(default = 0) 
	rank_date = models.DateTimeField(default=datetime.now)
	last_rank = models.IntegerField(default=0)
	last_rank_date = models.DateTimeField(default=datetime.now)
	date_created = models.DateTimeField(default=datetime.now)
	def __unicode__(self):
		return self.tag
#user specifies #tag like this and then you look through text to see if it has that
class Blog(models.Model):
	tag = models.ManyToManyField(Tag, related_name='blog_tags')
	title = models.CharField(max_length=90)
	creation_date = models.DateTimeField(default=datetime.now)
	content = models.TextField(max_length=5000)
	user = models.ForeignKey(User)
	def __unicode__(self):
		return self.title

class Email(models.Model):
	email = models.EmailField()
	def __unicode__(self):
		return self.email

class Volunteer(models.Model):
	name = models.CharField(max_length=60)
	email = models.EmailField()
	phone = models.CharField(max_length=20, blank=True, null=True)
	volunteer = models.CharField(max_length=60)
	comments = models.CharField(max_length=500, blank=True, null=True)
	def __unicode__(self):
		return self.name

#rank method: take your objects and calculate the average and the stdev of the scores during this period - need new score and old score - only rank scores greater than some number. 
#RANK: basically assume keep the same rank but adjust for hot new things etc ultimately want your solid core of discussion plus the new things that deserve to be in this top layout

#look at different vote classes basically or idk but grab and look at the average increase percent in that vote range so look for ones that shouldnt be there and then look so look for average move from this to last and then look at those moves as percent and rank those
class Rank(models.Model): #gives me the stats to use to rank different parts along the time curve that everything is moving on. created once each rank
	type_ranked = models.CharField(max_length=100) #class name of what was ranked
	date_ranked = models.DateTimeField(default=datetime.now) #date of the ranking
	number_ranked = models.IntegerField() #number of objects ranked
	average_rank = models.IntegerField() #look at stdev take off tails and disgard them 
	std_dev = models.IntegerField() #develop rank based on this score. can only rank ones that are hit
class Issue(models.Model):    title = models.CharField(max_length=60)    slug = models.CharField(max_length=120, primary_key=True)
    rank = models.IntegerField(default=0) #increase rank every hour or so    rank_trending = models.IntegerField(default = 0) #every hour...
    rank_date = models.DateTimeField(default=datetime.now)
    last_rank = models.IntegerField(default=0)
    last_rank_date = models.DateTimeField(default=datetime.now)
    tags = models.ManyToManyField(Tag, blank=True)#frequently updated tag list
    state = USStateField(choices=STATE_CHOICES, null=True, blank=True)
    city = models.CharField(blank=True, null=True, max_length=100)    creation_date = models.DateTimeField(default=datetime.now) #allow people to submit own issue name
    creator = models.ForeignKey(User) #allow people to submit own issues, track who submits what
    def open_letters(self): #add another model to set the trending rank score etc
    	open_letters = Open_Letter.objects.filter(issue=self).order_by('-rank')[:3]
    	return open_letters    def __unicode__(self):        return self.title    def save(self, *args, **kwargs):        self.slug = slugify(self.title, instance=self)        super(Issue, self).save(*args, **kwargs)

class Public_Id(models.Model): #make politician boolean
	user = models.ForeignKey(User)
	first = models.CharField(max_length=200)
	last = models.CharField(max_length=100, blank=True, null=True)
	title = models.CharField(max_length=100, blank=True, null=True)
	public = models.BooleanField(default=False)
	politician = models.ForeignKey('Politician', blank=True, null=True)
	city = models.CharField(max_length=100)
	state = USStateField(choices=STATE_CHOICES, null=True, blank=True)
	def __unicode__(self):
		return self.first
  #no usernames unless using real name. only register with email address.#Or debate style - pose the issue, go to town, politician can participate, be tagged by users, etc. # of tags of politician counted

#Open_Letter objects should be staticclass Open_Letter(models.Model): #trending globally want to know number of votes relative to age so discount votes     issue = models.ForeignKey(Issue)    title = models.CharField(max_length=260)    slug = models.CharField(max_length=120)
    draft = models.BooleanField(default=True)
    introduction = models.TextField(max_length=1000, blank=True)    content = models.TextField(max_length=1000, blank=True)    creation_date = models.DateTimeField(default=datetime.now)    creator = models.ForeignKey(Public_Id)
    contributors = models.ManyToManyField(User, related_name='contributors')
    responses = models.IntegerField(default=0)
    image_url = models.URLField(null=True, blank=True)#allow imgur photo upload    youtube_url = models.URLField(null=True, blank=True)#allow youtube
    target = models.TextField(max_length = 120, blank=True, null=True)#city state or national
    state = USStateField(choices=STATE_CHOICES, null=True, blank=True)
    politician_id = models.TextField(max_length=120, blank=True, null=True)
    rank = models.IntegerField(default=1)
    up = models.IntegerField(default=1)
    down = models.IntegerField(default=0)
    upvotes = models.ManyToManyField(User, related_name='open_letter_up')
    downvotes = models.ManyToManyField(User, related_name='open_letter_down')
    tags = models.ManyToManyField(Tag, blank=True, null=True) #only list most common locally in the letter but tag object itself may be more popular
    def __unicode__(self):        return self.title    def save(self, *args, **kwargs):        self.slug = slugify(self.title, instance=self)        super(Open_Letter, self).save(*args, **kwargs) # is this going to be too data intensive? every time it is saved, does it reset the slug name and check for uniqueness?
    def ranking(self):
        n = self.up + self.down
        if n == 0:
        	self.rank = 0
        	self.save()
        z = 1.6 #95% confidence
        phat = float(self.up)/n
        self.rank = sqrt(phat+z*z/(2*n)-z*((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)
        self.save()
        return self.rank

#class Open_Letter_Dynamic(models.Model): #don't need to do this for comments i don't think because won't be accessing them individually very often. what you could do is check the rank of the open_letter vs the live rank and change it if it's super different this can help us save on computing if you make the ol_rank an input into the vote function
	#when sorting on the home page just look through this then can just display 	

class Politician(models.Model): #on ranking system need to have ability to factor ok so give rank of mid and long as ways of weighting your existing stuff down to a baseline score so maybe if number 1 idk but use that and also take into account traffic normal for that time of day
	unique = models.CharField(max_length=200) #slugify city 1st 4 letters and something else
	#slug = models.CharField(primary_key=True, max_length=200) EVENTUALLY DO SLUG
	jurisdiction = models.CharField(max_length=100)#city, state, congress, etc
	user = models.ForeignKey(User, blank=True, null=True)#can say if registered or not, go to their website if not to request
	rank_response = models.IntegerField(default=0)#based on number of letters received and votecount
	rank_trending = models.IntegerField(default = 0)#based on being targeted a lot all of a sudden 
	rank_date = models.DateTimeField(default=datetime.now)
	last_rank = models.IntegerField(default=0)
	last_rank_date = models.DateTimeField(default=datetime.now)
	title = models.CharField(max_length=30)
	first = models.CharField(max_length=60)
	last = models.CharField(max_length=60)
	party = models.CharField(max_length=20)
	district = models.CharField(max_length=20)
	in_office = models.BooleanField()
	address = models.CharField(max_length=100)
	address2 = models.CharField(max_length=100)
	responses = models.IntegerField(default=0)
	phone = models.CharField(max_length=100)
	state = USStateField(choices=STATE_CHOICES)
	city = models.CharField(max_length=100, blank=True, null=True) #only have for city gov
	website = models.URLField(null=True, blank=True)
	twitter = models.URLField(null=True, blank=True)
	facebook = models.URLField(null=True, blank=True)
	photo = models.CharField(max_length=200, null=True, blank=True)
	#committees = models.ManyToManyField(Committee)
	inbox = models.ManyToManyField(Open_Letter, through='Request')
	response_threshold = models.IntegerField(default = 3) #how many requests before they will consider giving a response?
	def __unicode__(self):		return u'%s %s %s' % (self.title, self.last, self.state)
	def response_count(self):
		return Request.objects.filter(politician=self, responses__gte=1).count()  
	def request_count(self):
		return Request.objects.filter(politician=self, upvotes__gte=self.response_threshold, responses=0).count()

#NATIONAL INSTEAD OF CONGRESSMAN

#rank relative to jurisdiction
 
	#def top(self):
	#	return self.inbox_set.all.order_by('-mention__mentions')

#STATE INTEAD OF STATE_LEGISLATOR

class Staff(models.Model): #dif staff w/ dif priveleges
	title = models.CharField(max_length=100)
	priveleges = models.CharField(max_length=100) 
	politician = models.ForeignKey(Politician)
	members = models.ManyToManyField(User, related_name='staff')

class Request(models.Model):	politician = models.ForeignKey(Politician)
	request_date = models.DateTimeField(default=datetime.now)#date the politician is targeted
	upvotes = models.IntegerField(default = 1) #was mentions
	user_requests = models.ManyToManyField(User, related_name='user_requests')
	responses = models.IntegerField(default=0) #number of politician responses	open_letter = models.ForeignKey(Open_Letter)	def __unicode__(self):		return u'%s %s' % (self.upvotes, self.open_letter.title)




#maybe create a class for errors and to signal we need to do a manual import of that politician

#either have inbox include everything and just show stuff w/ over x upvotes or...
#RANK POLITICIANS BY STATUS AND COMMITTEE ESSENTIALY AN INFLUENCE RANKclass Following(models.Model): #ADDED NEW FIELDS	user = models.ForeignKey(User)
	influence = models.IntegerField(default=1) #rank of the user?
	upvotes = models.ManyToManyField(Open_Letter, related_name='upvoted_open_letters') #was called mentions by decentralizing it will let us get the you might also be interested by taking random sampling of upvoters and looking for similar upvotes
	downvotes = models.ManyToManyField(Open_Letter, related_name='downvoted_open_letters')	open_letters = models.ManyToManyField(Open_Letter, blank=True, related_name='follow_open_letters')
	my_letters = models.ManyToManyField(Open_Letter, blank=True, related_name='my_open_letters')
	#town_halls = models.ManyToManyField(Town_Hall, blank=True, related_name='follow_townhalls') #ama and favama related and AMA 
	politicians = models.ManyToManyField(Politician, blank=True, related_name='follow_politicians')#differentiate by jurisdiction?	my_politicians = models.ManyToManyField(Politician, blank=True, related_name='my_politicians')
	users = models.ManyToManyField(User, related_name='follow_user')
	#last_login so can sort openletters by what your most recent login was	def __unicode__(self):		return self.user.username
	def congress(self):
		congressmen = self.politicians.filter(jurisdiction='federal').order_by('-responses')
		return congressmen
	def state(self):
		state_legislators = self.politicians.filter(jurisdiction='state').order_by('-responses')
		return state_legislators
	def local(self):
		local_legislators = self.politicians.filter(jurisdiction='local').order_by('-responses')

class Reply(models.Model): #how to know if it is politician or not	creator = models.ForeignKey(Public_Id)
	creation_date = models.DateTimeField(default=datetime.now) #rank = voters up - down
	rank = models.IntegerField(default=1)
	politician = models.ForeignKey(Politician, blank=True, null=True)
	voters_up = models.ManyToManyField(User, related_name='reply_voters_up')
	voters_down = models.ManyToManyField(User, related_name='reply_voters_down')	abuse = models.IntegerField(default=0)
	spam = models.IntegerField(default=0)
	other = models.TextField(max_length=5000)
	flag = models.IntegerField(default = 0)	flaggers = models.ManyToManyField(User, related_name='reply_flag_vote')	comment = models.TextField(max_length=1000)
	#replies = models.ManyToManyField(Second_Reply, blank = True, related_name='second_replies') #NEW
	#politician_replies = models.ManyToManyField(Politician_Second_Reply, blank=True, related_name='reply_politician_second_replies')	def __unicode__(self):		return self.comment
	
#let politicians publicly like things/comments if they want to?class Comment(models.Model): #how to know if it is politician or not	open_letter = models.ForeignKey(Open_Letter)	creator = models.ForeignKey(Public_Id)
	politician = models.ForeignKey(Politician, blank=True, null=True)
	creation_date = models.DateTimeField(default=datetime.now)	comment = models.TextField(max_length=1000)
	title = models.CharField(max_length=200, blank=True, null=True)
	rank = models.IntegerField(default=1)
	voters_up = models.ManyToManyField(User, related_name='voters_up')#NEED TO ADD COUNT METHOD REDO VOTING METHOD JUST CHECK VOTERS FIRST 
	voters_down = models.ManyToManyField(User, related_name='voters_down')	abuse = models.IntegerField(default=0)
	spam = models.IntegerField(default=0)
	other = models.TextField(max_length=5000)
	flag = models.IntegerField(default = 0)	flaggers = models.ManyToManyField(User, related_name='flag_vote')	replies = models.ManyToManyField(Reply, blank = True, related_name='comment_replies')	def __unicode__(self):		return self.comment
		

#CLASSES FOR POLITICIANS ONLY allow to sort by isue etc
class Politician_Category(models.Model): #for politicians to organize it
	politician = models.ForeignKey(Politician)
	category = models.CharField(max_length=100) #have ability for politicians to grant certain staffers access to certain politician_categories of info
	class Comment_Note(models.Model): #allows politicians to come back to that comment/reply later
	category = models.ForeignKey(Politician_Category, blank=True)
	resolved = models.BooleanField(default=False)
	restrict = models.ManyToManyField(Staff, blank=True, related_name='note_permission')
	comment = models.ForeignKey(Comment, blank=True, related_name='note_comment')
	reply_comment = models.ForeignKey(Reply, blank=True, related_name='note_reply')
	#second_reply_comment = models.ForeignKey(Second_Reply, blank=True, related_name='note_second_reply')
	title = models.CharField(max_length=200, blank=True, null=True)
	note = models.TextField(max_length=2000)
	importance = models.IntegerField(default=0)
	creation_date = models.DateTimeField(default=datetime.now)
	politician = models.ForeignKey(Politician)#only for politicians
