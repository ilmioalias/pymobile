# -*- coding: utf-8 -*-

from django.http import HttpResponse          
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

import pymobile.administration.models as models
import pymobile.administration.forms as forms
import pymobile.administration.tables as tables
import pymobile.administration.utils as u
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

# Create your views here.

TMP_ADMIN="cliente/admin.html"
TMP_FORM="cliente/modelform.html"
TMP_DEL="cliente/deleteform.html"
TMP_VIEW="cliente/view.html"

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def init(request):
    template = TMP_ADMIN
    objs = models.Cliente.objects.all()
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
        
    table = tables.ClienteTable(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = forms.ClienteFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform}
    return render_to_response(template, data,
                              context_instance=RequestContext(request)) 

@login_required
def add_object(request):  
    template = TMP_FORM
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.ClienteForm(post_query)
        
        if form.is_valid():
            new_obj = form.save()
            
            logger.debug("{}: aggiunto il cliente {} [id={}]"
                         .format(request.user, new_obj, new_obj.id))
            messages.add_message(request, messages.SUCCESS, 'Cliente aggiunto')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_cliente")) 
            else:
                url = reverse("init_cliente")
                return HttpResponse('''
                                <script type='text/javascript'>
                                    opener.redirectAfter(window, '{}');
                                </script>'''.format(url))
    else:
        form = forms.ClienteForm()    

    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
def mod_object(request, object_id):
    obj = get_object_or_404(models.Cliente, pk=object_id)
    
    if u.is_telefonista(request.user):
        # se l'utente connesso è un telefonista può modificare solamente clienti
        # relativi a suoi appuntamenti non ancora assegnati
        user = request.user
        profile = user.dipendente
        if (models.Appuntamento.objects.filter(cliente=obj).exclude(telefonista=profile).exists() |
            models.Appuntamento.objects.filter(agente__isnull=False, cliente=obj).exists()):
            messages.add_message(request, messages.ERROR, "Non è possibile modificare il cliente:"\
                                 " contattare l'amministratore")
            return HttpResponseRedirect(reverse("view_cliente", args=[object_id,]))
    
    template = TMP_FORM
    action = "mod"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.ClienteForm(post_query, instance=obj)
    
        if form.is_valid():
            new_obj = form.save()
            
            logger.debug("{}: modificato il cliente {} [id={}]"
                         .format(request.user, new_obj, new_obj.id))
            messages.add_message(request, messages.SUCCESS, 'Cliente modificato')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_cliente")) 
            else:
                url = reverse("view_cliente", args=[object_id,])
                return HttpResponse('''
                                <script type='text/javascript'>
                                    opener.redirectAfter(window, '{}');
                                </script>'''.format(url))                 
    else: 
        form = forms.ClienteForm(instance=obj)
    
    data = {"modelform": form, "action": action, "cliente": obj,}
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
            models.Cliente.objects.filter(id__in=ids).delete()
            
            if len(ids) == 1:
                logger.debug("{}: eliminato il cliente [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Cliente elimnato')
            elif len(ids) > 1:
                logger.debug("{}: eliminati i clienti [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Clienti eliminati')
            url = reverse("init_cliente")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Cliente.objects.filter(id__in=ids)
    
    logger.debug("{}: ha intenzione di eliminare i clienti {}"
                 .format(request.user, [(str(obj), "id=" + str(obj.id)) for obj in objs]))
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))
