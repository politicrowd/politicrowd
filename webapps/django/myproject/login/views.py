# coding: utf-8
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core import serializers
from django import forms
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
import shlex, random
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from sunlight import congress, openstates
from login.models import Location
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from politics.models import Ask, Issue, Ask_Comment, Ask_Reply, Response_Type, Mentions, Restrict_Vote, Question, Compromise, Favorite, State_Mention, MyPolitician

from politician.models import Politician, AMA, Comments, Replies

def committee(request, committee):
	upages = Ask.objects.filter(ucommittee_id=committee).order_by('-rank')
	lpages = Ask.objects.filter(lcommittee_id=committee).order_by('-rank')
	committee = openstates.committee_detail(committee_id=committee)
	return render_to_response("politician/committee.html", {"committee":committee, "upages":upages, "lpages":lpages}, context_instance=RequestContext(request))
committee = login_required(committee)
	
	

def politician(request, first, last):
	congressman = congress.legislators(lastname=last, firstname=first)[0]
	bioguide = congressman['bioguide_id']
	committees = congress.committees_for_legislator(bioguide_id=bioguide)
	nickname = congressman['nickname']
	now = datetime.now()
	party = congressman['party']
	district = congressman['district']
	inoffice = congressman['in_office']
	state = congressman['state']
	email = congressman['email']
	website = congressman['website']
	facebook = congressman['facebook_id']
	office = congressman['congress_office']
	phone = congressman['phone']
	twitter = congressman['twitter_id']
	title = congressman['title']
	mentions = Mentions.objects.filter(politician=bioguide)
	politician=Politician.objects.filter(unique=bioguide)
	live = AMA.objects.filter(politician=politician,
			creation_date__lte=now, end_date__gte=now
			).order_by('-creation_date')
	infinite = AMA.objects.filter(politician=politician,
			creation_date__lte=now, end_date=None
			).order_by('-creation_date')
	coming = AMA.objects.filter(
			politician=politician, creation_date__gte=now
			).order_by('-creation_date')
	ended = AMA.objects.filter(politician=politician, end_date__lte=now).order_by('-end_date')

	return render_to_response("politician/politician.html", {"title":title, "committees":committees, "nickname":nickname,"live":live, "infinite":infinite, "coming":coming, "ended":ended, "first":first, "last":last, "bioguide":bioguide, "district":district, "party":party, "inoffice":inoffice, "state":state, "email":email, "website":website, "facebook":facebook, "office":office, "phone":phone, "twitter":twitter, "mentions":mentions, "politician":politician}, context_instance=RequestContext(request))
politician = login_required(politician)

#do legislator_detail rather than legislators and lookup with id instead of first/last because you need the detail to show roles for committees and such
def staterep(request, first, last, state):
	congressman = openstates.legislators(state=state, last_name=last, first_name=first)[0]
	photo = ""
	now = datetime.now()
	party = congressman['party']
	unique = congressman['leg_id']
	politician=Politician.objects.filter(unique=unique)
	chamber = congressman['chamber']
	district = congressman['district']
	state = congressman['state']
	detail = openstates.legislator_detail(leg_id=unique)
	roles = detail['roles'][1:]
	committee_pages = []
	for committee in roles:
		committee_pages += Ask.objects.filter(lcommittee_id=committee['committee_id']).order_by('-rank')
	detail = roles
	live = AMA.objects.filter(politician=politician,
			creation_date__lte=now, end_date__gte=now
			).order_by('-creation_date')
	coming = AMA.objects.filter(
			politician=politician, creation_date__gte=now
			).order_by('-creation_date')
	ended = AMA.objects.filter(politician=politician, end_date__lte=now).order_by('-end_date')
	mentions = State_Mention.objects.filter(politician=unique).order_by('-mentions')
	try:
		photo = congressman['photo_url']
		return render_to_response("politician/staterep.html", {"committee_pages":committee_pages, "first":first, "last":last, "district":district, "party":party, "live":live, "detail":detail, "coming":coming, "ended":ended, "chamber":chamber, "photo":photo, "state":state, "mentions":mentions, "unique":unique}, context_instance=RequestContext(request))
	except KeyError:
		photo = ""
		return render_to_response("politician/staterep.html", {"first":first, "last":last, "district":district, "party":party, "politician":politician, "chamber":chamber, "photo":photo, "state":state, "live":live, "coming":coming, "detail":detail, "ended":ended, "mentions":mentions, "unique":unique}, context_instance=RequestContext(request))
	return HttpResponse("Politician Not Found")
staterep = login_required(staterep)


def legislator(request, leg_id):
	congressman = openstates.legislator_detail(leg_id=leg_id)
	photo = ""
	now = datetime.now()
	party = congressman['party']
	politician=Politician.objects.filter(unique=leg_id)
	chamber = congressman['chamber']
	district = congressman['district']
	state = congressman['state']
	detail = congressman['roles'][1:]
	first = congressman['first_name']
	last = congressman['last_name']
	state = congressman['state']
	committee_pages = []
	for committee in detail:
		committee_pages += Ask.objects.filter(lcommittee_id=committee['committee_id']).order_by('-rank')
	
	live = AMA.objects.filter(politician=politician,
			creation_date__lte=now, end_date__gte=now
			).order_by('-creation_date')
	coming = AMA.objects.filter(
			politician=politician, creation_date__gte=now
			).order_by('-creation_date')
	ended = AMA.objects.filter(politician=politician, end_date__lte=now).order_by('-end_date')
	mentions = State_Mention.objects.filter(politician=leg_id).order_by('-mentions')
	try:
		photo = congressman['photo_url']
		return render_to_response("politician/staterep.html", {"committee_pages":committee_pages, "first":first, "last":last, "district":district, "party":party, "live":live, "detail":detail, "coming":coming, "ended":ended, "chamber":chamber, "photo":photo, "state":state, "mentions":mentions, "leg_id":leg_id}, context_instance=RequestContext(request))
	except KeyError:
		photo = ""
		return render_to_response("politician/staterep.html", {"first":first, "last":last, "district":district, "party":party, "politician":politician, "chamber":chamber, "photo":photo, "state":state, "live":live, "coming":coming, "detail":detail, "ended":ended, "mentions":mentions, "unique":unique}, context_instance=RequestContext(request))
	return HttpResponse("Politician Not Found")
legislator = login_required(legislator)

def save_politician(request):
	if request.method == "POST":
		user = request.user
		location = Location.objects.get(user=user)
		state = location.state
		title = request.POST["title"]
		first = request.POST["first"]
		last = request.POST["last"]
		jurisdiction = request.POST["jurisdiction"]
		unique = ''
		legislator = ''
		if jurisdiction == 'Local':
			legislator = openstates.legislators(state=state, last_name=last, first_name=first)[0]
			unique = legislator['id']
			politician = Politician(politician=request.user, title=title, first=first, last=last, unique=unique, jurisdiction=0)
		else:
			legislator = congress.legislators(state=location.state, lastname=last, firstname=first)[0]
			unique = legislator['bioguide_id']
			politician = Politician(politician=request.user, title=title, first=first, last=last, unique=unique, jurisdiction=1)
		politician.save()
		return HttpResponseRedirect("/")
save_politician = login_required(save_politician)

def save_ama(request):
	if request.method == "POST":
		title = request.POST["topic"]
		extra = request.POST["extra"]
		restrict = request.POST["restrict"]
		unique = request.POST["unique"]
		try:
			hour=int(request.POST["hour"])
			end=int(request.POST["end-hour"])
  			valid_datetime = datetime.strptime(request.POST["date"], '%m/%d/%Y')
  			valid_datetime = valid_datetime.replace(hour=hour)
  			end_date = datetime.strptime(request.POST["date"], '%m/%d/%Y')
  			end_date = end_date.replace(hour=end)
  			politician = Politician.objects.get(unique=unique)
  			if 'type' in request.POST:
  				types = request.POST["type"]
  				if types == 'debate':
  					ama = AMA(title=title, politician=politician, creation_date=valid_datetime, end_date=end_date, extra=extra, restrict=restrict, townhall=False)
  					ama.save()
  				else:
					ama = AMA(title=title, politician=politician, creation_date=valid_datetime, end_date=end_date, extra=extra, restrict=restrict)
					ama.save()
			else:
				ama = AMA(title=title, politician=politician, creation_date=valid_datetime, end_date=end_date, extra=extra, restrict=restrict)
				ama.save()
			return HttpResponseRedirect("/congress/"+ama.slug+"/")
		except ValueError:
			return HttpResponse("Something went wrong. Please contact us.")
save_ama = login_required(save_ama)

def morecomments(request, slug):
	try:
		ama = AMA.objects.get(slug=slug)
		comments_list = Comments.objects.filter(article=AMA.objects.get(slug=slug)).order_by('-rank')
		paginator = Paginator(comments_list, 1)
		page = request.GET.get('page')
		try:
			commments = paginator.page(page)
			return render_to_response("politician/comments.html", {"comments":comments, "slug":slug}, context_instance=RequestContext(request))
		except PageNotAnInteger:
			comments = paginator.page(1)
		except EmptyPage:
			comments = paginator.page(paginator.num_pages)
		return render_to_response("politician/comments.html", {"comments":comments, "slug":slug}, context_instance=RequestContext(request))
	except AMA.DoesNotExist:
		return HttpResponse("Something went wrong")
morecomments = login_required(morecomments)

def title_change(request):
	if request.method == "POST":
		title = request.POST["title"]
		slug = request.POST["slug"]
		ama = AMA.objects.get(slug=slug)
		ama.title=title
		ama.save()
		slug = ama.slug
		return HttpResponseRedirect("/congress/"+slug+"/")
	return HttpRespones("Error")
title_change = login_required(title_change)


def extra_change(request):
	if request.method == "POST":
		extra = request.POST["extra"]
		slug = request.POST["slug"]
		ama = AMA.objects.get(slug=slug)
		ama.extra=extra
		ama.save()
		slug = ama.slug
		return HttpResponseRedirect("/congress/"+slug+"/")
	return HttpRespones("Error")
title_change = login_required(title_change)

	


def view_ama(request, slug): #if not in district just dont show comment box
	try:
		
		ama = AMA.objects.get(slug=slug)
		restrict = ama.restrict
		user = request.user
		politician = ama.politician
		jurisdiction = politician.jurisdiction
		unique = politician.unique
		title = ama.title
		extra = ama.extra
		now = timezone.now()
		comments = Comments.objects.filter(article=ama, deleted=False).order_by('-rank')
		if request.user == politician.politician:
			return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request)) 
		if restrict == 1:
			try:
				indistrict = MyPolitician.objects.get(user=user)
				if jurisdiction == 1:
					if unique == indistrict.fed1:
						if ama.creation_date <= now: 
							if ama.end_date == None:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							if ama.end_date >= now:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							else:
								return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician},
							context_instance=RequestContext(request))
						else:
							return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
					
					if unique == indistrict.fed2:
						if ama.creation_date <= now: 
							if ama.end_date == None:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							if ama.end_date >= now:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							else:
								return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician},
							context_instance=RequestContext(request))
						else:
							return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
					if unique == indistrict.fed3:
						if ama.creation_date <= now: 
							if ama.end_date == None:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							if ama.end_date >= now:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							else:
								return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
						else:
							return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
				else:
					if unique == indistrict.state1:
						if ama.creation_date <= now: 
							if ama.end_date == None:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							if ama.end_date >= now:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							else:
								return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician},
							context_instance=RequestContext(request))
						else:
							return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
					if unique == indistrict.state2:
						if ama.creation_date <= now: 
							if ama.end_date == None:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							if ama.end_date >= now:
								return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
							else:
								return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician},
							context_instance=RequestContext(request))
						else:
							return render_to_response("politician/noama.html", {"ama":ama, "late":True, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
					return render_to_response("politician/noama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician},
							context_instance=RequestContext(request))
			except MyPolitician.DoesNotExist:
				address = True
				states = STATE_CHOICES
				return render_to_response("politician/noama.html", {"ama":ama,"title":title, "slug":slug, "states":states, "extra":extra, "comments":comments, "address":address, "politician":politician},
							context_instance=RequestContext(request))
			return render_to_response("politician/noama.html", {"ama":ama, "title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
		if restrict == 2:
			try:
				local = Location.objects.get(user=user)
				poli = Location.objects.get(user=politician.politician)
				if local.state == poli.state:
					return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
				else:
					return render_to_response("politician/noama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
			except Location.DoesNotExist:
					return render_to_response("politician/noama.html", {"ama":ama,"title":title, "slug":slug, "states":states, "extra":extra, "comments":comments, "address":address, "politician":politician}, context_instance=RequestContext(request))
		if restrict == 4:
			return render_to_response("politician/ama.html", {"ama":ama,"title":title, "slug":slug, "extra":extra, "comments":comments, "politician":politician}, context_instance=RequestContext(request))
				
	except AMA.DoesNotExist:
		return HttpResponse("Town Hall does not exist!")
	return HttpResponse("something went wrong")
view_ama = login_required(view_ama)

def fav_comment(request):
	if request.method == "POST":
		try:
			comment = request.POST["comment"]
			slug = request.POST["slug"]
			types = request.POST["response"]
			ama = AMA.objects.get(slug=slug)
			user = request.user
			creator = Location.objects.get(user=user)
			if types == 'critical':
				response = Comments(comment = comment, article=ama, creator=creator, pro=False)
				response.save()
			else:
				response = Comments(comment=comment, article=ama, creator=creator)
				response.save()	
			response.vote.add(user)
			ama.rank +=1
			ama.save()
			return HttpResponseRedirect("/congress/" + slug + "/")
		except AMA.DoesNotExist:
			raise Http404('Page not Found')
fav_comment = login_required(fav_comment)

def comment(request):
	if request.method == "POST":
		try:
			comment = request.POST["comment"]
			slug = request.POST["slug"]
			ama = AMA.objects.get(slug=slug)
			user = request.user
			creator = Location.objects.get(user=user)
			response = Comments(comment = comment, article=ama, creator=creator)
			response.save()
			response.vote.add(user)
			ama.rank +=1
			ama.save()
			return HttpResponseRedirect("/congress/" + slug + "/")
		except AMA.DoesNotExist:
			raise Http404('Page not Found')
comment = login_required(comment)	

def rreply(request):
	if request.method == "POST":
		comment_id = request.POST["id"]
		comment = request.POST["comment"]
		get_comment = Comments.objects.get(id = comment_id)
		creator = Location.objects.get(user=request.user)
		if creator.politician == True:
			politician = Politician.objects.get(politician=request.user)
			if get_comment.article.politician == politician:
				reply = get_comment.replies.create(creator = creator, comment = comment)
				reply.reply_votes.add(request.user)
				response = Responses(ama = get_comment.article, creator = politician, comment=get_comment, reply=comment)
				response.save()
				send = "%s: <br /> %s" % (creator, comment)
				return HttpRespones(send)
		reply = get_comment.replies.create(creator = creator, comment = comment)
		reply.reply_votes.add(request.user)
		message = "%s: <br /> %s" % (creator, comment)
		return HttpResponse(message)
	return HttpResponse("Something went wrong")
rreply = login_required(rreply)	

def replyup(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			reply =  Replies.objects.get(id=id)
			user_voted = reply.reply_votes.filter(username=request.user.username)
			if not user_voted:
				reply.rank += 1
				reply.up += 1
				reply.reply_votes.add(request.user)
				reply.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve reply")
replyup = login_required(replyup)

def replydown(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			reply =  Replies.objects.get(id=id)
			user_voted = reply.reply_votes.filter(username=request.user.username)
			if not user_voted:
				reply.rank -= 1
				reply.down += 1
				reply.reply_votes.add(request.user)
				reply.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve reply")
replydown = login_required(replydown)

def town_up(request):
	if request.is_ajax():
		if 'slug' in request.GET:
			slug = request.GET['slug']
			ama = AMA.objects.get(slug=slug)
			user = request.user
			user_voted = ama.voters.filter(username=user.username)
			if not user_voted:
				user_down = ama.downvoters.filter(username=user.username)
				if not user_down:
					ama.rank += 1
					ama.up += 1
					ama.voters.add(user)
					ama.save()
					return HttpResponse("Thank you for voting.")
				else:
					ama.downvoters.remove(user)
					ama.rank += 1
					ama.down -= 1
					ama.up += 1
					ama.voters.add(user)
					ama.save()
					return HttpResponse("We have changed your vote to 'Agree'")
			return HttpResponse("You already voted!")
		return HttpResponse("Error, Townhall not Found")
	return HttpResponse("Ajax Error")
town_up = login_required(town_up)

def town_down(request):
	if request.is_ajax():
		if 'slug' in request.GET:
			slug = request.GET['slug']
			ama = AMA.objects.get(slug=slug)
			user = request.user
			user_voted = ama.downvoters.filter(username=user.username)
			if not user_voted:
				user_up = ama.voters.filter(username=user.username)
				if not user_up:
					ama.rank -= 1
					ama.down += 1
					ama.downvoters.add(user)
					ama.save()
					return HttpResponse("Thank you for voting.")
				else:
					ama.voters.remove(user)
					ama.rank -= 1
					ama.up -= 1
					ama.down += 1
					ama.downvoters.add(user)
					ama.save()
					return HttpResponse("We have changed your vote to 'Disagree'")
			return HttpResponse("You already voted!")
		return HttpResponse("Error, Townhall not Found")
	return HttpResponse("Ajax Error")
town_down = login_required(town_down)
			
def up(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			comment =  Comments.objects.get(id=id)
			user_voted = comment.vote.filter(username=request.user.username)
			if not user_voted:
				comment.rank += 1
				comment.up += 1
				comment.vote.add(request.user)
				comment.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve comment")
up = login_required(up)

def down(request):
	if request.is_ajax(): 
		if 'id' in request.GET:
			id = request.GET['id']
			comment =  Comments.objects.get(id=id)
			user_voted = comment.vote.filter(username=request.user.username)
			if not user_voted:
				comment.rank -= 1
				comment.down += 1
				comment.vote.add(request.user)
				comment.save()
				return HttpResponse("Thank you for voting.")
			return HttpResponse("You already voted!")
		return HttpResponse("Could not retrieve comment")
down = login_required(down)

def report(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				comment = Comments.objects.get(id=id)
				user_voted = comment.flag_votes.filter(username=request.user.username)
				if not user_voted:
					comment.flag += 1
					comment.flag_votes.add(request.user)
					comment.save()
					message = "You have successfully reported %s's comment" % (comment.creator.name)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's comment!" % (comment.creator.name)
					return HttpResponse(message)
			except Ask_Comment.DoesNotExist:
				raise Http404('Comment not Found.')
			return HttpResponseRedirect("/" + slug + "/")
	return HttpResponseRedirect("/" + slug + "/")
report = login_required(report)


def unreportcomment(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				comment = Comments.objects.get(id=id)
				user_voted = comment.flag_votes.filter(username=request.user.username)
				if not user_voted:
					comment.flag -= 1
					comment.flag_votes.add(request.user)
					comment.save()
					message = "You have successfully unreported %s's comment" % (comment.creator.name)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's comment!" % (comment.creator.name)
					return HttpResponse(message)
			except Ask_Comment.DoesNotExist:
				raise Http404('Comment not Found.')
			return HttpResponse("Something went wrong")
	return HttpResponse("Something went wrong")
unreportcomment = login_required(unreportcomment)


def unreportreply(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				reply = Replies.objects.get(id=id)
				user_voted = reply.reply_flaggers.filter(username=request.user.username)
				if not user_voted:
					reply.flag -= 1
					reply.reply_flaggers.add(request.user)
					reply.save()
					message = "You have successfully unreported %s's reply" % (reply.creator.name)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's reply!" % (reply.creator.name)
					return HttpResponse(message)
			except Ask_Reply.DoesNotExist:
				raise Http404('Reply not Found.')
			return HttpResponseRedirect("/" + slug + "/")
		return HttpResponse("Something went wrong")
	return HttpResponse("Something went wrong")

unreportreply = login_required(unreportreply)

def delete(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				comment = Comments.objects.get(id=id)
				comment.deleted = True
				comment.save()
			except Comments.DoesNotExist:
				return HttpResponse("Fail")
			return HttpResponse("Comment successfully deleted")
delete = login_required(delete)

def reply_delete(request):
	if 'id' in request.GET:
		try:
			id = request.GET['id']
			comment = Replies.objects.get(id=id)
			comment.delete = True
			comment.save()
		except Replies.DoesNotExist:
			return HttpResponse("Fail")
		return HttpResponse("Reply successfully deleted")
reply_delete = login_required(reply_delete)


#, vote = comment.vote, flag = comment.flag, flag_votes=comment.flag_votes, replies = comment.replies
def reportreply(request):
	if request.is_ajax():
		if 'id' in request.GET:
			try:
				id = request.GET['id']
				reply = Replies.objects.get(id=id)
				user_voted = reply.reply_flaggers.filter(username=request.user.username)
				if not user_voted:
					reply.flag += 1
					reply.reply_flaggers.add(request.user)
					reply.save()
					message = "You have successfully reported %s's reply" % (reply.creator.name)
					return HttpResponse(message)
				else:
					message = "You have already reported %s's reply!" % (reply.creator.name)
					return HttpResponse(message)
			except Ask_Reply.DoesNotExist:
				raise Http404('Reply not Found.')
	return HttpResponse("Something went wrong")
reportreply = login_required(reportreply)

def favorite(request, slug):
	if request.is_ajax():
		post = AMA.objects.get(slug=slug)
		try:
			fav = Favorite.objects.get(user=request.user)
			if fav.ama.filter(slug=slug):
				return HttpResponse("Already favorited")
			else:
				fav.ama.add(post)
				fav.save()
				return HttpResponse("Successfully added to your favorites")
		except Favorite.DoesNotExist:
			fav = Favorite(user=request.user)
			fav.save()
			fav.ama.add(post)
			fav.save()
			return HttpResponse("Successfully added to your favorites")
		return HttpResponse("problem1")
	return HttpResponse("problem2")
favorite = login_required(favorite)


def cloudhall(request):
	cloudhalls = AMA.objects.filter(creation_date__lte=datetime.now())
	return render_to_response("politician/cloudhall.html", {"cloudhalls":cloudhalls}, context_instance=RequestContext(request))
