# -*- coding: utf-8 -*-

from django.http import HttpResponse          
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test

import pymobile.administration.forms as forms
import pymobile.administration.tables as tables
import pymobile.administration.utils as u

# Create your views here.

TMP_ADMIN="account/admin.html"
TMP_FORM="account/modelform.html"
TMP_DEL="account/deleteform.html"
TMP_VIEW="account/view.html"
TMP_LOGIN="index.html"

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
#        next_page = request.POST.get("next")
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                
                messages.add_message(request, messages.SUCCESS, 'Benvenuto {}'.format(user))
                # Redirect to a success page.
                # FIXME: qui deve eessere ridirezionato verso una home page
                # FIXME: usare "next_page"?!
                if u.is_telefonista(user):
                    url = reverse("init_appuntamento")
                else:
                    url = reverse("init_dipendente")
                return HttpResponseRedirect(url)
            else:
                # Return a 'disabled account' error message
                messages.add_message(request, messages.ERROR, 'Account {} non più attivo'.format(user))
                return HttpResponseRedirect(reverse("login"))
        else:
            # Return an 'invalid login' error message.
            messages.add_message(request, messages.ERROR, 'Nome utente o Password errati'.format(user))
            return HttpResponseRedirect(reverse("login"))
    else:
        return render_to_response(TMP_LOGIN,
                                  context_instance=RequestContext(request))

@login_required     
def logout_user(request):
    auth.logout(request)
    # Redirect to a success page.
    messages.add_message(request, messages.SUCCESS, 'Logout effettuato')
    return HttpResponseRedirect(reverse("login"))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def init(request):
    template = TMP_ADMIN
    objs = User.objects.filter(is_superuser=False)
    
    initial = {}
    pag = 1
    ordering = None
    
    if request.method == "GET" and request.GET:
        query_get = request.GET.copy()
        initial = {}
        
        if query_get.has_key("pag"):
            pag = query_get["pag"]
            del query_get["pag"]
        if query_get.has_key("sort"):
            ordering = query_get["sort"]
            del query_get["sort"]
        if query_get:
            objs, initial = u.filter_objs(objs, query_get)
        
    table = tables.AccountTable(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = forms.AccountFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform,}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))        

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def add_object(request):  
    template = TMP_FORM
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.AccountForm(post_query)
        
        if form.is_valid():
            form.save()
            
            messages.add_message(request, messages.SUCCESS, 'Account aggiunto')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_account")) 
            else:
                return HttpResponseRedirect(reverse("init_account"))
    else:
        form = forms.AccountForm()    

    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def mod_object(request, object_id):
    template = TMP_FORM
    action = "mod"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(User, pk=object_id)
        form = forms.AccountForm(post_query, instance=obj)
        
        if form.is_valid():
            form.save()
            
            messages.add_message(request, messages.SUCCESS, 'Account modificato')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_account")) 
            else:
                return HttpResponseRedirect(reverse("view_account", 
                                                    args=[object_id]))
    else:
        obj = get_object_or_404(User, pk=object_id)
        # groups è un campo manytomany dobbiamo inizializzarlo a parte
        group = obj.groups.all()[0]
        # se l'account è di tipo "telefonista" ricaviamo il profilo collegato
        if group.name == "telefonista":
            profile = obj.dipendente
        else:
            profile = ""
        form = forms.AccountForm(instance=obj, initial={"groups": group,
                                                        "profile": profile})
#        form.initial["groups"] = group
    
    data = {"modelform": form, "action": action, "account": obj,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def del_object(request):
    template = TMP_DEL
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            User.objects.filter(id__in=ids).delete()
            
            if len(ids) > 1:
                messages.add_message(request, messages.SUCCESS, 'Appuntamenti eliminati')
            elif len(ids) == 1:
                messages.add_message(request, messages.SUCCESS, 'Account eliminato')
            url = reverse("init_account")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = User.objects.filter(id__in=ids)
    
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def mod_password(request, object_id):
    template = "account/mod_password.html"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(User, pk=object_id)
        form = forms.AccountModPasswordForm(post_query, initial={"account_id": obj.id})
        
        if form.is_valid():
            form.save()
            
            messages.add_message(request, messages.SUCCESS, 'Password modificata')    
            return HttpResponseRedirect(reverse("view_account", 
                                                    args=[object_id]))
    else:
        obj = get_object_or_404(User, pk=object_id)
        form = forms.AccountModPasswordForm(initial={"account_id": obj.id,})
    
    data = {"modelform": form, "account": obj,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))
