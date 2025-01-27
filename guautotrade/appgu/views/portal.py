from django.core import serializers
from django.http import HttpResponse
import json
from django.contrib.auth.views import login
from django.shortcuts import render, redirect
from ..models import Vehicles, Vehicles_Tuscany, Dealers, Orders, NewsPosts, Events, Events_Tuscany, NewsPosts_Tuscany
from .. import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.db.models import Q


def index(request):
    if request.user.is_authenticated:
        return render(request, 'portal/portal.html')
    redirect(login)

# place an order in the portal
def order(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            newform = forms.AdminOrderForm()
        else:
            newform = forms.OrderForm()
        if request.method == "POST":
            if request.user.is_staff:
                form = forms.AdminOrderForm(request.POST)
            else:
                form = forms.OrderForm(request.POST)
            response_data = {'result': _('Failed to place order.'), 'status': 'failed', 'formerr': form.errors,'form': str(newform)}
            if form.is_valid():
                userid = request.user.id

                try:
                    if request.user.is_staff:
                        dealerobj = Dealers.objects.get(user=User.objects.get(pk=request.POST['forwho']))
                    else:
                        dealerobj = Dealers.objects.get(pk=User.objects.get(id=userid))
                except:
                    response_data = {'result': _('Order could not be placed.'), 'status': 'failed', 'formerr': _('No dealer found with the given ID.')}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )

                order = Orders(dealerID=dealerobj, model=request.POST['model'], colour=request.POST['colour'], homologation=True if 'homologation' in request.POST else False, custom_clearance=True if 'custom_clearance' in request.POST else False, additional_comments=request.POST['additional_comments'])
                order.save()

                response_data = {'result': _('Order has been succesfully placed.'), 'status': 'success'}
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return render(request, 'portal/base_form.html', {'form': newform, 'headerclass': 'portal', 'title': _('Order Form'), 'lead': _('Place an order for a vehicle')})
    return redirect(login)

def addnewspost(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            form = forms.NewsPostForm()
            if request.method == 'POST':
                form = forms.NewsPostForm(request.POST, request.FILES)
                if form.is_valid():
                    v = NewsPosts(banner=form.cleaned_data['banner'], title=request.POST['title'], headline=request.POST['headline'], quote=request.POST['quote'], quotefooter=request.POST['quotefooter'], description=request.POST['description'])
                    v.save()
                    response_data = {'result': 'Create succesful', 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.NewsPostForm()
                    response_data = {'result': 'Create unsuccesful', 'status': 'failed', 'formerr': form.errors,
                                     'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            return render(request, 'portal/base_form.html', {'form': form, 'fileUpload': 'True', 'title': 'Add News Post', 'lead': 'Here you can add news posts to the database, to be displayed on the website.'})
    return redirect(login)

# a personal dealer orderlist
def portalmyorders(request):
    if request.user.is_authenticated:
        if not request.user.is_staff:
            userid = request.user.id
            allOrders = Orders.objects.filter(dealerID=userid).order_by('-date')
            return render(request, 'portal/myorders.html', {'orders': allOrders})
    return redirect(login)

# an orderlist that can only be seen by a staff member (or superuser)
def portalorderlist(request):
    if request.user.is_authenticated:
        form = forms.PartialOrderForm()
        if request.method == "POST":

            obj = Orders.objects.get(pk=request.POST['change'])
            obj.model = request.POST['inp3']
            obj.colour = request.POST['inp4']
            obj.scheduled_completion_date = request.POST['inp8']

            obj.homologation = request.POST['check6x']
            obj.custom_clearance = request.POST['check7x']
            obj.deposit_received = request.POST['check9x']
            obj.payment_received = request.POST['check10x']

            if request.FILES:
                obj.invoice = request.FILES['invoice']

            if str(request.POST['check6x']) == 'True' and str(obj.homologation) == 'False':
                obj = True
            elif str(request.POST['check6x']) == 'False' and str(obj.homologation) == 'True':
                obj = False

            if request.POST['check7x'] == 'True' and obj.custom_clearance == 'False':
                obj = True
            elif str(request.POST['check7x']) == 'False' and str(obj.custom_clearance) == 'True':
                obj = False

            if request.POST['check9x'] == 'True' and obj.deposit_received == 'False':
                obj = True
            elif str(request.POST['check9x']) == 'False' and str(obj.deposit_received) == 'True':
                obj = False

            if request.POST['check10x'] == 'True' and obj.payment_received == 'False':
                obj = True
            elif str(request.POST['check10x']) == 'False' and str(obj.payment_received) == 'True':
                obj = False

            obj.save()

        allOrders = Orders.objects.all().order_by('-date')
        if allOrders:
            exists = True
        else:
            exists = False
        return render(request, 'portal/orderlist.html', {'orders': allOrders, 'form': form, 'exists': exists})
    return redirect(login)

# an admin page to register a dealer
def registerdealer(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = forms.RegistrationDealerForm(request.POST)
            if form.is_valid():
                form.save()

                response_data = {'result': _("Succesfully registered dealer."), 'status': 'success'}
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                newform = forms.RegistrationDealerForm()
                response_data = {'result': _("Failed to register dealer."), 'status': 'failed', 'formerr': form.errors,
                                 'form': str(newform)}

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

        form = forms.RegistrationDealerForm()
        return render(request, 'portal/base_form.html', {'form': form, 'title': _('Register Dealer'), 'lead': _('Here you can register a new dealer.')})
    return redirect(login)

# a superuser page to register an admin
def registeradmin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == "POST":
                form = forms.RegistrationAdminForm(request.POST)
                if form.is_valid():
                    form.save()

                    response_data = {'result': _("Succesfully registered admin."), 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.RegistrationAdminForm()
                    response_data = {'result': _("Failed to register admin."), 'status': 'failed', 'formerr': form.errors,
                                     'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            form = forms.RegistrationAdminForm()
            return render(request, 'portal/base_form.html', {'form': form, 'title': _('Register Admin'), 'lead': _('Here you can register a new administrator.')})
    return redirect(login)

# a staff page to add a vehicle to the database, which will be displayed on the home page
def addvehicle(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            form = forms.VehicleForm()
            if request.method == 'POST':
                form = forms.VehicleForm(request.POST, request.FILES)
                if form.is_valid():
                    if request.POST['companyselect'] == 'shelby':
                        v = Vehicles(image=form.cleaned_data['image'], model=request.POST['model'], headline=request.POST['headline'], description=request.POST['description'])
                    else:
                        v = Vehicles_Tuscany(image=form.cleaned_data['image'], model=request.POST['model'], headline=request.POST['headline'], description=request.POST['description'])

                    v.save()

                    response_data = {'result': _('Succesfully added vehicle.'), 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.VehicleForm()
                    response_data = {'result': _('Failed to add vehicle.'), 'status': 'failed', 'formerr': form.errors, 'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            return render(request, 'portal/base_form.html', {'form': form, 'fileUpload': 'True', 'title': _('Add Vehicle'), 'lead': _('Here you can add vehicles to the database, to be displayed on the website.'), 'selectCompany': True})
    return redirect(login)

# a staff page to add a newspost to the database, which will be displayed on the home page
def addnewspost(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            form = forms.NewsPostForm()
            if request.method == 'POST':
                form = forms.NewsPostForm(request.POST, request.FILES)
                if form.is_valid():
                    if request.POST['companyselect'] == 'shelby':
                        v = NewsPosts(banner=form.cleaned_data['banner'], title=request.POST['title'], headline=request.POST['headline'], quote=request.POST['quote'], quotefooter=request.POST['quotefooter'], description=request.POST['description'])
                    else:
                        v = NewsPosts_Tuscany(banner=form.cleaned_data['banner'], title=request.POST['title'], headline=request.POST['headline'], quote=request.POST['quote'], quotefooter=request.POST['quotefooter'], description=request.POST['description'])
                    v.save()
                    response_data = {'result': _('Succesfully added newspost.'), 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.NewsPostForm()
                    response_data = {'result': _('Failed to add newspost.'), 'status': 'failed', 'formerr': form.errors,
                                     'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            return render(request, 'portal/base_form.html', {'form': form, 'fileUpload': 'True', 'title': _('Add News Post'), 'lead': _('Here you can add news posts to the database, to be displayed on the website.'), 'selectCompany': True})
    return redirect(login)

def addeventpost(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            form = forms.EventForm()
            if request.method == 'POST':
                form = forms.EventForm(request.POST)
                if form.is_valid():
                    if request.POST['companyselect'] == 'shelby':
                        e = Events(title=request.POST['title'], description=request.POST['description'], link=request.POST['link'], date=request.POST['date'])
                    else:
                        e = Events_Tuscany(title=request.POST['title'], description=request.POST['description'], link=request.POST['link'], date=request.POST['date'])
                    e.save()
                    response_data = {'result': _("Event succesfully added."), 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.EventForm()
                    response_data = {'result': _("Failed to add event."), 'status': 'failed', 'formerr': form.errors,
                                     'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            return render(request, 'portal/base_form.html', {'form': form, 'title': _('Add Event'), 'lead': _('Here you can add events to the database, to be displayed on the events calendar.'), 'selectCompany': True})
    return redirect(login)

def addmapdealer(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            form = forms.MapDealerForm()
            if request.method == 'POST':
                form = forms.MapDealerForm(request.POST)
                if form.is_valid():
                    form.save()

                    response_data = {'result': _('Succesfully added dealer to the map.'), 'status': 'success'}
                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
                else:
                    newform = forms.MapDealerForm()
                    response_data = {'result': _('Failed to add dealer to the map.'), 'status': 'failed', 'formerr': form.errors,
                                     'form': str(newform)}

                    return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                    )
            return render(request, 'portal/base_form.html', {'form': form, 'title': _('Add Map Dealer for Shelby'), 'lead': _('Here you can add a dealer to the map, to be displayed on the website.'), 'extra': '<input type="hidden" id="region">'})
    return redirect(login)


def changePassword(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form)
                response_data = {'result': _('Succesfully changed password'), 'status': 'success'}
                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            else:
                newform = PasswordChangeForm(request.user)
                response_data = {'result': _('Failed to change password'), 'status': 'failed', 'formerr': form.errors,
                                 'form': str(newform)}

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
        form = PasswordChangeForm(request.user)
        return render(request, 'portal/base_form.html', {'form': form, 'title': _('Change Password'), 'lead': _('If you would like to change your password, fill out this form.')})
    return redirect(login)

def search(request):
    if request.method == 'POST':
        search_text = request.POST['searchtext']
        users = User.objects.all().filter(Q(first_name__icontains=search_text)
                                          | Q(last_name__icontains=search_text)
                                          | Q(username__icontains=search_text)
                                          | Q(email__icontains=search_text))

        serialized_obj = serializers.serialize("json", users)
        return HttpResponse(serialized_obj, content_type="application/json")
    return render(request, 'portal/search.html')