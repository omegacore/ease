"""Django consults this page to determine the html that should be sent
 to the user
"""


from django.shortcuts import render, redirect

from django.views import generic,View
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.generic.edit import (CreateView, UpdateView, DeleteView)

from account_mgr_app.models import Profile
import account_mgr_app
from .models import Alert, Trigger 
from .forms import configAlert, configTrigger, deleteAlert, detailAlert

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm
from django.utils.decorators import method_decorator

from django.shortcuts import get_object_or_404
from django.http import Http404

from django.core.urlresolvers import reverse
from django.urls import reverse_lazy


from django.forms.formsets import formset_factory
from django.db import transaction, IntegrityError, models
from django.contrib import messages


@login_required()
def list_all(request):
    """Currently unused - Draw a page with a full list of PVs and Alerts.

    Attributes
    ----------
    request : django.http.HttpRequest

    
    Returns
    -------
    django.http.HttpResponse
    """
    context = {}
    context['alert_list'] = Alert.objects.all()
    context['user'] = request.user
    return render( request, 'debug_list_all.html', context)


@method_decorator(login_required, name = 'dispatch')
class Title_page(generic.ListView):
    template_name = 'title.html'
    form_class = configAlert
    paginate_by = 30
    
    def title(request):
       context = {}
       context['user'] = request.user
       return render( request, 'title.html', context)
   
    def get_queryset(self):
        new_context = Alert.objects.all().order_by('name')
        return new_context
   

@method_decorator(login_required, name = 'dispatch')
class alerts_all(generic.ListView):
    """Currently unused - Draw a page with a full list of PVs and Alerts

    Args
    ____
        request : django.http.HttpRequest

    Returns
    -------
        render : django.http.HttpResponse
    """
    model = Alert
    template_name = 'alerts_all.html'
    paginate_by = 30

    def get_queryset(self):
        new_context = Alert.objects.all().order_by('name')
        query = self.request.GET.get("q")#
        if query:
            new_context = new_context.filter(name__icontains=query)#
        return new_context

@method_decorator(login_required, name = 'dispatch')
class alert_detail(View):
    def get(self, request, *args, **kwargs):
        self.pk = kwargs.get("pk",None)
        try:
            alert_inst = get_object_or_404(Alert,pk=self.pk)
        except Http404:
            return HttpResponseRedirect(reverse('alerts_page_all'))
        
        if request.user.profile in alert_inst.owner.all():
            return HttpResponseRedirect(reverse(
                    'alert_config',
                    kwargs={'pk':self.pk}))

        subscribed = False
        if request.user.profile in alert_inst.subscriber.all():
            subscribed = True
        form = detailAlert(
            initial = {
                'new_subscribe': subscribed
            }
        )

        context = {
            'alert': alert_inst,
            'form':form,
        }
    
        return render( 
            request, 
            'alert_detail.html', 
            context
        )

    def post(self, request, *args, **kwargs):
        self.pk = kwargs.get("pk",None)
        try:
            alert_inst = get_object_or_404(Alert,pk=self.pk)
        except Http404:
            return HttpResponseRedirect(reverse('alerts_page_all'))
        
        if request.user.profile in alert_inst.owner.all():
            return HttpResponseRedirect(reverse(
                    'alert_config',
                    kwargs={'pk':self.pk}))

        form = detailAlert(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('new_subscribe'):
                try:
                    alert_inst.subscriber.add(request.user.profile)
                except ValueError:
                    # instance already exists -- pass
                    pass
            else:
                try:
                    alert_inst.subscriber.remove(request.user.profile)
                except ValueError:
                    # instance already removed -- pass
                    pass

            return HttpResponseRedirect(reverse('alerts_page_all'))


@method_decorator(login_required, name = 'dispatch')
class alert_config(View):
    def get(self, request, *args, **kwargs):
        """Draw the page when create or config is loaded by the user
        """
        self.pk = kwargs.get("pk",None)
        if self.pk == None:
            create = True
        else:
            create = False
            # attempt to fetch database entry for alert, redirect on fail 
            try:
                alert_inst = get_object_or_404(Alert,pk=self.pk)
            except Http404:
                return HttpResponseRedirect(reverse('alert_create'))

        if not create:
            # reject non-owner users
            if request.user.profile not in alert_inst.owner.all():
                return HttpResponseRedirect(reverse(
                        'alert_detail',
                        kwargs={'pk':self.pk}))

        if create:
            alert_inst = None
            alert_initial = {}
            trigger_initial = []
        else:
            if request.user.profile in alert_inst.subscriber.all():
                subscribed = True
            else:
                subscribed = False
            # prepare initial values for form fields showing current values
            
            initial_owner_list = User.objects.filter(
                profile__in=alert_inst.owner.all()
            )

            
            initial_usernames =  [
                u.username + " (" + u.last_name + ", " + u.first_name + ")" 
                for u in initial_owner_list
            ]

            initial_owners = ", ".join(sorted(initial_usernames))

            alert_initial = {
                'new_name': alert_inst.name,
                'new_owners': initial_owners,
                'new_subscribe': subscribed,
                'new_lockout_duration':alert_inst.lockout_duration,    
            }


            trigger_initial = [
                {   
                    'new_name': l.name,
                    'new_pv': l.value_src,
                    'new_value':l.value,
                    'new_compare':l.compare,
                } 
                for l in alert_inst.trigger_set.all()
            ]

        triggerFormSet = formset_factory(configTrigger)
        
        form = configAlert(initial = alert_initial)
        triggerForm = triggerFormSet(
            initial = trigger_initial,
            prefix='tg'
        )
        all_usernames =  [
            u.username + " (" + u.last_name + ", " + u.first_name + ")" 
            for u in User.objects.all()
        ]
        all_usernames = sorted(all_usernames)

        return render(
            request = request, 
            template_name = "alert_config.html", 
            context = {
                'form':form,
                'triggerForm':triggerForm,
                'alert':alert_inst,
                'create':create,
                'usernames': all_usernames,
            },
        )

    def post(self, request, *args, **kwargs):
        # DEBUG ONLY --------------------------------------
        if 0:
            print("")
            for x in sorted(request.POST):
                print("{:>20}  {:>20}  {:>20}".format(  
                    x,
                    str(dict(request.POST)[x]),
                    str(type(dict(request.POST)[x]))))
            print("")
        
            form = configAlert(request.POST,)
            #triggerForm = triggerFormSet(request.POST, prefix='tg')

            if form.is_valid():
                print(form.cleaned_data)
        # DEBUG ONLY --------------------------------------
        
        
        self.pk = kwargs.get("pk",None)
        triggerFormSet = formset_factory(configTrigger)
        if self.pk == None:
            create = True
        else:
            create = False
        
        form = configAlert(request.POST,)
        triggerForm = triggerFormSet(request.POST, prefix='tg')
        # if there is no preexisting Alert - create a new one
        if create:
            alert_inst = Alert()
            alert_inst.save()

        else:
            # attempt to get indicated alert instance, redirect on fail
            try:
                alert_inst = get_object_or_404(Alert,pk=self.pk)
            except Http404:
                return HttpResponseRedirect(reverse('alert_create'))

            if request.user.profile not in alert_inst.owner.all():
                return HttpResponseRedirect(reverse(
                        'alert_detail',
                        kwargs={'pk':self.pk}))        
         
        if form.is_valid():
            
            # Set/Modify the alert's name 
            alert_inst.name = form.cleaned_data['new_name']

            # Set/Modify the alert's list of owners
            alert_inst.owner.clear()
            for new_owner in form.cleaned_data['new_owners']:
                alert_inst.owner.add(new_owner)

            # Set/Modify the alert's lockout duration
            alert_inst.lockout_duration = form.cleaned_data[
                'new_lockout_duration']

            # Set/Modify the alert's subscription relation with the user
            if ((form.cleaned_data['new_subscribe'])
                and (request.user.profile not in alert_inst.subscriber.all())):
                    alert_inst.subscriber.add(request.user.profile)
            elif ((not form.cleaned_data['new_subscribe'])
                and (request.user.profile in alert_inst.subscriber.all())):
                    alert_inst.subscriber.remove(request.user.profile)
        
            alert_inst.save()

            new_triggers = []
            for single_trigger_form in triggerForm:
                # reexamine this section, is it still necessary?
                # do values occasionally return false? like new_subscribe
                if single_trigger_form.is_valid():

                    new_triggers.append(
                        Trigger(
                            name = single_trigger_form.cleaned_data.get(
                                'new_name'),
                            alert = alert_inst,
                            value_src = single_trigger_form.cleaned_data.get(
                                'new_pv'),
                            compare = single_trigger_form.cleaned_data.get(
                                'new_compare'),
                            value = single_trigger_form.cleaned_data.get(
                                'new_value'),
                        )
                    )
            
            try:
                # atomic prevents db change unless all changes are error free
                with transaction.atomic():
                    alert_inst.trigger_set.all().delete()
                    Trigger.objects.bulk_create(new_triggers)
                    pass

            except IntegrityError:
                pass
                #print("UPDATE FAILURE")
        else:
            all_usernames = sorted([usr.username for usr in User.objects.all()])
            return render(
                request = request, 
                template_name = "alert_config.html", 
                context = {
                    'form':form,
                    'triggerForm':triggerForm,
                    'alert':alert_inst,
                    'create':create,
                    'usernames':all_usernames,
                },
            )

        return HttpResponseRedirect(reverse('alerts_page_all'))


@login_required()
def alert_delete(request,pk=None,*args,**kwargs):
    """Draws deletion page for an alert.

    Args
    ____
        pk : int
            DB index of the displayed alert. PK is sent automatically from the 
            regex in url. 

    Note
    ____
        Having deletion occur on a post request is safer than a get request. 
        This page is designed solely to present the form required for receiving
        the post request.
    """
    for x in sorted(request.POST):
        print(x,"\t",request.POST[x])
    try:
        alert_inst = get_object_or_404(Alert,pk=pk)
    
    except Http404:
        return HttpResponseRedirect(reverse('alerts_page_all'))

    if request.method == "POST":
        deleteForm = deleteAlert(request.POST, )
        print("post detected")

        if deleteForm.is_valid():
            print("deleting")
            Alert.objects.filter(pk=pk).delete()
            return HttpResponseRedirect(reverse('alerts_page_all'))

        else:
            print("BAD FORM")

    else:
        deleteForm = deleteAlert()
    

    return render(
        request,
        "alert_delete.html",
        {'form':deleteForm,'alert':alert_inst},
    )

