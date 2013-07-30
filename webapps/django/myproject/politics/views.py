# coding: utf-8
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core import serializers
from django import forms
from django.db.models import Q
import shlex, random
from django.template import Context
from django.db.models import Count
from django.template.loader import get_template 
import datetime
import operator
from django.contrib import auth #need below auth ones then?
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import USStateField
from django.core.validators import validate_email
import geopy
from geopy import geocoders
from pygeocoder import Geocoder
from sunlight import congress, openstates
from politics.models import Tag, Rank, Issue, Open_Letter, Politician, Staff, Reply, Comment, Request, Following, Politician_Category, Comment_Note, Email, Public_Id, Volunteer
from login.models import Location
from django.core.mail import send_mail
#from politician.models import Politician, AMA
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from geopy import geocoders
from pygeocoder import Geocoder, GeocoderError


#new accounts views ADD A NEXT OPTION TO SHOW WHERE NEED TO REDIRECT TO
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")
	if request.method == "POST":
		email = request.POST.get('email', '')
		password = request.POST.get('password', '')
		user = auth.authenticate(email=email, password=password)
		if user is not None and user.is_active:
		# Correct password, and the user is marked "active"
			auth.login(request, user)
			# Redirect to a success page.
			return HttpResponseRedirect("/")
		else:
		# Show an error page
			error = "We could not log you in with those credentials"
			return render_to_response("politics/login-register.html",{error:"error"}, context_instance=RequestContext(request))
	else:
		return render_to_response("politics/login-register.html",{}, context_instance=RequestContext(request)) #should do static response here

def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")

def volunteer(request):
	if request.method == "POST":
		name = request.POST["name"]
		email = request.POST["email"]
		phone = request.POST["phone"]
		volunteer = request.POST["volunteer"]
		comments = request.POST["comment"]
		volunteer_signup = Volunteer(name=name, email=email, phone=phone, volunteer=volunteer, comments=comments)
		volunteer_signup.save()	
		send_mail(
    'Thanks for supporting PolitiCrowd!',
    get_template('politics/volunteer_email.html').render(
        Context({
        	'name':name,
            'email': email,
            'volunteer':volunteer
        })
    ),
    'crowd@politicrowd.com',
    [email],
    fail_silently = True
	)
	return HttpResponseRedirect('/about/')

def register_extra_rep(request, unique):
	following = Following.objects.get(user=request.user)
	try:
		politician = Politician.objects.get(unique=unique)
		following.my_politicians.add(politician)
		new_user = True
		return render_to_response("politics/my_politics.html",{"my_politics":following, "new_user":new_user}, context_instance=RequestContext(request))
	except Politician.DoesNotExist:
		return HttpResponse('Error, that id is invalid. Click the back button on your browser.')
	
register_extra_rep = login_required(register_extra_rep)
	


def register(request):
	if request.user.is_authenticated():
		return HttpResponse('logged_in')
	if request.method == "POST":
		email = request.POST.get('email', '')
		password1 = request.POST.get('password1', '')
		password2 = request.POST.get('password2', '')
		first = request.POST.get('first', '')
		last = request.POST.get('last', '')
		zipcode = request.POST.get('zipcode', '')
		politicians = congress.legislators_for_zip(zipcode)
		politician_query = []
		#get user city and state
		geocoder = geocoders.GoogleV3()
		geocoding_results = None
		g = Geocoder()
		geocoding_results = list(geocoder.geocode(zipcode, exactly_one=False))
		split = geocoding_results[0][0].split(',')
		city = split[0]
		state = split[1].split(' ')[1]
		gov = Politician.objects.get(unique='kitzhaber')
		politician_query.append(gov)
		for politician in politicians:
			try:
				to_append = Politician.objects.get(unique=politician['bioguide_id'])
			except Politician.DoesNotExist:
				try:
					address = politician['congress_office']
				except KeyError:
					address = ''
				try:
					phone = politician['phone']
				except KeyError:
					phone = ''
				try:
					website = politician['website']
				except KeyError:
					website = ''
				try:
					twitter = 'http://www.twitter.com/'+politician['twitter_id']
				except KeyError:
					twitter = ''
				try:
					facebook = 'http://www.facebook.com/'+politician['facebook_id']
				except KeyError:
					facebook = ''
				to_append = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'], last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter, facebook=facebook, photo=politician['bioguide_id'])
				to_append.save()
			politician_query.append(to_append)
			
		if password1 == password2:
			try:
				existing = User.objects.get(email__iexact=email)
				error = "That email already exists!"
				return render_to_response("politics/login-register.html",{"error":error}, context_instance=RequestContext(request)) 
			except User.DoesNotExist:
				#if validate_email(email):
				user = User.objects.create_user(username=email, email=email, password=password1)
				user.first_name = first
				user.last_name = last
				user.save()
				user = auth.authenticate(email=email, password=password1)
				if user is not None and user.is_active:
					auth.login(request, user)
					following = Following(user=user)
					following.save()
					public = Public_Id(user=user, first=user.first_name, last=user.last_name, 						city=city, state=state)
					public.save()
					
					content = "Thanks for registering " + request.user.first_name + "!" + " To login, visit http://www.PolitiCrowd.com/login and enter your username,"+ request.user.username + ", and password. Email us with feedback or questions."      
					send_mail("PolitiCrowd registration confirmed", content, 'PolitiCrowd'+'<crowd@politicrowd.com>', [email], fail_silently=True)
					if len(politician_query) == 4:
						for politician in politician_query:
							following.my_politicians.add(politician)
						new_user = True 
						return render_to_response("politics/my_politics.html",{"my_politics":following, "new_user":new_user}, context_instance=RequestContext(request)) 
					confirm = []
					to_save = []
					for politician in politician_query:
						if politician.title == 'Rep':
							confirm.append(politician)
						else:
							to_save.append(politician)
					if len(to_save) != 2:
						for politician in to_save:
							confirm.append(politician)
					else:
						for politician in to_save:
							following.my_politicians.add(politician)		
					return render_to_response("politics/confirm.html",{"confirm":confirm}, context_instance=RequestContext(request)) 
				
				else:
					return HttpResponse('limitless')
				#else:
				#	error = "Invalid Email."
				#	return render_to_response("politics/login-register.html",{error:"error"}, context_instance=RequestContext(request))
		else:
			error = "Passwords do not match"
			return render_to_response("politics/login-register.html",{"error":error}, context_instance=RequestContext(request))
	else:
		return render_to_response("politics/login-register.html",{}, context_instance=RequestContext(request))

def register_location(request):
	if request.is_ajax():
		user = request.user
		first = user.first_name
		last = user.last_name
		latitude = request.GET["latitude"]
		longitude = request.GET["longitude"]
		address = request.GET["address"]
		city = request.GET["city"]
		state = request.GET["state"]
		query = '%s, %s, %s' % (address, city, state)
		#Create new empty user profile (Following)
		following = Following(user=user)
		following.save()
		if latitude:
			location = Location(user = user, first=first, last=last, address='', latitude=latitude, longitude=longitude, city=city, state=state)
			location.save()
			politicians = congress.legislators_for_lat_lon(latitude,longitude)
			
			#empty list of federal/state politicians
			fed_list=[]
			state_list=[]

			#get/create federal politicians
			if len(politicians)==3: #if no extra politicians to choose from
				fed_list=[]
				for politician in politicians:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['congress_office']
						except KeyError:
							address = ''
						try:
							phone = politician['phone']
						except KeyError:
							phone = ''
						try:
							website = politician['website']
						except KeyError:
							website = ''
						try:
							twitter = 'http://www.twitter.com/'+politician['twitter_id']
						except KeyError:
							twitter = ''
						try:
							facebook = 'http://www.facebook.com/'+politician['facebook_id']
						except KeyError:
							facebook = ''
						new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
							last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
							address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter,
							facebook=facebook, photo=politician['bioguide_id']  
							)
						new.save()
						following.my_politicians.add(new)
				#get/create state politicians
			state_legislators = openstates.legislator_geo_search(latitude, longitude)
			if len(state_legislators)==2:		
				for politician in state_legislators:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['offices'][0]['address']
							splits = address.split(",")
							end = len(splits)-2
							address2 = splits[end]+','+splits[end+1]
							address1_length = len(address) - len(address2)
							address1 = address[:address1_length]
						except KeyError:
							address1 = ''
							address2 = ''
						try:
							phone = politician['offices'][0]['phone']
						except KeyError:
							phone = ''
						try:
							website = politician['url']
						except KeyError:
							website = ''
						try:
							photo = politician['photo_url']
						except KeyError:
							photo = ''
						title = politician['chamber']
						if title == 'lower':
							title = 'Rep'
						else:
							title = 'Sen'
						new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
							last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
							address=address1, address2=address2, party=politician['party'], phone=phone, state=state, website=website, photo=photo  
							)
						new.save()
						following.my_politicians.add(new)		
			return HttpResponse('success')
		else:
			try:
				g = Geocoder()
				if g.geocode(query).valid_address:
					location = Location(user = user, first=first, last=last, address=address, city=city, state=state)
					location.save()
					latitude = location.latitude
					longitude = location.longitude
					politicians = congress.legislators_for_lat_lon(latitude,longitude)
					#empty list of federal/state politicians
					fed_list=[]
					state_list=[]
					#get/create federal politicians
					
					if len(politicians)==3: #if no extra politicians to choose from
						fed_list=[]
						for politician in politicians:
							try:
								following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
							except Politician.DoesNotExist:
								try:
									address = politician['congress_office']
								except KeyError:
									address = ''
								try:
									phone = politician['phone']
								except KeyError:
									phone = ''
								try:
									website = politician['website']
								except KeyError:
									website = ''
								try:
									twitter = 'http://www.twitter.com/'+politician['twitter_id']
								except KeyError:
									twitter = ''
								try:
									facebook = 'http://www.facebook.com/'+politician['facebook_id']
								except KeyError:
									facebook = ''
								new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
									last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
									address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter,
									facebook=facebook, photo=politician['bioguide_id']  
									)
								new.save()
								following.my_politicians.add(new)
					
					#get/create state politicians
					state_legislators = openstates.legislator_geo_search(latitude, longitude)
					if len(state_legislators)==2:		
						for politician in state_legislators:
							try:
								following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
							except Politician.DoesNotExist:
								try:
									address = politician['offices'][0]['address']
									splits = address.split(",")
									end = len(splits)-2
									address2 = splits[end]+','+splits[end+1]
									address1_length = len(address) - len(address2)
									address1 = address[:address1_length]
								except KeyError:
									address1 = ''
									address2 = ''
								try:
									phone = politician['offices'][0]['phone']
								except KeyError:
									phone = ''
								try:
									website = politician['url']
								except KeyError:
									website = ''
								try:
									photo = politician['photo_url']
								except KeyError:
									photo = ''
								title = politician['chamber']
								if title == 'lower':
									title = 'Rep'
								else:
									title = 'Sen'
								new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
									last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
									address=address1, address2=address2, party=politician['party'], phone=phone, state=state, website=website, photo=photo  
									)
								new.save()
								following.my_politicians.add(new)
					return HttpResponse('success')
				else:
					return HttpResponse("Invalid Address. Go back to the last screen and try again.")
			except geopy.geocoders.google.GQueryError:
				return HttpResponse("Error, please try again")
	return HttpResponseRedirect("/")#not request.post
register_location = login_required(register_location) 
#end accounts views

#START NEW CODE POST MARKUPBOX

#CREATE OPEN_LETTER:
def submit_1(request):
	issues = Issue.objects.all()
	if 'slug' in request.GET:
		slug = request.GET["slug"]
		try:
			draft = Open_Letter.objects.get(slug=slug)
		except Open_Letter.DoesNotExist:
			draft = ""
		return render_to_response("politics/submit-step1.html",{"issues":issues, "draft":draft}, context_instance=RequestContext(request))
	else:
		return render_to_response("politics/submit-step1.html",{"issues":issues}, context_instance=RequestContext(request))
submit_1 = login_required(submit_1)

def create_draft(request):
	if request.method == "POST":
		title = request.POST["title"]
		issue = request.POST["issue"]
		introduction = request.POST["introduction"]
		slug = request.POST["slug"]
		user = request.user
		creator = Public_Id.objects.get(user=user)
		if slug == "":
			draft = Open_Letter(issue=Issue.objects.get(slug=issue), title=title, introduction=introduction, draft=True, creator=creator)
			draft.save()
			following = Following.objects.get(user=user)
			following.my_letters.add(draft)
			return HttpResponse(draft.slug)
		else:
			try:
				draft = Open_Letter.objects.get(slug=slug)
				draft.title = title
				if draft.issue.slug != issue:
					draft.issue = Issue.objects.get(slug=issue)
				draft.introduction = introduction
				draft.save()
				return HttpResponse(draft.slug)
			except Open_Letter.DoesNotExist:
				return HttpResponse('error')	
	else:
		return HttpResponse('error')

create_draft = login_required(create_draft)

def create_draft1(request):
	if request.method == "POST":
		slug = request.POST["slug"]
		try: 
			draft = Open_Letter.objects.get(slug=slug)
			content = request.POST["content"]
			draft.content = content
			draft.save()
			return HttpResponse('ok')
		except Open_Letter.DoesNotExist:
			return HttpResponse('error')
	return HttpResponse('error')
		
create_draft1 = login_required(create_draft1)

def save_1(request):
	if request.method == "POST":
		title = request.POST["title"]
		issue = request.POST["issue"]
		introduction = request.POST["introduction"]
		slug = request.POST["slug"]
		user = request.user
		creator = Public_Id.objects.get(user=user)
		if slug == "":
			try:
				draft = Open_Letter.objects.get(creator=creator, title=title)
				return render_to_response("politics/submit-step2.html",{"slug":draft.slug, "content":draft.content}, context_instance=RequestContext(request)) 
			except Open_Letter.DoesNotExist:
				draft = Open_Letter(issue=Issue.objects.get(slug=issue), title=title, introduction=introduction, draft=True, creator=creator)
				draft.save()
				slug = draft.slug
				following = Following.objects.get(user=user)
				following.my_letters.add(draft)
				return render_to_response("politics/submit-step2.html",{"slug":slug}, context_instance=RequestContext(request)) 
		else:
			try:
				draft = Open_Letter.objects.get(slug=slug)
				draft.title = title
				if draft.issue.slug != issue:
					draft.issue = Issue.objects.get(slug=issue)
				draft.introduction = introduction
				draft.save()
				slug = draft.slug
				return render_to_response("politics/submit-step2.html",{"slug":slug, "content":draft.content}, context_instance=RequestContext(request)) 
			except Open_Letter.DoesNotExist:
				return HttpResponse('error')	
	else:
		if 'slug' in request.GET:
			slug = request.GET["slug"]
			try:
				open_letter = Open_Letter.objects.get(slug=slug)
				return render_to_response("politics/submit-step2.html",{"content":open_letter.content, "slug":slug}, context_instance=RequestContext(request)) 
			except Open_Letter.DoesNotExist:
				return HttpResponse('error')
		else:
			return HttpResponse('error')
save_1 = login_required(save_1)

def save_2(request):
	if request.method == "POST":
		slug = request.POST["slug"]
		content = request.POST["content"]
		try:
			draft = Open_Letter.objects.get(slug=slug)
			draft.content = content
			draft.save()
			return render_to_response("politics/submit-step3.html",{"slug":slug}, context_instance=RequestContext(request)) 
		except Open_Letter.DoesNotExist:
			return HttpResponse('error')	
	else:
		return HttpResponse('error')
save_2 = login_required(save_2)

def save_3(request):
	if request.method == "POST":
		slug = request.POST["slug"]
		target = ''
		if 'congress' in request.POST:
			target = request.POST["congress"]
		state = ''
		if 'state' in request.POST:
			state = request.POST["state"]
		politician = ''
		if 'politician' in request.POST:
			politician = request.POST["politician"]
		try:	
			open_letter = Open_Letter.objects.get(slug=slug)
			open_letter.target = target
			open_letter.state = state
			open_letter.politician_id = politician
			open_letter.draft = False
			open_letter.save()
		except Open_Letter.DoesNotExist:
			return HttpResponse('error')
		return HttpResponseRedirect('/openletters/'+open_letter.slug+'/')
	return HttpResponse('error')
save_3 = login_required(save_3)

def email_page(request):
	#send_mail('subject', 'message', 'Dont Reply <do_not_replay@domain.com>', ['youremail@example.com'])		
	if request.method == "POST":	
		#slug = request.POST["slug"]
		try:
			if 'politician' in request.POST:
				unique = request.POST["politician"]
				politician = Politician.objects.get(unique=unique)
				email = request.POST["email"]
				if unique == 'test':
					content = "Your friend " + request.user.first_name + " " + "wants you to check out PolitiCrowd, a non-partisan engagement platform to connect you with your politicians. Check the demo page to see what transparent government can look like - http://www.politicrowd.com/demo/politician/"  
					send_mail(request.user.first_name + ' wants to share an OpenLetter on PolitiCrowd with you!', content, request.user.first_name + ' ' + request.user.last_name+'<'+request.user.email+'>', [email], fail_silently=True)
					return HttpResponseRedirect('/demo/politician/')
				content = "Your friend " + request.user.first_name + " " + "wants you to check out " + politician.title + " " + politician.last + "'s" + " profile on PolitiCrowd. Check the link: http://www.politicrowd.com/politicians/" + politician.unique       
				send_mail(request.user.first_name + ' wants to share an OpenLetter on PolitiCrowd with you!', content, request.user.first_name + ' ' + request.user.last_name+'<'+request.user.email+'>', [email], fail_silently=True)
				return HttpResponseRedirect('/politicians/'+unique)
			else:
				slug = request.POST["slug"]
				openletter = Open_Letter.objects.get(slug=slug)
				email = request.POST["email"]
				content = "Your friend " + request.user.first_name + " " + "wants you to check out an OpenLetter on PolitiCrowd related to " + openletter.issue.title + ". Visit the link to view the letter titled: " + openletter.title + ": www.politicrowd.com/openletters/"+openletter.slug+"/."
				return HttpResponseRedirect('/openletters/'+openletter.slug+'/')
		except Politician.DoesNotExist:
			return HttpResponseRedirect('/')

email_page = login_required(email_page)


#Image Upload 
def sideLoad(imgURL):
	img = urllib.quote_plus(imgURL)
	req = urllib2.Request('https://api.imgur.com/3/image', 'image=' + img)
	req.add_header('Authorization', 'Client-ID ' + clientID)
	response = urllib2.urlopen(req)
	response = json.loads(response.read())
	return str(response[u'data'][u'link'])


def home(request):
	open_letters = Open_Letter.objects.all().order_by('-rank')[:25]
	gov = Politician.objects.get(unique='kitzhaber')
	politicians = Politician.objects.all().order_by('-responses').order_by('jurisdiction')[:25]
	return render_to_response("politics/index.html",{"open_letters":open_letters, "politicians":politicians}, context_instance=RequestContext(request))
home = login_required(home)

def my_politics_pagination(request):
	if request.is_ajax():
		try:
			my_politics = Following.objects.get(user=request.user)
			open_letters = my_politics.open_letters.all()
			paginator = Paginator(open_letters, 6)
			page = request.GET.get('page')
			try:
				open_letters = paginator.page(page)
			except PageNotAnInteger:
				open_letters = paginator.page(1)
			except EmptyPage: #out of range deliver last page
				open_letters = paginator.page(paginator.num_pages)
			return render_to_response("politics/letterbox.html",{"open_letters":open_letters}, context_instance=RequestContext(request))
		except Following.DoesNotExist:
			return HttpResponse('error')
	return HttpResponse('ajax')
my_politics_pagination = login_required(my_politics_pagination)

def my_politics(request):
	try:
		my_politics = Following.objects.get(user=request.user)
		open_letters = my_politics.open_letters.all()
		paginator = Paginator(open_letters, 6)
		page = request.GET.get('page')
		following_count = my_politics.politicians.count()+my_politics.my_politicians.count()
		public_id = Public_Id.objects.get(user=request.user)
		issues = my_politics.open_letters.values('issue').annotate(dcount=Count('issue')).order_by('-dcount')
		try:
			open_letters = paginator.page(page)
		except PageNotAnInteger:
			open_letters = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			open_letters = paginator.page(paginator.num_pages)
		location = Location.objects.get(user=request.user)
		return render_to_response("politics/my_politics.html",{"my_politics":my_politics, "open_letters":open_letters, "location":location, "following_count":following_count, "issues":issues, "public_id":public_id}, context_instance=RequestContext(request))
	except Location.DoesNotExist:
		location = ""
		return render_to_response("politics/my_politics.html",{"my_politics":my_politics, "open_letters":open_letters, "location":location, "following_count":following_count, "issues":issues, "public_id":public_id}, context_instance=RequestContext(request))
my_politics = login_required(my_politics)

def update_profile(request):
	if request.method == "POST":
		user = request.user
		email = request.POST["email"]
		password1 = request.POST["password1"]
		password2 = request.POST["password2"]
		if email != user.email:
			try:
				existing = User.objects.get(email__iexact=email)
				error = "That email already exists!"
			except User.DoesNotExist:
				user.email = email
				user.username = email
		if password1 != '':
			if password1 == password2:
				user.set_password(password1)
			else:
				error = "password"
				return render_to_response("politics/my_politics.html",{"error":error}, context_instance=RequestContext(request))
		user.save()
		return HttpResponseRedirect('/profile/')
	return HttpResponse('not post')		
update_profile = login_required(update_profile)

def update_location(request):
	if request.method == "POST":
		user = request.user
		address = request.POST["address"]
		city = request.POST["city"]
		state = request.POST["state"]
		try:
			location = Location.objects.get(user=user)
			location.address = address
			location.city = city
			location.state = state
			location.latitude = ''
			location.longitude = ''
			error = location.save()
			if error == 'address':
				try:
					public = Public_Id.objects.get(user=user)
					public.delete()
					return render_to_response("politics/my_politics.html",{"error":error}, context_instance=RequestContext(request))
				except Public_Id.DoesNotExist:
					return render_to_response("politics/my_politics.html",{"error":error}, context_instance=RequestContext(request)) 
		except Location.DoesNotExist:
			location = Location(address=address, city=city, state=state, user=user)
			error = location.save()
			if error == 'address':
				try:
					public = Public_Id.objects.get(user=user)
					public.delete()
					return render_to_response("politics/my_politics.html",{"error":error}, context_instance=RequestContext(request))
				except Public_Id.DoesNotExist:
					return render_to_response("politics/my_politics.html",{"error":error}, context_instance=RequestContext(request))
		try:
			public = Public_Id.objects.get(user=user)
			public.city = city
			public.state = state
			public.save()
		except Public_Id.DoesNotExist:
			public = Public_Id(user=user, first=user.first_name, last=user.last_name, city=city, state=state)
			public.save()
		latitude = location.latitude
		longitude = location.longitude
		following = Following.objects.get(user=user)
		politicians = congress.legislators_for_lat_lon(latitude, longitude)
		#empty list of federal/state politicians
		following.my_politicians.clear()
		fed_list=[]
		state_list=[]
		#get/create federal politicians
		if len(politicians)==3: #if no extra politicians to choose from
			fed_list=[]
			for politician in politicians:
				try:
					following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
				except Politician.DoesNotExist:
					try:
						address = politician['congress_office']
					except KeyError:
						address = ''
					try:
						phone = politician['phone']
					except KeyError:
						phone = ''
					try:
						website = politician['website']
					except KeyError:
						website = ''
					try:
						twitter = 'http://www.twitter.com/'+politician['twitter_id']
					except KeyError:
						twitter = ''
					try:
						facebook = 'http://www.facebook.com/'+politician['facebook_id']
					except KeyError:
						facebook = ''
					new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
						last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
						address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter,
						facebook=facebook, photo=politician['bioguide_id']  
						)
					new.save()
					following.my_politicians.add(new)
					#get/create state politicians
		state_legislators = openstates.legislator_geo_search(latitude, longitude)
		if len(state_legislators)==2:		
			for politician in state_legislators:
				try:
					following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
				except Politician.DoesNotExist:
					try:
						address = politician['offices'][0]['address']
						splits = address.split(",")
						end = len(splits)-2
						address2 = splits[end]+','+splits[end+1]
						address1_length = len(address) - len(address2)
						address1 = address[:address1_length]
					except KeyError:
						address1 = ''
						address2 = ''
					try:
						phone = politician['offices'][0]['phone']
					except KeyError:
						phone = ''
					try:
						website = politician['url']
					except KeyError:
						website = ''
					try:
						photo = politician['photo_url']
					except KeyError:
						photo = ''
					title = politician['chamber']
					if title == 'lower':
						title = 'Rep'
					else:
						title = 'Sen'
					new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
						last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
						address=address1, address2=address2, party=politician['party'], phone=phone, state=state, website=website, photo=photo  
						)
					new.save()
					following.my_politicians.add(new)	
		return HttpResponseRedirect('/profile/')
update_location = login_required(update_location)


def my_politics_letters(request):
	following = Following.objects.get(user=request.user)
	if request.is_ajax():
		target = ''
		if 'target' in request.GET:
			target = request.GET["target"]
			if target == 'All':
				open_letters = following.open_letters.all()
			if target == 'State':
				open_letters = following.open_letters.filter(target='State')
			if target == 'Congress':
				open_letters = following.open_letters.filter(target='Congress')
			if target == 'Submissions':
				open_letters = following.my_letters.all()
		else:
			open_letters = following.open_letters.all()
		paginator = Paginator(open_letters, 6)
		page = request.GET.get('page')
		try:
			open_letters = paginator.page(page)
		except PageNotAnInteger:
			open_letters = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			open_letters = paginator.page(paginator.num_pages)
		
		return render_to_response("politics/letterbox.html",{"open_letters":open_letters, "target":target}, context_instance=RequestContext(request))
	return HttpResponse('error')
my_politics_letters = login_required(my_politics_letters)

def polilist(request):
	if request.is_ajax():
		politicians = request.GET["politicians"]
		HttpResponse(politicians)
		following = Following.objects.get(user=request.user)
		if politicians == 'mine':
			politicians = following.my_politicians.all()
		if politicians == 'All':
			politicians = following.politicians.all()
		if politicians == 'Congress':
			politicians = following.politicians.filter(jurisdiction='federal')
		if politicians == 'state':
			politicians = following.politicians.filter(jurisdiction='state')
		return render_to_response("politics/politician_slider.html",{"politicians":politicians},context_instance=RequestContext(request))
	return HttpResponse('soemthing iss wrong')
polilist = login_required(polilist)


def load_letters(request):
	if request.is_ajax():
		
		if 'issue' in request.GET:
			issue = request.GET["issue"]
			
		else:
			issue = ''
		try:
			issue = Issue.objects.get(title=issue)
		except Issue.DoesNotExist:
			issue = ''
		if 'target' in request.GET:
			target = request.GET["target"]
			
		else:
			target = 'All'
		if target == 'All':
			if issue != '':
				open_letters = Open_Letter.objects.filter(issue=issue).order_by('-rank')
			else:
				open_letters = Open_Letter.objects.all().order_by('-rank')
		else:
			if issue != '':
				open_letters = Open_Letter.objects.filter(target=target, issue=issue).order_by('-rank')
			else:
				open_letters = Open_Letter.objects.filter(target=target).order_by('-rank')
		
		paginator = Paginator(open_letters, 6)
		page = request.GET.get('page')
		try:
			open_letters = paginator.page(page)
		except PageNotAnInteger:
			open_letters = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			open_letters = paginator.page(paginator.num_pages)
	
	return render_to_response("politics/letterbox_issues.html",{"open_letters":open_letters, "issue":issue, "target":target},context_instance=RequestContext(request))
#return HttpResponse('soemthing went wrong')
load_letters = login_required(load_letters)


def letter_box(request):
	if request.is_ajax():
		if 'target' in request.GET:
			target = request.GET["target"]
		else:
			target = 'All'
		if target == 'All':
			open_letters = Open_Letter.objects.all().order_by('-rank')
		else:
			open_letters = Open_Letter.objects.filter(target=target).order_by('-rank')
		issues = open_letters.values('issue').annotate(dcount=Count('issue')).order_by('-dcount')
		paginator = Paginator(open_letters, 6)
		page = request.GET.get('page')
		try:
			open_letters = paginator.page(page)
		except PageNotAnInteger:
			open_letters = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			open_letters = paginator.page(paginator.num_pages)
		
		return render_to_response("politics/letter_box.html",{"open_letters":open_letters, "issues":issues,"target":target},context_instance=RequestContext(request))
	return HttpResponse('soemthing went wrong')
letter_box = login_required(letter_box)



def open_letter(request, slug):
	try:
		try:
			politician = Politician.objects.get(user=request.user)
		except Politician.DoesNotExist:
			politician = None
		open_letter = Open_Letter.objects.get(slug=slug)
		requests = Request.objects.filter(open_letter=open_letter, politician__isnull = False, upvotes__gte=1).order_by('-upvotes')
		politician_comments = Comment.objects.filter(open_letter=open_letter, politician__isnull = False).order_by('-rank')
		comments = Comment.objects.filter(open_letter=open_letter, politician = None).order_by('-rank')
		return render_to_response("politics/openletter.html",{"politician":politician, "politician_comments":politician_comments, "open_letter":open_letter, "requests":requests, "comments":comments}, context_instance=RequestContext(request))
	except Open_Letter.DoesNotExist:
		raise Http404('Page Not Found')
	except Public_Id.DoesNotExist:
		return HttpResponseRedirect('/profile/')

def load_comments(request, target, slug):
	if request.is_ajax():
		open_letter = Open_Letter.objects.get(slug=slug)
		if target == 'All':
			comments = Comment.objects.filter(open_letter=open_letter).order_by('-upvotes')
		else:
			if target == 'Contributors':
				comments = Comment.objects.filter(open_letter=open_letter, creator__politician__isnull=True)
			else:
				if target == 'Politicians':
					comments = Comment.objects.filter(open_letter=open_letter).exclude(creator__politician__isnull=True)
		return render_to_response("politics/comments.html",{"comments":comments}, context_instance=RequestContext(request))
	return HttpResponse(target)
load_comments = login_required(load_comments)

#open_letter voting

def open_letter_up(request):
	if request.is_ajax():
		if 'slug' in request.GET:
			slug = request.GET['slug']
			try:
				open_letter = Open_Letter.objects.get(slug=slug)
				user = request.user
				username = user.username
				down = open_letter.downvotes.filter(email=request.user.email)
				if not down:
					up = open_letter.upvotes.filter(email=request.user.email)
					if not up:
						open_letter.upvotes.add(user)
						open_letter.up+=1
						open_letter.save()
						return HttpResponse("1")
					else:
						open_letter.upvotes.remove(user)
						return HttpResponse("0") #removedvote
				else:
					open_letter.downvotes.remove(user)
					open_letter.upvotes.add(user)
					open_letter.down-=1
					open_letter.up+=1
					open_letter.save()
					return HttpResponse("2")
			except Open_Letter.DoesNotExist:
				raise Http404('Page Not Found')
		return HttpResponse("error2")
	return HttpResponse("ajax error")
open_letter_up = login_required(open_letter_up)

def open_letter_down(request):
	if request.is_ajax():
		if 'slug' in request.GET:
			slug = request.GET['slug']
			try:
				open_letter = Open_Letter.objects.get(slug=slug)
				user = request.user
				username = user.username
				up = open_letter.upvotes.filter(email=request.user.email)
				if not up:
					down = open_letter.downvotes.filter(email=request.user.email)
					if not down:
						open_letter.downvotes.add(user)
						open_letter.down+=1
						return HttpResponse("1")
					else:
						open_letter.downvotes.remove(user)
						return HttpResponse("0") #removedvote
				else:
					open_letter.upvotes.remove(user)
					open_letter.downvotes.add(user)
					open_letter.up-=1
					open_letter.down+=1
					open_letter.save()
					return HttpResponse("2")
			except Open_Letter.DoesNotExist:
				raise Http404('Page Not Found')
		return HttpResponse("error2")
	return HttpResponse("ajax error")
open_letter_down = login_required(open_letter_down)

def report(request, id, slug):
	if request.method == "POST":
		try:	
			comment = Comment.objects.get(id=id)
			user_voted = comment.flaggers.filter(username=request.user.username)
			if not user_voted:
				for option in request.POST.getlist('checkbox1'):
					if option == 'spam':
						comment.spam+=1
					else:
						if option == 'abuse':
							comment.abuse+=1
						else:
							if option == 'other':
								other = request.POST['other']
								if other != '':
									comment.other+="---"+other
				comment.flag+=1
				comment.flaggers.add(request.user)
				comment.save()
							
			return HttpResponseRedirect("/openletters/" + slug + "/")
					
		except Comment.DoesNotExist:
			raise Http404('Comment not Found.')
	return HttpResponseRedirect("/openletters/" + slug + "/")
report = login_required(report)

def report_reply(request, id, slug):
	if request.method == "POST":
		try:	
			reply = Reply.objects.get(id=id)
			user_voted = reply.flaggers.filter(username=request.user.username)
			if not user_voted:
				for option in request.POST.getlist('checkbox1'):
					if option == 'spam':
						reply.spam+=1
					else:
						if option == 'abuse':
							reply.abuse+=1
						else:
							if option == 'other':
								other = request.POST['other']
								if other != '':
									reply.other+="---"+other
				reply.flag+=1
				reply.flaggers.add(request.user)
				reply.save()
							
			return HttpResponseRedirect("/openletters/" + slug + "/")
					
		except Reply.DoesNotExist:
			raise Http404('Reply not Found.')
	return HttpResponseRedirect("/openletters/" + slug + "/")
report_reply = login_required(report_reply)





def request_politician(request, slug):
	if request.is_ajax():
		try:
			politicians_all = Following.objects.get(user=request.user)
			open_letter = Open_Letter.objects.get(slug=slug)
			politicians = []
			if open_letter.target == 'Congress':
				politicians = politicians_all.my_politicians.filter(jurisdiction='federal')
				return render_to_response("politics/request_politicians.html", {"politicians":politicians, "slug":slug}, context_instance=RequestContext(request))
			else:
				if open_letter.target == 'State':
					politicians = politicians_all.my_politicians.filter(jurisdiction='state', state=open_letter.state)
					return render_to_response("politics/request_politicians.html", {"politicians":politicians, "slug":slug}, context_instance=RequestContext(request))
				else:
					if open_letter.target == 'Politician':
						politicians = politicians_all.my_politicians.filter(unique=open_letter.politician_id)
						return render_to_response("politics/request_politicians.html", {"politicians":politicians, "slug":slug}, context_instance=RequestContext(request))
		
				
			return render_to_response("politics/request_politicians.html", {"politicians":politicians, "slug":slug}, context_instance=RequestContext(request))
		except Following.DoesNotExist:
			return HttpResponse("Error with user address") 
		
	return HttpResponse('ajax')
request_politician = login_required(request_politician)

def politician_search(request, slug):
	if request.is_ajax():
		if 'search' in request.GET:
			search = request.GET['search'].strip()
			
			search = search.split(' ')
		
			if len(search) >1:
				error = "Please try your search again - search by last name or state"
				return render_to_response("politics/request_success.html",{"error":error},context_instance=RequestContext(request))
			else:
				try:
					open_letter = Open_Letter.objects.get(slug=slug)
					requests = Request.objects.filter(open_letter=open_letter, politician__state__iexact=search[0])
					if not requests:
						requests = Request.objects.filter(open_letter=open_letter, politician__last__iexact=search[0])
					return render_to_response("politics/politician_search.html",{"requests":requests},context_instance=RequestContext(request))
				except Open_Letter.DoesNotExist:
					return HttpResponse("2")
			return HttpResponse("3")
		return HttpResponse("4")
	return HttpResponse("5")
politician_search = login_required(politician_search)
				


def request_response(request, slug):	
	if request.is_ajax():	
		try:
			open_letter = Open_Letter.objects.get(slug=slug)
			if 'selected' in request.GET:
				politician_ids = request.GET['selected']
				clean_ids = politician_ids.split(",")
				clean_ids = clean_ids[0:len(clean_ids)-1]
				requests = []
		
				for politician_id in clean_ids:
					politician = Politician.objects.get(unique=politician_id)
			
					try:	
						new_request = Request.objects.get(politician=politician, open_letter=open_letter)
						voted = new_request.user_requests.filter(email=request.user.email) 
						if not voted:
							new_request.upvotes +=1
							new_request.save()
							new_request.user_requests.add(request.user)
							requests.append(new_request)
					except Request.DoesNotExist:
						new_request = Request(politician=politician, open_letter=open_letter)
						new_request.save()
						new_request.user_requests.add(request.user)
						requests.append(new_request)
				error = "Nothing to see here. You already requested a response or didn't make a selection. Try again!"
				return render_to_response("politics/request_success.html",{"requests":requests, "error":error},context_instance=RequestContext(request))
			else:
				return HttpResponse("2")
		except:
			return HttpResponse("0")
	return HttpResponse("12")
request_response = login_required(request_response)

def add_party(request):
	state_politicians = openstates.legislators(state='OR')
	for politician in state_politicians:
		finder = Politician.objects.get(unique=politician['leg_id'])
		finder.party = politician['party']
		finder.save()
	return HttpResponseRedirect('/')
	

def add_politicians(request, state):
	try:
		state_politicians = openstates.legislators(state=state)
		congress_politicians = congress.legislators(state=state)
		for politician in congress_politicians:
			try:
				politician = Politician.objects.get(unique=politician['bioguide_id'])
			except Politician.DoesNotExist:
				try:
					address = politician['congress_office']
				except KeyError:
					address = ''
				try:
					phone = politician['phone']
				except KeyError:
					phone = ''
				try:
					website = politician['website']
				except KeyError:
					website = ''
				try:
					twitter = 'http://www.twitter.com/'+politician['twitter_id']
				except KeyError:
					twitter = ''
				try:
					facebook = 'http://www.facebook.com/'+politician['facebook_id']
				except KeyError:
					facebook = ''
				politician = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'], last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter, facebook=facebook, photo=politician['bioguide_id'])
				politician.save()
		for politician in state_politicians:
			try:
				politician = Politician.objects.get(unique=politician['leg_id'])
			except Politician.DoesNotExist:
				try:
					address = politician['offices'][0]['address']
					splits = address.split(",")
					end = len(splits)-2
					address2 = splits[end]+','+splits[end+1]
					address1_length = len(address) - len(address2)
					address1 = address[:address1_length]
				except KeyError:
					address1 = ''
					address2 = ''
				try:
					phone = politician['+phone']
				except KeyError:
					phone = ''
				try:
					website = politician['url']
				except KeyError:
					website = ''
				try:
					photo = politician['photo_url']
				except KeyError:
					photo = ''
				title = politician['chamber']
				if title == 'lower':
					title = 'Rep'
				else:
					title = 'Sen'
				politician = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
					last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
					address=address1, address2=address2, phone=phone, state=state,
					website=website, photo=photo, party=politician['party'] 
					)
				politician.save()
		return HttpResponseRedirect('/')
	except:
		return HttpResponseRedirect('/')
	add_politicians = login_required(add_politicians)

	



def politician_profile(request, unique):
	try:
		politician = Politician.objects.get(unique=unique)
		open_letters = Request.objects.filter(politician=politician, upvotes__gte=politician.response_threshold, responses=0).order_by('-upvotes')
		unread_count = open_letters.count()
		responded_count = Request.objects.filter(politician=politician, responses__gte=1).count()
		issues = open_letters.values('open_letter__issue').annotate(dcount=Count('open_letter__issue')).order_by('-dcount')
		paginator = Paginator(open_letters, 6)
		page = request.GET.get('page')
		try:
			open_letters = paginator.page(page)
		except PageNotAnInteger:
			open_letters = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			open_letters = paginator.page(paginator.num_pages)
			
		responses = Request.objects.filter(politician=politician, responses__gte=1)
		response_issues = responses.values('open_letter__issue').annotate(dcount=Count('open_letter__issue')).order_by('-dcount')
		paginator = Paginator(responses, 6)
		page = request.GET.get('page')
		try:
			responses = paginator.page(page)
		except PageNotAnInteger:
			responses = paginator.page(1)
		except EmptyPage: #out of range deliver last page
			responses = paginator.page(paginator.num_pages)
		
		return render_to_response("politics/politician_profile.html",{"politician":politician, "open_letters":open_letters, "responded_count":responded_count, "issues":issues, "unread_count":unread_count, "responses":responses, "response_issues":response_issues},context_instance=RequestContext(request))
	except Politician.DoesNotExist:
		raise Http404('Page Not Found')
politician_profile = login_required(politician_profile)

def load_politician_letters(request):
	if request.is_ajax():
		
		try:
			unique = request.GET["unique"]
			target = request.GET["target"]
			politician = Politician.objects.get(unique=unique)
			return HttpResponse(politician)
			if target == 'requested':
				open_letters = Request.objects.filter(politician=politician, upvotes__gte=politician.response_threshold).order_by('-upvotes')
				issues = open_letters.values('open_letter__issue').annotate(dcount=Count('open_letter__issue')).order_by('-dcount')
			else:	
				open_letters = Request.objects.filter(politician=politician, responses__gte=1).order_by('-upvotes')
				issues = open_letters.values('open_letter__issue').annotate(dcount=Count('open_letter__issue')).order_by('-dcount')
			paginator = Paginator(open_letters, 6)
			page = request.GET.get('page')
			try:
				open_letters = paginator.page(page)
			except PageNotAnInteger:
				open_letters = paginator.page(1)
			except EmptyPage: #out of range deliver last page
				open_letters = paginator.page(paginator.num_pages)
			return render_to_response("politics/letter_container_politicians.html",{"open_letters":open_letters, "issues":issues},context_instance=RequestContext(request))
		except:
			raise Http404('Page Not Found')
		raise Http404('You cannot access this view without Ajax.')
load_politician_letters = login_required(load_politician_letters)

		



def letterbox_politician(request): #returns list of openletters by issue
	if request.is_ajax():
		try:
			politician_id = request.GET["politician"]
			issue = request.GET["issue"]
			target = request.GET["target"]
			#response = request.GET["
			politician = Politician.objects.get(unique=politician_id)
			if issue == 'all': #need to do query on request object so can get number of requests etc
				if target == 'requested':
					open_letters = Request.objects.filter(politician=politician, upvotes__gte=politician.response_threshold, responses=0).order_by('-upvotes')
				else:
					open_letters = Request.objects.filter(politician=politician, responses__gte=1).order_by('-upvotes')
				
			else:
				issue = Issue.objects.get(title__iexact=issue)
				if target == 'requested':
					open_letters = Request.objects.filter(politician=politician, open_letter__issue=issue, upvotes__gte=politician.response_threshold, responses=0).order_by('-upvotes') #should show how many requested their response not how many votes it got. 		
				else:
					open_letters = Request.objects.filter(politician=politician, open_letter__issue=issue, responses__gte=1).order_by('-upvotes')	
			
			paginator = Paginator(open_letters, 6)
			page = request.GET.get('page')
			try:
				open_letters = paginator.page(page)
			except PageNotAnInteger:
				open_letters = paginator.page(1)
			except EmptyPage: #out of range deliver last page
				open_letters = paginator.page(paginator.num_pages)

			return render_to_response("politics/letterbox_politician.html",{"open_letters":open_letters},context_instance=RequestContext(request))
		except:
			return HttpResponse('error')
		return HttpResponse('no')
	return HttpResponse('nooo')
letterbox_politician = login_required(letterbox_politician)

def letterbox_issue(request):
	if request.is_ajax():
		
		try:
			issue = request.GET["issue"]
			if issue == 'all':
				open_letters = Open_Letter.objects.all()
			else:
				open_letters = Open_Letter.objects.filter(issue__title=issue)
			paginator = Paginator(open_letters, 6)
			page = request.GET.get('page')
			try:
				open_letters = paginator.page(page)
			except PageNotAnInteger:
				open_letters = paginator.page(1)
			except EmptyPage: #out of range deliver last page
				open_letters = paginator.page(paginator.num_pages)
			return render_to_response("politics/letterbox_issue.html",{"open_letters":open_letters, "issue":issue},context_instance=RequestContext(request))
		except:
			return HttpResponse('error')
		return HttpResponse('error')
	return HttpResponse('error')

letterbox_issue = login_required(letterbox_issue)

def open_letter_sort(request):
	if request.is_ajax():
		try:
			politician_id = request.GET["politician"]
			politician = Politician.objects.get(unique=politician_id)
			sort_by = request.GET["sortby"]
			if sort_by == 'New':
				requests = Request.objects.filter(politician=politician).order_by('-request_date')
			else:
				if sort_by == 'Top':
					requests = Request.objects.filter(politician=politician).order_by('-upvotes')
				#else:
				#	if sort_by == 'Trending':
				#		requests = Request.objects.filter(politician=politician).order_by('-rank')
			return render_to_response("politics/letterbox.html",{"requests":requests},context_instance=RequestContext(request))
		except:
			return HttpResponse('something went wrong')
		return HttpResponse('soemthing iss wrong')
	return HttpResponse('oops')
				
open_letter_sort = login_required(open_letter_sort)

def follow_politician(request):
	if request.is_ajax():
		try:
			politician_id = request.GET["politician_id"]
			politician = request.GET["politician"]
			following = Following.objects.get(user=request.user)
			exist = following.politicians.filter(unique=politician_id)
			if not exist:
				politician = Politician.objects.get(unique=politician_id)
				following.politicians.add(politician)
				return HttpResponse("Successfully added to your My Politics page!")
			else:
				return HttpResponse("You are already following " + politician)
		except Following.DoesNotExist:
			return HttpResponse("Something's wrong with your profile.")
		except:
			return HttpResponse("Error.")
	return HttpResponse("Need Ajax")
follow_politician = login_required(follow_politician)

def follow_open_letter(request):
	if request.is_ajax():
		try:
			slug = request.GET["slug"]
			following = Following.objects.get(user=request.user)
			exist = following.open_letters.filter(slug=slug)
			if not exist:
				open_letter = Open_Letter.objects.get(slug=slug)
				following.open_letters.add(open_letter)
				return HttpResponse("Successfully added to your favorites.")
			else:
				return HttpResponse("0")
		except:
			return HttpResponse("You are already following this OpenLetter.")
	return HttpResponse("No linking here.")
follow_open_letter = login_required(follow_open_letter)





def email(request):
	if request.method == "POST":	
		email = request.POST["email"]
		newmail = Email(email=email)
		#lists = mailchimp.utils.get_connection().get_list_by_id('6768db2972')
		#lists.subscribe(email, {'EMAIL':email})
		newmail.save()
		
		
		send_mail(
    'Thanks for supporting PolitiCrowd!',
    get_template('politics/email.html').render(
        Context({
            'email': email
        })
    ),
    'crowd@politicrowd.com',
    [email],
    fail_silently = True
)
	return render_to_response("registration/login.html", {'email':email}, context_instance=RequestContext(request))

def save_comment(request, slug):
	try:
		title = request.POST["title"]
		if title == 'Add a title to a long comment':
			title = ''
		comment = request.POST["comment"]
		user = request.user
		creator = Public_Id.objects.get(user=user)
		open_letter = Open_Letter.objects.get(slug=slug)
		if 'politician' in request.POST:
			is_politician = request.POST["politician"]
			if is_politician == 'ok':
				try:
					politician = Politician.objects.get(user=user)	
					request = Request.objects.get(politician=politician, open_letter=open_letter)
					request.responses+=1
					request.save()
					open_letter.responses+=1
					politician.responses+=1
					politician.save()
					open_letter.save()
					
				except Politician.DoesNotExist:
					politician = None
				comment = Comment(title=title, politician=politician, comment = comment, open_letter=open_letter, creator=creator)
				comment.save()
		else:
			comment = Comment(title=title, comment = comment, open_letter=open_letter, creator=creator)
			comment.save()
			
		comment.voters_up.add(user)
		contributor = open_letter.contributors.filter(username=user.username)
		if not contributor:
			open_letter.contributors.add(user)
		return HttpResponseRedirect("/openletters/"+slug+"/")
	except Open_Letter.DoesNotExist:
		raise Http404('Page not Found')
	return HttpResponse("1")
save_comment = login_required(save_comment)

def comment_up(request):
	if request.is_ajax():
		user = request.user
		try:
			comment_id = request.GET["comment_id"]
			comment = Comment.objects.get(id=comment_id)
			down = comment.voters_down.filter(email=user.email)
			if not down:
				up = comment.voters_up.filter(email=user.email)
				if not up:
					comment.voters_up.add(user)
					comment.rank+=1
					comment.save()
					return HttpResponse("1")
				else:
					comment.voters_up.remove(user)
					comment.rank-=1
					comment.save()
					return HttpResponse("0")
			else:
				comment.voters_down.remove(user)
				comment.voters_up.add(user)
				comment.rank+=2
				comment.save()
				return HttpResponse("2")
		except Comment.DoesNotExist:
			raise Http404('Comment not Found')
	return HttpResponse("2")
comment_up = login_required(comment_up)

def reply_up(request):
	if request.is_ajax():
		user = request.user
		try:
			reply_id = request.GET["reply_id"]
			reply = Reply.objects.get(id=reply_id)
			down = reply.voters_down.filter(email=user.email)
			if not down:
				up = reply.voters_up.filter(email=user.email)
				if not up:
					reply.voters_up.add(user)
					reply.rank+=1
					reply.save()
					return HttpResponse("1")
				else:
					reply.voters_up.remove(user)
					reply.rank-=1
					reply.save()
					return HttpResponse("0")
			else:
				reply.voters_down.remove(user)
				reply.voters_up.add(user)
				reply.rank+=2
				reply.save()
				return HttpResponse("2")
		except Reply.DoesNotExist:
			raise Http404('reply not Found')
	return HttpResponse("2")
reply_up = login_required(reply_up)


def comment_down(request):
	if request.is_ajax():
		user = request.user
		try:
			comment_id = request.GET["comment_id"]
			comment = Comment.objects.get(id=comment_id)
			up = comment.voters_up.filter(email=user.email)
			if not up:
				down = comment.voters_down.filter(email=user.email)
				if not down:
					comment.voters_down.add(user)
					comment.rank-=1
					comment.save()
					return HttpResponse("1")
				else:
					comment.voters_down.remove(user)
					comment.rank+=1
					comment.save()
					return HttpResponse("0")
			else:
				comment.voters_up.remove(user)
				comment.voters_down.add(user)
				comment.rank-=2
				comment.save()
				return HttpResponse("2")
		except Comment.DoesNotExist:
			raise Http404('Comment not Found')
	return HttpResponse("2")
comment_down = login_required(comment_down)

def reply_down(request):
	if request.is_ajax():
		user = request.user
		try:
			reply_id = request.GET["reply_id"]
			reply = Reply.objects.get(id=reply_id)
			up = reply.voters_up.filter(email=user.email)
			if not up:
				down = reply.voters_down.filter(email=user.email)
				if not down:
					reply.voters_down.add(user)
					reply.rank-=1
					reply.save()
					return HttpResponse("1")
				else:
					reply.voters_down.remove(user)
					reply.rank+=1
					reply.save()
					return HttpResponse("0")
			else:
				reply.voters_up.remove(user)
				reply.voters_down.add(user)
				reply.rank-=2
				reply.save()
				return HttpResponse("2")
		except Reply.DoesNotExist:
			raise Http404('reply not Found')
	return HttpResponse("2")
reply_down = login_required(reply_down)

def open_letter_up(request):
	if request.is_ajax():
		if 'slug' in request.GET:
			slug = request.GET['slug']
			try:
				open_letter = Open_Letter.objects.get(slug=slug)
				user = request.user
				username = user.username
				down = open_letter.downvotes.filter(email=request.user.email)
				if not down:
					up = open_letter.upvotes.filter(email=request.user.email)
					if not up:
						open_letter.upvotes.add(user)
						return HttpResponse("1")
					else:
						open_letter.upvotes.remove(user)
						return HttpResponse("0") #removedvote
				else:
					open_letter.downvotes.remove(user)
					open_letter.upvotes.add(user)
					return HttpResponse("2")
			except Open_Letter.DoesNotExist:
				raise Http404('Page Not Found')
		return HttpResponse("error2")
	return HttpResponse("ajax error")
open_letter_up = login_required(open_letter_up)



def save_reply(request, slug, comment_id): #for reply and comment need to have separate save for politician because too many hits to database to always check if the person is a politician or not. 
	try:
		reply = request.POST["reply"]
		user = request.user
		creator = Public_Id.objects.get(user=user)
		comment = Comment.objects.get(id=comment_id)
		try:
			politician = Politician.objects.get(user=user)
		except Politician.DoesNotExist:
			politician = None
		reply = Reply(comment=reply, politician=politician, creator=creator)
		reply.save()
		reply.voters_up.add(user)
		open_letter = Open_Letter.objects.get(slug=slug)
		contributor = open_letter.contributors.filter(username=user.username)
		if not contributor:
			open_letter.contributors.add(user)
		comment.replies.add(reply)
		comment.rank += 1
		comment.save()
		return HttpResponseRedirect("/openletters/"+slug+"/")
	except Comment.DoesNotExist:
		raise Http404('Comment not Found')
	return HttpResponse("1")
save_reply = login_required(save_reply)

def issues(request):
	open_letters = Open_Letter.objects.all().order_by('-rank')
	
	issues = open_letters.values('issue').annotate(dcount=Count('issue')).order_by('-dcount')
	paginator = Paginator(open_letters, 6)
	page = request.GET.get('page')
	try:
		open_letters = paginator.page(page)
	except PageNotAnInteger:
		open_letters = paginator.page(1)
	except EmptyPage: #out of range deliver last page
		open_letters = paginator.page(paginator.num_pages)
	return render_to_response("politics/issues.html", {"open_letters":open_letters, "issues":issues}, context_instance=RequestContext(request))
issues = login_required(issues)

def issues_pagination(request):
	if request.is_ajax():
		try:
			open_letters = Open_Letter.objects.all()
			paginator = Paginator(open_letters, 6)
			page = request.GET.get('page')
			try:
				open_letters = paginator.page(page)
			except PageNotAnInteger:
				open_letters = paginator.page(1)
			except EmptyPage: #out of range deliver last page
				open_letters = paginator.page(paginator.num_pages)
			return render_to_response("politics/letterbox.html",{"open_letters":open_letters}, context_instance=RequestContext(request))
		except Following.DoesNotExist:
			return HttpResponse('error')
	return HttpResponse('ajax')

issues_pagination = login_required(issues_pagination)


def politicians(request):
	congress = Politician.objects.filter(jurisdiction='federal')
	state = Politician.objects.filter(jurisdiction='state')
	return render_to_response("politics/politicians.html",{"congress":congress, "state":state}, context_instance=RequestContext(request))
politicians = login_required(politicians)
#END NEW CODE POST MARKUPBOX




#maybe just have them debate issue and forget the title and such, can have multiple issue pages. makes it less cluttered. allow to submit youtube/link in comments but the comments are the focus so minimize the step to get conversation going. 

#maybe just have them debate issue and forget the title and such, can have multiple issue pages. makes it less cluttered. allow to submit youtube/link in comments but the comments are the focus so minimize the step to get conversation going. 

#get people to click on promoted pages by giving them 50% of the profits to donate to any project of their choice on the site w/ no service fee or advertise an idea -> verify so no fraud


#maybe just have them debate issue and forget the title and such, can have multiple issue pages. makes it less cluttered. allow to submit youtube/link in comments but the comments are the focus so minimize the step to get conversation going. 

#develop functions to retrieve best comments etc or store in issue name
#def global_view(request):
#	#top auto, request just trending/auto in separate view javascript request.
#	issues = Issue.objects.all().order_by('-rank')
#	open_letters = Open_Letter.objects.filter(target='Congress').order_by('-rank')[:15]
#	return render_to_response("politics/home.html", {"issues":issues, "open_letters":open_letters}, context_instance=RequestContext(request))
#
#global_view = login_required(global_view)

def congress_letters(request):
	open_letters = Open_Letter.objects.filter(target='Congress').order_by('-rank')[:15]
	return render_to_response("politics/letters_list.html", {"open_letters":open_letters}, context_instance=RequestContext(request))

congress_letters = login_required(congress_letters)

def state(request, state):
	open_letters = Open_Letter.objects.filter(state=state).order_by('-rank')[:15]
	return render_to_response("politics/letters_list.html", {"open_letters":open_letters}, context_instance=RequestContext(request))
state = login_required(state)

def my_view(request):
	try: #fix location and mypolitician .get so it's more efficient
			location = Location.objects.get(user=request.user)
	except Location.MultipleObjectsReturned:
			location = Location.objects.filter(user=request.user)[0]
	except Location.DoesNotExist:
		states = STATE_CHOICES
		return render_to_response("politics/address.html",{},context_instance=RequestContext(request))
	latitude = location.latitude
	longitude = location.longitude
	politicians = congress.legislators_for_lat_lon(latitude,longitude)[:3]
	state_reps = openstates.legislator_geo_search(latitude, longitude)[:2]
	state = location.state
	return render_to_response("politics/politician_list.html", {"politicians":politicians, "state_reps":state_reps, "state":state}, context_instance=RequestContext(request))	
my_view = login_required(my_view)


def search_issues(request):
	issues = []
	if 'query' in request.GET:
		query = request.GET['query'].strip()
		if query:
			issues = Issue.objects.filter(title__icontains=query)[:6]
			return HttpResponse("issues") 
	return HttpResponse("You need ajax")
search_issues = login_required(search_issues)

	
#have different comment form if not logged in. require them to answer question
#just load top ~15 of each type into view unless they want to view new or random cache selections and ask them to sort these random groupings

#create view that creates random list of comments and caches so that people can get continuous sply of new stuff, eventually feeding in more questionable ones to get rid of them quickly. 

def upvote_all(request, slug):
	open_letter = Open_Letter.objects.get(slug=slug)
	try:
		politicians = Following.objects.get(user=request.user)
		user_voted = politicians.upvotes.filter(slug=slug)
		if not user_voted:
			if open_letter.target == 'Congress':
				for politician in politicians.my_politicians.filter(jurisdiction='federal'):
					try: #federal 1
						request = Request.objects.get(politician=politician, open_letter=open_letter)
						request.upvotes +=1
						request.save()
					except Request.DoesNotExist:
						request = Request(politician=politician, upvotes=1, open_letter=open_letter)
						request.save()
			if open_letter.target == 'State':
				for politician in politicians.my_politicians.filter(jurisdiction='state'):
					try: 
						request = Request.objects.get(politician=politician, open_letter=open_letter)
						request.upvotes +=1
						request.save()
					except Request.DoesNotExist:
						request = Request(politician=politician, upvotes=1, open_letter=open_letter)
						request.save()
			politicians.upvotes.add(open_letter)
			return HttpResponse("Yes")
		return HttpResponse("No")
	except Following.DoesNotExist:
		return HttpResponse("No Location") 
upvote_all = login_required(upvote_all)



def upvote_one(request, slug): #need to fix this one and know beforehand whether indiv is state or congress
	open_letter = Open_Letter.objects.get(slug=slug)
	target = Politician.objects.get(unique=post.politician_id) #CHECK TO CREATE POLITICIAN ON SUBMIT PAGE
	try:
		politicians = Following.objects.get(user=request.user)
		user_voted = politicians.upvotes.filter(slug=slug)
		if not user_voted:
			for politician in politicians.my_politicians:
				if target==politician:
					try:
						mention = Request.objects.get(politician=politician, open_letter=open_letter)
						mention.upvotes +=1
						mention.save()
					except Request.DoesNotExist:
						mention = Request(politician=politicians, open_letter=open_letter)
						mention.save()
					politicians.upvotes.add(post)
					return HttpResponse("Yes")
			return HttpResponse("None")
		return HttpResponse("No")
	except Following.DoesNotExist:
		return HttpResponse("No Location") 
upvote_one = login_required(upvote_one)



def byissue(request, issue, letter_type):
	issue = Issue.objects.get(slug=issue)
	if letter_type == 'Congress':
		pages_list = Open_Letter.objects.filter(issue=issue).order_by('-rank')
	else:
		if letter_type == 'State':
			pages_list = Open_Letter.objects.filter(issue=issue, state='OR').order_by('-rank')
		else:
			pages_list = Open_Letter.objects.filter(issue=issue, politician_id=letter_type).order_by('-rank')
	paginator = Paginator(pages_list, 6)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)
	return render_to_response("politics/byissue.html", {"issue":issue, "pages":pages}, 
	context_instance=RequestContext(request))
byissue = login_required(byissue)

#def base(request):
#	issues = Issue.objects.all().order_by('-rank')[1:6]
#	return {
#		'issues': issues
#	}

def issue_save(request):
	if request.method == "POST":	
		issue = request.POST["issue"]
		try:
			exist = Issue.objects.get(title=issue)
			return HttpResponse("Issue by that name already exists!")
		except Issue.DoesNotExist:
			nissue = Issue(title=issue, creator=request.user)
			nissue.save()
			return HttpResponseRedirect("/issues/")

issue_save = login_required(issue_save)

def replyup(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			reply = Reply.objects.get(id=id)
			user_voted = reply.reply_voters.filter(username=request.user.username)
			if not user_voted:
				reply.rank += 1
				reply.up += 1
				reply.reply_voters.add(request.user)
				reply.save()
				return HttpResponse("success")
			return HttpResponse("fail")
		return HttpResponse("Could not retrieve reply")
replyup = login_required(replyup)

def replydown(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			reply =  Reply.objects.get(id=id)
			user_voted = reply.reply_voters.filter(username=request.user.username)
			if not user_voted:
				reply.rank -= 1
				reply.down += 1
				reply.reply_voters.add(request.user)
				reply.save()
				return HttpResponse("success")
			return HttpResponse("fail")
		return HttpResponse("Could not retrieve reply")
replydown = login_required(replydown)

def up(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			comment =  Comment.objects.get(id=id)
			user_voted = comment.voters.filter(username=request.user.username)
			if not user_voted:
				comment.rank += 1
				comment.up += 1
				comment.voters.add(request.user)
				comment.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve comment")
up = login_required(up)


def comp_upvote(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			compromise =  Compromise.objects.get(id=id)
			user_voted = compromise.voters.filter(username=request.user.username)
			if not user_voted:
				compromise.rank += 1
				compromise.up += 1
				compromise.voters.add(request.user)
				compromise.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve compromise")
comp_upvote = login_required(comp_upvote)

def comp_downvote(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			compromise =  Compromise.objects.get(id=id)
			user_voted = compromise.voters.filter(username=request.user.username)
			if not user_voted:
				compromise.rank -= 1
				compromise.down += 1
				compromise.voters.add(request.user)
				compromise.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve compromise")
comp_downvote = login_required(comp_downvote)

def page_up(request):
	if request.is_ajax(): 
		if 'slug' in request.GET:
			slug = request.GET['slug']
			page =  Open_Letter.objects.get(slug=slug)
			user_voted = page.letter_voters.filter(username=request.user.username)
			if not user_voted:
				page.rank += 1
				page.letter_voters.add(request.user)
				page.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve page")
page_up = login_required(page_up)
		
def down(request):
	if request.is_ajax():
		if 'id' in request.GET:
			id = request.GET['id']
			comment =  Comment.objects.get(id=id)
			user_voted = comment.voters.filter(username=request.user.username)
			if not user_voted:
				comment.rank -= 1
				comment.down +=1
				comment.voters.add(request.user)
				comment.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve comment")
down = login_required(down)

		
def page_down(request):
	if request.is_ajax(): 
		if 'slug' in request.GET:
			slug = request.GET['slug']
			page =  Open_Letter.objects.get(slug=slug)
			user_voted = page.letter_voters.filter(username=request.user.username)
			if not user_voted:
				page.rank += 1
				page.letter_voters.add(request.user)
				page.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve page")
page_down = login_required(page_down)
#def (request):
#	return render_to_response("bootstrap/twitter.html", {}, context_instance=RequestContext(request))
#can you add-on to new user-linked group instead of dis weird shit
#ask questions on forms for new users until they have proven themselves -see other priveleges below
#they should get asked a question automatically remove their votes once they fail one of the question tests - force question test after 5 votes/comments. "sorry to interrupt, could you please prove you're human? -> answer question, ask/answer new question" - AT LOGIN. two tests: first test if they can answer properly - give them three tries on dif questions before asking them not to vote for 
#all political money should be donated (profits that is - show receipts and bills) -> event at the end to decide what it should go for whether its projects or whatever - social innovation funder
#make arguments by dragging to either side for bad/good -> an argument must be properly formatted - ie it must have 
#unlike reddit the site is based on the introduction of new people
#make higher-standing member that is the only one who can access the deleted area
#were going to serve as an example for congress ----- 
#fixed sorting windows border = to type of comment window currently viewing
#two windows, flip through windows at top to add to the viewer. treat the two viewing windows to be like a video player and allow them to view any set of comments/replies wherever they want. so just make them iframes and load the requested material. allow them to search their 'inventory' or the site at large to tag to this page. so you have critical, informative/neutral, favorable, and outside tags, also each window can become a search window (aka iframe) 
#can vote on whatever/classify whatever if they 
#have checkbox asking if they want to turn merge mode on. when that happens comment boxes should mouseover highlighted to show they are movable
#click on click off
#when click on show it and when click off don't show it... allow to show multiple that way


#def randomm():
#	count = Question.objects.count()
#	rand = random.randint(0, count-1)
#	try:
#		q = Question.objects.get(id=rand)
#		return q
#	except Open_Letter.DoesNotExist:
#			return randomm()
      				
#def check(request):
#	final = "fail"
#	if request.is_ajax(): 
#		if 'value' in request.GET:
#			value = request.GET['value']
#			if 'q' in request.GET:
#				q = request.GET['q']
#				try:
#					question = Question.objects.get(id=q)
#					if question.answer == value:
#						return HttpResponse()
#					else:
#						try:
#							object = randomm()
#						except Question.DoesNotExist:
#							object = Question.objects.get(id=6)
#							
#						to_return ="Try again later"
#						return HttpResponse(to_return)
#				except Question.DoesNotExist:
#					value = Question.objects.get(id=2)
#					return HttpResponse(fail)
#				return HttpResponse(fail)
#			return HttpResponse(fail)
#		return HttpResponse(fail)
#	return HttpResponse(fail)


#def test(request):
#	page = randomm()
#	#restrict = Restrict_Vote.objects.get(page=page)
#	return render_to_response("politics/test.html", {"page":page}, context_instance=RequestContext(request))	

def about(request):
	return render_to_response("politics/about.html", context_instance=RequestContext(request))
about = login_required(about)

def view_pages(request):
	page_list = Open_Letter.objects.all().order_by('-rank')
	paginator = Paginator(page_list, 25)
	page = request.GET.get('page')
	try:
		articles = paginator.page(page)
	except PageNotAnInteger:
		articles = paginator.page(1)
	except EmptyPage: #out of range deliver last page
		articles = paginator.page(paginator.num_pages)
	return render_to_response("politics/articles.html", {"articles":articles}, context_instance=RequestContext(request))
view_pages = login_required(view_pages)



def favorite(request, slug):
	if request.is_ajax():
		post = Open_Letter.objects.get(slug=slug)
		try:
			fav = Favorite.objects.get(user=request.user)
			if fav.page.filter(slug=slug):
				return HttpResponse("No")
			else:
				fav.page.add(post)
				fav.save()
				return HttpResponse("Yes")
		except Favorite.DoesNotExist:
			fav = Favorite(user=request.user)
			fav.save()
			fav.page.add(post)
			fav.save()
			return HttpResponse("Yes")
		return HttpResponse("problem1")
	return HttpResponse("problem2")
favorite = login_required(favorite)


def politipage(request):
		user = request.user
		location = Location.objects.get(user=user)
		posts = Open_Letter.objects.filter(creator=user)[:6]
		favorites = Following.objects.filter(user=user)
		requesting = request.user
		try:
			location = Location.objects.get(user=user)
			latitude = location.latitude
			longitude = location.longitude
			home = location.state
			something = True
			politicians = congress.legislators_for_lat_lon(latitude,longitude)
			state = openstates.legislator_geo_search(latitude, longitude)
			if requesting == user:
				comments = Comment.objects.filter(creator=user)[:6]
				return render_to_response("politics/politipage.html", {"user":user, "location":location, "politicians":politicians, "something":something, "home":home, "posts":posts, "state":state, "favorites":favorites, "comments":comments},context_instance=RequestContext(request))
			else:
				return render_to_response("politics/politipage.html", {"user":user, "politicians":politicians, "something":something, "home":home, "posts":posts, "state":state, "favorites":favorites},context_instance=RequestContext(request))
		except Location.DoesNotExist:
			states = STATE_CHOICES
			if requesting==user:
				comments = Comment.objects.filter(creator=user)[:6]
				return render_to_response("politics/politipage.html", {"user":user, "states":states, "posts":posts, "favorites":favorites, "comments":comments},context_instance=RequestContext(request))
			else:
				return render_to_response("politics/politipage.html", {"user":user, "posts":posts, "favorites":favorites}, context_instance=RequestContext(request))
				
#Create new Ask me About main page
def create(request):
	issues = Issue.objects.all()
	all = Issue.objects.all()
	now = datetime.datetime.now()
	end = now + datetime.timedelta(days=7)
	return render_to_response("politics/create.html",{"issues":issues, "now":now, "end":end, "all":all}, context_instance=RequestContext(request))
create = login_required(create)

def location_save(request):
	if request.method == "POST":
		user = request.user
		first = request.POST["first"]
		last = request.POST["last"]
		address = request.POST["address"]
		city = request.POST["city"]
		state = request.POST["state"]
		zip_code = request.POST["zip"]
		query = '%s, %s, %s %s' % (address, city, state, zip_code)
		g = Geocoder()
		if g.geocode(query).valid_address:
			location = Location(user = user, first=first, last=last, address=address, city=city, state=state, zipcode=zip_code)
			location.save()
			latitude = location.latitude
			longitude = location.longitude
			politicians = congress.legislators_for_lat_lon(latitude,longitude)
			#empty list of federal/state politicians
			fed_list=[]
			state_list=[]
			#create user object to eventually store their politicians
			following = Following(user=user)
			following.save()
			#get/create federal politicians
			if len(politicians)==3: #if no extra politicians to choose from
				fed_list=[]
				for politician in politicians:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['congress_office']
						except KeyError:
							address = ''
						try:
							phone = politician['phone']
						except KeyError:
							phone = ''
						try:
							website = politician['website']
						except KeyError:
							website = ''
						try:
							twitter = politician['twitter']
						except KeyError:
							twitter = ''
						try:
							facebook = politician['facebook']
						except KeyError:
							facebook = ''
						new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
						last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
						address=address, address2='Washington, DC 20515', phone=phone, state=state,
						website=website, twitter=twitter, facebook=facebook, photo=politician['bioguide_id']  
						)
						new.save()
						following.my_politicians.add(new)
						fed_list.append(new)

			#get/create state politicians
			state = openstates.legislator_geo_search(latitude, longitude)
			if len(state)==2:
				
				for politician in state:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['offices'][0]['address']
							splits = address.split(",")
							end = len(splits)-2
							address2 = splits[end]+','+splits[end+1]
							address1_length = len(address) - len(address2)
							address1 = address[:address1_length]
						except KeyError:
							address1 = ''
							address2 = ''
						try:
							phone = politician['+phone']
						except KeyError:
							phone = ''
						try:
							website = politician['url']
						except KeyError:
							website = ''
						try:
							photo = politician['photo_url']
						except KeyError:
							photo = ''
						title = politician['chamber']
						if title == 'lower':
							title = 'Rep'
						else:
							title = 'Sen'

						new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
						last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
						address=address1, address2=address2, phone=phone, state=state,
						website=website, photo=photo  
						)
						new.save()
						following.my_politicians.add(new)
			return HttpResponseRedirect("/"+user.username+"/profile/")
	return HttpResponseRedirect("/"+request.user.username+"/profile/")
location_save = login_required(location_save)



def hlocation_save(request): #need to test when no lat
	if request.method == "POST":
		user = request.user
		first = user.first_name
		last = user.last_name
		latitude = request.POST["latitude"]
		longitude = request.POST["longitude"]
		address = request.POST["address"]
		city = request.POST["city"]
		state = request.POST["state"]
		query = '%s, %s, %s' % (address, city, state)
		try:
			following = Following.objects.get(user=user)
			following.my_politicians.clear()
		except Following.DoesNotExist:
			following = Following(user=user)
			following.save()
		try:
			public_id = Public_Id.objects.get(user=user)
			public_id.city = city
			public_id.state = state
			public_id.save()
		except Public_Id.DoesNotExist:
			public_id = Public_Id(user=user, first=first, last=last, city=city, state=state)
			public_id.save()
		if latitude:
			try: 
				location = Location.objects.get(user=user)
			except Location.DoesNotExist:
				 location = Location(user = user, first=first, last=last, address='', latitude=latitude, longitude=longitude, city=city, state=state)
				 location.save()
			politicians = congress.legislators_for_lat_lon(latitude,longitude)
			#empty list of federal/state politicians
			fed_list=[]
			state_list=[]

			#get/create federal politicians
			if len(politicians)==3: #if no extra politicians to choose from
				fed_list=[]
				for politician in politicians:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['congress_office']
						except KeyError:
							address = ''
						try:
							phone = politician['phone']
						except KeyError:
							phone = ''
						try:
							website = politician['website']
						except KeyError:
							website = ''
						try:
							twitter = 'http://www.twitter.com/'+politician['twitter_id']
						except KeyError:
							twitter = ''
						try:
							facebook = 'http://www.facebook.com/'+politician['facebook_id']
						except KeyError:
							facebook = ''
						new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
							last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
							address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter,
							facebook=facebook, photo=politician['bioguide_id']  
							)
						new.save()
						following.my_politicians.add(new)
				#get/create state politicians
			state_legislators = openstates.legislator_geo_search(latitude, longitude)
			if len(state_legislators)==2:		
				for politician in state_legislators:
					try:
						following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
					except Politician.DoesNotExist:
						try:
							address = politician['offices'][0]['address']
							splits = address.split(",")
							end = len(splits)-2
							address2 = splits[end]+','+splits[end+1]
							address1_length = len(address) - len(address2)
							address1 = address[:address1_length]
						except KeyError:
							address1 = ''
							address2 = ''
						try:
							phone = politician['offices'][0]['phone']
						except KeyError:
							phone = ''
						try:
							website = politician['url']
						except KeyError:
							website = ''
						try:
							photo = politician['photo_url']
						except KeyError:
							photo = ''
						title = politician['chamber']
						if title == 'lower':
							title = 'Rep'
						else:
							title = 'Sen'
						new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
							last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
							address=address1, address2=address2, party=politician['party'], phone=phone, state=state, website=website, photo=photo  
							)
						new.save()
						following.my_politicians.add(new)		
		else:
			try:
				g = Geocoder()
				if g.geocode(query).valid_address:
					try: 
						location = Location.objects.get(user=user)
					except Location.DoesNotExist:
						location = Location(user = user, first=first, last=last, address=address, city=city, state=state)
						location.save()
					latitude = location.latitude
					longitude = location.longitude
					politicians = congress.legislators_for_lat_lon(latitude,longitude)
					#empty list of federal/state politicians
					fed_list=[]
					state_list=[]
					#get/create federal politicians
					
					if len(politicians)==3: #if no extra politicians to choose from
						fed_list=[]
						for politician in politicians:
							try:
								following.my_politicians.add(Politician.objects.get(unique=politician['bioguide_id']))
							except Politician.DoesNotExist:
								try:
									address = politician['congress_office']
								except KeyError:
									address = ''
								try:
									phone = politician['phone']
								except KeyError:
									phone = ''
								try:
									website = politician['website']
								except KeyError:
									website = ''
								try:
									twitter = 'http://www.twitter.com/'+politician['twitter_id']
								except KeyError:
									twitter = ''
								try:
									facebook = 'http://www.facebook.com/'+politician['facebook_id']
								except KeyError:
									facebook = ''
								new = Politician(unique=politician['bioguide_id'], title=politician['title'], first=politician['firstname'],
									last=politician['lastname'], jurisdiction='federal', district=politician['district'], in_office=politician['in_office'], 
									address=address, address2='Washington, DC 20515', party=politician['party'], phone=phone, state=state, website=website, twitter=twitter,
									facebook=facebook, photo=politician['bioguide_id']  
									)
								new.save()
								following.my_politicians.add(new)
					
					#get/create state politicians
					state_legislators = openstates.legislator_geo_search(latitude, longitude)
					if len(state_legislators)==2:		
						for politician in state_legislators:
							try:
								following.my_politicians.add(Politician.objects.get(unique=politician['leg_id']))
							except Politician.DoesNotExist:
								try:
									address = politician['offices'][0]['address']
									splits = address.split(",")
									end = len(splits)-2
									address2 = splits[end]+','+splits[end+1]
									address1_length = len(address) - len(address2)
									address1 = address[:address1_length]
								except KeyError:
									address1 = ''
									address2 = ''
								try:
									phone = politician['offices'][0]['phone']
								except KeyError:
									phone = ''
								try:
									website = politician['url']
								except KeyError:
									website = ''
								try:
									photo = politician['photo_url']
								except KeyError:
									photo = ''
								title = politician['chamber']
								if title == 'lower':
									title = 'Rep'
								else:
									title = 'Sen'
								new = Politician(unique=politician['leg_id'], title=title, first=politician['first_name'],
									last=politician['last_name'], jurisdiction='state', district=politician['district'], in_office=politician['active'], 
									address=address1, address2=address2, party=politician['party'], phone=phone, state=state, website=website, photo=photo  
									)
								new.save()
								following.my_politicians.add(new)
				else:
					return HttpResponse("Invalid Address. Go back to the last screen and try again.")
			except geopy.geocoders.google.GQueryError:
				return HttpResponseRedirect("/")
		if 'slug' in request.POST:
			slug = request.POST["slug"]
			return HttpResponseRedirect("/openletters/"+slug+"/")
		else:
			return HttpResponseRedirect("/")
		
	return HttpResponseRedirect("/")#not request.post
hlocation_save = login_required(hlocation_save)



def my_politicians(request, state, city, latitude, longitude):
	#also take in city and if in portland grab the city council
	politicians = congress.legislators_for_lat_lon(latitude,longitude)	
	state_legislators = openstates.legislator_geo_search(latitude, longitude)
	return render_to_response("politics/my_politicians.html",{"politicians":politicians, "state":state, "city":city, "state_legislators":state_legislators}, context_instance=RequestContext(request))


	
my_politicians = login_required(my_politicians)



def save_page(request):
	if request.method == "POST":
		issue = ""
		if 'issue' in request.POST:
			issue = request.POST["issue"]
			if issue != "other":
				issue = Issue.objects.get(title=issue)
			else:
				if 'issue-search' in request.POST:
					raw = request.POST["issue-search"]
					index = raw.find('|')
					if index > 0:
						issue = raw[index+2:]
						issue = Issue.objects.get(title=issue)
					else:
						issue = Issue(title=raw, creator=request.user)
						issue.save()		
			question = request.POST["question"]
			extra = request.POST["extra"]
			youtube = request.POST["youtube"]
			
			target = ''
			if 'congress' in request.POST:
				target = request.POST["congress"]
			state = ''
			if 'state' in request.POST:
				state = request.POST["state"]
			
			politician = ''
			if 'politician' in request.POST:
				politician = request.POST["politician"]
			politician_id = ''
			if 'politician_id' in request.POST:
				politician_id = request.POST["politician_id"]	
			creator = request.user
			page = Open_Letter(issue = issue, creator = creator, title = question, content = extra, youtube_url = youtube, target=target, state=state, politician=politician, politician_id=politician_id)
			page.save()
			issue.rank+=1
			issue.save()
		return HttpResponseRedirect("/openletters/"+page.slug+"/")
save_page = login_required(save_page)					

def cite(request, slug):
	if request.method == "POST":
		comment = request.POST["id"]
		comment = Comment.objects.get(id=comment)
		source = request.POST["source"]
		comment.source = source
		comment.save()
		return HttpResponseRedirect("/openletters/" + slug + "/")
cite = login_required(cite)

def compcite(request, slug):
	if request.method == "POST":
		comment = request.POST["id"]
		comment = Compromise.objects.get(id=comment)
		source = request.POST["source"]
		comment.source = source
		comment.save()
		return HttpResponseRedirect("/openletters/" + slug + "/")
compcite = login_required(compcite)
#Add old values of source don't just replace


def search(request):
	if 'query' in request.GET:
		query = request.GET['query']
		if query != '':
			pages = Open_Letter.objects.filter(title__icontains=query)
			issues = Issue.objects.filter(title__icontains=query)
			more=[]
			most=[]
			politicians = shlex.split(query)
			first = politicians[0]
			if 2 <= len(politicians):
				last = politicians[1]
				politicians = congress.legislators(lastname=last, firstname=first)
				more = congress.legislators(lastname=last, nickname=first)				
			else:
				politicians = congress.legislators(firstname=query)
				more = congress.legislators(lastname=query)
				most = congress.legislators(nickname=query)
			return render_to_response("politics/searching.html",{"pages":pages, "issues":issues, "politicians":politicians,"more":more,"most":most}, context_instance=RequestContext(request))
	return HttpResponseRedirect("/")
search = login_required(search)

def letter_search(request, query):
	open_letters = Open_Letter.objects.filter(title__icontains=query)
	return render_to_response("politics/search_letters.html",{"open_letters":open_letters, "query":query}, context_instance=RequestContext(request))
letter_search = login_required(letter_search)

def poli_search(request, query):
	show_results = True
	politicians = []
	more = []
	most = []
	query = query.strip()
	politicians = shlex.split(query)
	first = politicians[0]
	if 2 <= len(politicians):
		last = politicians[1]
		politicians = congress.legislators(lastname=last, firstname=first)
		more = congress.legislators(lastname=last, nickname=first)				
	else:
		politicians = congress.legislators(firstname=query)
		more = congress.legislators(lastname=query)
		most = congress.legislators(nickname=query)
	return render_to_response("politics/search.html",{"politicians":politicians,"more":more,"most":most}, context_instance=RequestContext(request))
poli_search = login_required(poli_search)

#def view_pro(request, slug):
#	pro_list = Comment.objects.filter(article=Open_Letter.objects.get(slug=slug), response__id=1).order_by('-rank')
#	paginator = Paginator(pro_list, 1)
#	page = request.GET.get('page')
#	try:
#		pro_comments = paginator.page(page)
#	except PageNotAnInteger:
#		pro_comments = paginator.page(1)
#	except EmptyPage: #out of range deliver last page
#		pro_comments = paginator.page(paginator.num_pages)
#	return render_to_response("politics/comments.html", {"pro_comments":pro_comments, "slug":slug}, context_instance=RequestContext(request))
#view_pro = login_required(view_pro)

#def view_neg(request, slug):
#	neg_list = Comment.objects.filter(article=Open_Letter.objects.get(slug=slug), response__id=2).order_by('-rank')
#	paginator = Paginator(neg_list, 1)
#	page = request.GET.get('page')
#	try:
#		neg_comments = paginator.page(page)
#	except PageNotAnInteger:
#		neg_comments = paginator.page(1)
#	except EmptyPage: #out of range deliver last page
#		neg_comments = paginator.page(paginator.num_pages)
#	return render_to_response("politics/comments.html", {"neg_comments":neg_comments, "slug":slug}, context_instance=RequestContext(request))
#view_neg = login_required(view_neg)

#def view_comp(request, slug):
#	comp_list = Compromise.objects.filter(article=Open_Letter.objects.get(slug=slug)).order_by('-rank')
#	paginator = Paginator(comp_list, 1)
#	page = request.GET.get('page')
#	try:
#		compromises = paginator.page(page)
#	except PageNotAnInteger:
#		compromises = paginator.page(1)
#	except EmptyPage: #out of range deliver last page
#		compromises = paginator.page(paginator.num_pages)
#	return render_to_response("politics/comments.html", {"compromises":compromises, "slug":slug}, context_instance=RequestContext(request))
#view_comp = login_required(view_comp)


def view_ask(request, slug):
	try:
		open_letter = Open_Letter.objects.get(slug=slug)
		requests = Request.objects.filter(open_letter=open_letter, upvotes__gte=1).order_by('-upvotes')
		comments = Comment.objects.filter(open_letter=open_letter)
		return render_to_response("politics/discuss.html",{"open_letter":open_letter, "requests":requests, "comments":comments}, context_instance=RequestContext(request))
	except Open_Letter.DoesNotExist:
		raise Http404('Page Not Found')
view_ask = login_required(view_ask)

		
def upvote(request, slug):
	slug = slug
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			comment = Comment.objects.get(id=id)
			user_voted = comment.voters.filter(username=request.user.username)
			if not user_voted:
				comment.rank += 1
				comment.voters.add(request.user)
				comment.save()
				return HttpResponseRedirect("/openletters/" + slug + "/")
			return HttpResponseRedirect("/openletters/" + slug + "/")
		except Comment.DoesNotExist:
			raise Http404('Comment not Found.')
	return HttpResponseRedirect("/openletters/" + slug + "/")
upvote = login_required(upvote)

def downvote(request, slug):
	slug = slug
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			comment = Comment.objects.get(id=id)
			user_voted = comment.voters.filter(username=request.user.username)
			if not user_voted:
				comment.rank -= 1
				comment.voters.add(request.user)
				comment.save()
				return HttpResponseRedirect("/openletters/" + slug + "/")
			return HttpResponseRedirect("/openletters/" + slug + "/")
		except Comment.DoesNotExist:
			raise Http404('Comment not Found.')
	return HttpResponseRedirect("/openletters/" + slug + "/")
downvote = login_required(downvote)

def replyvote(request, slug):
	slug = slug
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			reply = Reply.objects.get(id=id)
			user_voted = reply.reply_voters.filter(username=request.user.username)
			if not user_voted:
				reply.rank += 1
				reply.up +=1
				reply.reply_voters.add(request.user)
				reply.save()
		except Reply.DoesNotExist:
			raise Http404('Reply not Found')
		return HttpResponseRedirect("/openletters/" + slug + "/")
replyvote = login_required(replyvote)

def replydownvote(request, slug):
	slug = slug
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			reply = Reply.objects.get(id=id)
			user_voted = reply.reply_voters.filter(username=request.user.username)
			if not user_voted:
				reply.rank -= 1
				reply.down +=1
				reply.reply_voters.add(request.user)
				reply.save()
		except Reply.DoesNotExist:
			raise Http404('Reply not Found')
		return HttpResponseRedirect("/openletters/" + slug + "/")
replydownvote = login_required(replydownvote)




def unreport_comment(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				comment = Comment.objects.get(id=id)
				user_voted = comment.flag_vote.filter(username=request.user.username)
				if not user_voted:
					comment.flag -= 1
					comment.flag_vote.add(request.user)
					comment.save()
					message = "You have successfully unreported %s's comment" % (comment.creator)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's comment!" % (comment.creator)
					return HttpResponse(message)
			except Comment.DoesNotExist:
				raise Http404('Comment not Found.')
			return HttpResponse("Something went wrong")
	return HttpResponse("Something went wrong")
unreport_comment = login_required(unreport_comment)

def comp_report(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				compromise = Compromise.objects.get(id=id)
				user_voted = compromise.flag_vote.filter(username=request.user.username)
				if not user_voted:
					compromise.flag -= 1
					compromise.flag_vote.add(request.user)
					compromise.save()
					message = "Yes" % (compromise.creator)
					return HttpResponse(message)
				else:
					message = "No" % (compromise.creator)
					return HttpResponse(message)
			except Compromise.DoesNotExist:
				raise Http404('Compromise not Found.')
			return HttpResponse("Something went wrong")
	return HttpResponse("Something went wrong")
comp_report = login_required(comp_report)



def unreport_reply(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				reply = Reply.objects.get(id=id)
				user_voted = reply.reply_flagger.filter(username=request.user.username)
				if not user_voted:
					reply.flag -= 1
					reply.reply_flagger.add(request.user)
					reply.save()
					message = "You have successfully unreported %s's reply" % (reply.creator)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's reply!" % (reply.creator)
					return HttpResponse(message)
			except Reply.DoesNotExist:
				raise Http404('Reply not Found.')
			return HttpResponseRedirect("/openletters/" + slug + "/")
		return HttpResponse("Something went wrong")
	return HttpResponse("Something went wrong")

unreport_reply = login_required(unreport_reply)




def replyreport(request, slug):
	slug = slug
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				reply = Reply.objects.get(id=id)
				user_voted = reply.reply_flagger.filter(username=request.user.username)
				if not user_voted:
					reply.flag += 1
					reply.reply_flagger.add(request.user)
					reply.save()
					return HttpResponse("success")
				else:
					return HttpResponse("fail")
			except Reply.DoesNotExist:
				raise Http404('Reply not Found.')
			return HttpResponseRedirect("/openletters/" + slug + "/")
	return HttpResponseRedirect("/openletters/" + slug + "/")
replyreport = login_required(replyreport)

def source(request, slug):
	slug = slug
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			comment = Comment.objects.get(id=id)
			user_voted = comment.source_vote.filter(username=request.user.username)
			if not user_voted:
				comment.called_out+=1
				comment.source_vote.add(request.user)
				comment.save()
		except Comment.DoesNotExist:
			raise Http404('Comment not Found.')
			return HttpResponseRedirect("/openletters/" + slug + "/")
	return HttpResponseRedirect("/openletters/" + slug + "/")
source = login_required(source)

def reply(request, slug):
	slug = slug
	if request.method == "POST":
		comment_id = request.POST["id"]
		comment = request.POST["comment"]
		get_comment = Comment.objects.get(id = comment_id)
		creator = request.user
		get_comment.replies.create(creator = creator, comment = comment)
		message = "<a href='/%s/profile/'>%s</a>| <b>1 In Favor, 0 Against</b><br/> <br/> %s <br/><br/><b>You can't vote on your own reply<br/>" % (creator, creator, comment)
		return HttpResponse(message)
reply = login_required(reply)	

def comreply(request, slug):
	slug = slug
	if request.method == "POST":
		comment_id = request.POST["id"]
		comment = request.POST["comment"]
		get_comment = Compromise.objects.get(id = comment_id)
		creator = request.user
		get_comment.replies.create(creator = creator, comment = comment)
		message = "<a href='/%s/profile/'>%s</a>| <b>1 In Favor, 0 Against</b><br/> <br/> %s <br/><br/><b>You can't vote on your own reply<br/>" % (creator, creator, comment)
		return HttpResponse(message)
comreply = login_required(comreply)					

def comment(request, slug):
	slug = slug
	if request.method == "POST":
		try:
			comment = request.POST["comment"]
			open_letter = Open_Letter.objects.get(slug=slug)
			creator = request.user
			reply = Comment(comment = comment, open_letter=open_letter, creator=creator)
			reply.save()
			open_letter.rank+=1
			open_letter.save()
			reply.voters.add(creator)
			return HttpResponseRedirect("/openletters/" + slug + "/")
		except Open_Letter.DoesNotExist:
			raise Http404('Page not Found')
comment = login_required(comment)	

def legislators(request):
	if 'state' in request.GET:
		state = request.GET['state']
		lower = openstates.legislators(chamber='lower', state=state)
		upper = openstates.legislators(chamber='upper', state=state)
		congressmen = congress.legislators(state=state)
	return render_to_response("politics/legislators.html",{"state":state, "upper":upper, "lower":lower, "congressmen":congressmen}, context_instance=RequestContext(request))
legislators = login_required(legislators)

def congress_committee(request):
	house = congress.committees(chamber='House')
	senate = congress.committees(chamber='Senate')
	return render_to_response("politics/congress-committee.html",{"house":house, "senate":senate}, context_instance=RequestContext(request))
congress_committee = login_required(congress_committee)


def localize(request):
	return render_to_response("politics/signup_2.html",{}, context_instance=RequestContext(request))
localize = login_required(localize)