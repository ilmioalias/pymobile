# -*- coding: utf-8 -*-

from django.http import HttpResponse          
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

import pymobile.administration.models as models
import pymobile.administration.forms as forms
import pymobile.administration.tables as tables
import pymobile.administration.utils as u
import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

# Create your views here.

TMP_ADMIN="appuntamento/admin.html"
TMP_FORM="appuntamento/modelform.html"
TMP_DEL="appuntamento/deleteform.html"
TMP_VIEW="appuntamento/view.html"
TMP_ASSIGN="appuntamento/assignform.html"
TMP_REF="appuntamento/referente_view.html"
TMP_REFFORM="appuntamento/referente_modelform.html"
# questa pagina mi serve perché referente estende base.html per la modfica
TMP_REFMODFORM="appuntamento/referente_mod_modelform.html"
TMP_REFDELFORM="appuntamento/referente_deleteform.html"

@login_required
def init(request):
    template = TMP_ADMIN
    if u.is_telefonista(request.user):
        user = request.user
        profile = user.dipendente
        objs = models.Appuntamento.objects.filter(agente__isnull=True,
                                                  telefonista=profile,)
    else:    
        objs = models.Appuntamento.objects.all()
    # determiniamo gli agenti per l'assegnazione, devono essere solo quelli attivi 
    # il giorno successivo
    day = datetime.datetime.today().date() + datetime.timedelta(1)
    agenti = models.Dipendente.objects.filter(ruolo="agt", 
                                              data_assunzione__lte=day)\
                                      .exclude(data_licenziamento__lt=day)
    
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
        
    table = tables.AppuntamentoTable(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = forms.AppuntamentoFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform, "agenti": agenti}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))        

@login_required
def add_object(request):  
    template = TMP_FORM
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.AppuntamentoForm(post_query)
        
        if form.is_valid():
            appuntamento = form.save()
            
            logger.debug("{}: aggiunto l'appuntamento {}".format(request.user, appuntamento))
            messages.add_message(request, messages.SUCCESS, 'Appuntamento aggiunto')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_appuntamento")) 
            else:
                return HttpResponseRedirect(reverse("init_appuntamento"))
    else:
        if u.is_telefonista(request.user):
            user = request.user
            profile = user.dipendente
            form = forms.AppuntamentoForm(telefonista=profile)
        else:
            form = forms.AppuntamentoForm()    

    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
def mod_object(request, object_id):
    template = TMP_FORM
    action = "mod"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(models.Appuntamento, pk=object_id)
        form = forms.AppuntamentoForm(post_query, instance=obj)
    
        if form.is_valid():
            appuntamento = form.save()
            
            logger.debug("{}: modificato l'appuntamento {}".format(request.user, appuntamento))
            messages.add_message(request, messages.SUCCESS, 'Appuntamento modificato')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_appuntamento")) 
            else:
                return HttpResponseRedirect(reverse("view_appuntamento", 
                                                    args=[object_id]))
    else:
        obj = get_object_or_404(models.Appuntamento, pk=object_id) 
        form = forms.AppuntamentoForm(instance=obj)
    
    data = {"modelform": form, "action": action, "appuntamento": obj,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
def del_object(request):
    template = TMP_DEL
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.Appuntamento.objects.filter(id__in=ids).delete()
            
            if len(ids) > 1:
                messages.add_message(request, messages.SUCCESS, 'Appuntamenti eliminati')
            elif len(ids) == 1:
                messages.add_message(request, messages.SUCCESS, 'Appuntamento eliminato')
            url = reverse("init_appuntamento")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Appuntamento.objects.filter(id__in=ids)
    
    logger.debug("{}: ha intenzione di eliminare gli appuntamenti {}".format(request.user, [str(obj) for obj in objs]))
    
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def assign_object(request):
    template = TMP_ASSIGN
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id") and query_post.has_key("agente"):
            # assegnamo
            ids = query_post.getlist("id")
            agente_id = query_post["agente"]
            agente = get_object_or_404(models.Dipendente, id=agente_id)
            appuntamenti = models.Appuntamento.objects.filter(id__in=ids)
            
            models.Appuntamento.objects.filter(id__in=ids).update(agente=agente_id)
            
            if request.POST.has_key("send_mail"):
                # inviamo l'email
                to_email = agente.email
                from_email = "agenzia"
                subject = "Prossimi appuntamenti"
                msg = "Appuntamenti assegnati:\n"
                for appuntamento in appuntamenti:
                    msg += "\t- {}\n".format(appuntamento)
                msg += "\nBuon Lavoro."
                send_mail(subject, 
                          msg,
                          from_email,
                          [to_email,], 
                          fail_silently=False,)              
                
                logger.debug("{}: assegnati gli appuntamenti {} e inviata mail all'agente {}"
                             .format(request.user, 
                                     [str(appuntamento) for appuntamento in appuntamenti],
                                     agente))
                messages.add_message(request, messages.SUCCESS, 'Agente assegnato ed EMail inviata')
                url = reverse("init_appuntamento")
                return HttpResponse('''
                    <script type='text/javascript'>
                        opener.redirectAfter(window, '{}');
                    </script>'''.format(url))
            
            logger.debug("{}: assegnati gli appuntamenti {} all'agente {}"
                         .format(request.user, 
                                 [str(appuntamento) for appuntamento in appuntamenti],
                                 agente))
            messages.add_message(request, messages.SUCCESS, 'Agente assegnato')
            url = reverse("init_appuntamento")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    
    if query_get.has_key("id") and query_get.has_key("agente"):
        ids = query_get.getlist("id")
        agente_id = query_get["agente"]
        agente = get_object_or_404(models.Dipendente, id=agente_id)
        objs = models.Appuntamento.objects.filter(id__in=ids)
        
        data = {"objs": objs, "agente": agente}
        return render_to_response(template,
                                  data,
                                  context_instance=RequestContext(request))

@login_required
def add_child_object(request, field_name):
    action = "add" 
    
    def get_child_form(field_name):  
        f = field_name.capitalize() + "Form"
        if field_name == "cliente":
            t = "appuntamento/cliente_modelform.html"
        elif field_name == "agente":
            t = "appuntamento/agente_modelform.html"
        elif field_name == "telefonista":
            t = "appuntamento/telefonista_modelform.html"
        elif field_name == "referente":
            t = "appuntamento/referente_modelform.html"               
        return getattr(forms, f), t  
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form_class, template = get_child_form(field_name)
        form = form_class(post_query)
        
        if form.is_valid():
            try:
                new_obj = form.save()
                if field_name == "agente":
                    logger.debug("{}: aggiunto l'agente {} [chiave esterna di appuntamento]"
                                 .format(request.user, new_obj))
                else:
                    logger.debug("{}: aggiunto il {} {} [chiave esterna di appuntamento]"
                                 .format(request.user, field_name, new_obj))
            except form.ValidationError:
                new_obj = None
                                
            if new_obj: 
                return HttpResponse('''
                    <script type="text/javascript">
                        opener.closeSubModelform(window, "{}", "{}");
                    </script>'''.format(new_obj.pk, new_obj))
    else:
        form_class, template = get_child_form(field_name)
        form = form_class()
      
    data = {"modelform": form, "action": action,}     
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
def view_referente(request, object_id, referente_id):
    template = TMP_REF
    
    appuntamento_id = object_id
    appuntamento = get_object_or_404(models.Appuntamento, pk=appuntamento_id)
    referente = get_object_or_404(models.Referente, pk=referente_id)
    
    data = {"appuntamento": appuntamento, "object": referente}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
def mod_referente(request, object_id, referente_id):
    template = TMP_REFMODFORM
    action = "mod"
    
    appuntamento_id = object_id
    obj = get_object_or_404(models.Appuntamento, pk=appuntamento_id)
    
    if request.method == "POST":
        post_query = request.POST.copy()
        referente = get_object_or_404(models.Referente, pk=referente_id)
        form = forms.ReferenteForm(post_query, instance=referente)
    
        if form.is_valid():
            referente = form.save()
            
            logger.debug("{}: modificato il referente {} [chiave esterna di appuntamento]"
                                 .format(request.user, referente))
            messages.add_message(request, messages.SUCCESS, 'Referente modificato')
            return HttpResponseRedirect(reverse("view_referente", 
                                                args=[appuntamento_id, referente_id]))
    else:
        referente = get_object_or_404(models.Referente, pk=referente_id) 
        form = forms.ReferenteForm(instance=referente)
    
    data = {"modelform": form, "action": action, "appuntamento": obj,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
def del_referente(request, object_id):
    template = TMP_REFDELFORM
    
    appuntamento_id = object_id
    app = get_object_or_404(models.Appuntamento, pk=appuntamento_id)
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            referente_id = query_post["id"]
            models.Referente.objects.get(pk=referente_id).delete()
            
            logger.debug("{}: eliminato il referente [chiave esterna di appuntamento]"
                         .format(request.user))            
            messages.add_message(request, messages.SUCCESS, 'Referente eliminato')
            url = reverse("view_appuntamento", args=[appuntamento_id])
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    referente_id = query_get["id"]
    referente = get_object_or_404(models.Referente, pk=referente_id)      
    
    logger.debug("{}: ha intenzione di eliminare il referente {} [chiave esterna di appuntamento]"
                                 .format(request.user, referente))
    data = {"appuntamento": app, "obj": referente}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def send_mail_to_agente(request, object_id):
    template = "appuntamento/send_mailform.html"
    
    appuntamento_id = object_id
    appuntamento = get_object_or_404(models.Appuntamento, pk=appuntamento_id)
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("agente"):
            # cancelliamo
            agente_id = query_post.get("agente")
            agente = get_object_or_404(models.Dipendente, id=agente_id)
            
            # inviamo l'email
            to_email = agente.email
            from_email = "agenzia"
            subject = "Prossimi appuntamenti"
            msg = "Appuntamenti assegnati:\n"
            msg += "\t- {}\n".format(appuntamento)
            msg += "\nBuon Lavoro."
            send_mail(subject, 
                      msg,
                      from_email,
                      [to_email,], 
                      fail_silently=False,)
            
            logger.debug("{}: email inviata all'agente {} relativa all'appuntamento {}"
                         .format(request.user, 
                                 agente, 
                                 appuntamento,)) 
            messages.add_message(request, messages.SUCCESS, 'EMail inviata')
            url = reverse("view_appuntamento", args=[appuntamento_id])
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    agente_id = query_get.get("agente")
    agente = get_object_or_404(models.Dipendente, id=agente_id)      
    
    data = {"appuntamento": appuntamento, "agente": agente}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

#def filter_lookup(request):
#    res = []
#    
#    if request.GET:
#        query = request.GET.copy()
#
#        if query.has_key("cliente"):   
#            v = query["cliente"]
#            
#            search = Q(denominazione__icontains=v) | \
#                       Q(cognome__icontains=v) | \
#                       Q(nome__icontains=v) | \
#                       Q(partiva_codfisc__icontains=v)
#
#            objs = models.Cliente.objects.filter(search)[:15]
#            if objs:
#                res = [str(obj) for obj in objs]
#            
#    json = simplejson.dumps(res)
#    return HttpResponse(json, mimetype='application/json')   
