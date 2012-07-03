# -*- coding: utf-8 -*-

from django.http import HttpResponse          
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.servers.basehttp import FileWrapper

import pymobile.settings as settings
import pymobile.administration.models as models
import pymobile.administration.forms as forms
import pymobile.administration.tables as tables
import pymobile.administration.utils as u
import mimetypes
import os
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

# Create your views here.

TMP_ADMIN="contratto/admin.html"
TMP_FORM="contratto/modelform.html"
TMP_DEL="contratto/deleteform.html"
TMP_VIEW="contratto/view.html"

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def init(request):
    template = TMP_ADMIN
    objs = models.Contratto.objects.all()
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
    table = tables.ContrattoTable(objs, order_by=(ordering,))
    table.paginate(page=pag)                   

    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
    
    filterform = forms.ContrattoFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))

#@login_required
##@user_passes_test(lambda user: not u.is_telefonista(user),)
#@user_passes_test(lambda user: u.get_group(user) != "telefonista")
#def add_object(request):  
#    template = TMP_FORM
#    action = "add"
#    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
#                                                   models.PianoTariffario, 
#                                                   forms.PianoTariffarioForm,
#                                                   formset = forms.PianoTariffarioInlineFormset,
#                                                   can_delete=False,
#                                                   extra=1,)
#        
#    if request.method == "POST":
#        post_query = request.POST.copy()
#        form = forms.ContrattoForm(post_query, request.FILES)
#        
#        if form.is_valid():
#            contratto = form.save(commit=False)
#            formset = PianoTariffarioFormset(post_query, instance=contratto)
#            
#            if formset.is_valid():
#                new_obj = form.save()
#                formset.save()
#                
#                logger.debug("{}: aggiunto il contratto {} [id={}]"
#                             .format(request.user, new_obj, new_obj.id))
#                messages.add_message(request, messages.SUCCESS, 'Contratto aggiunto')
#                if request.POST.has_key("add_another"):              
#                    return HttpResponseRedirect(reverse("add_contratto_pt")) 
#                else:
#                    return HttpResponseRedirect(reverse("init_contratto"))
#        else:
#            formset = PianoTariffarioFormset(post_query)
#    else:
#        form = forms.ContrattoForm()
#        formset = PianoTariffarioFormset(instance=models.Contratto())                
#    
#    data = {"modelform": form, "action": action, "modelformset": formset,}                
#    return render_to_response(template, 
#                              data,ELITE DI PIROLA ELISAdi PIROLA EL
#                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_object_info(request):  
    template = "contratto/modelform_info.html"
    action = "add"
#    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
#                                                   models.PianoTariffario, 
#                                                   forms.PianoTariffarioForm,
#                                                   formset = forms.PianoTariffarioInlineFormset,
#                                                   can_delete=False,
#                                                   extra=1,)
        
    if request.method == "POST":
        form = forms.ContrattoForm(request.POST, request.FILES)
        
        if form.is_valid():
            request.session["contratto"] = {"post": {}, "files": {}}
            for k, v in request.POST.iteritems():
                request.session["contratto"]["post"][k] = v
            for k, v in request.FILES.iteritems():
                request.session["contratto"]["files"][k] = v
            
#            contratto = form.save(commit=False)
#            formset = PianoTariffarioFormset(post_query, instance=contratto)
#            
#            if formset.is_valid():
                
                
#                logger.debug("{}: aggiunto il contratto {} [id={}]"
#                             .format(request.user, new_obj, new_obj.id))
#                messages.add_message(request, messages.SUCCESS, 'Contratto aggiunto')
            return HttpResponseRedirect(reverse("add_contratto_pt"))
#        else:
#            formset = PianoTariffarioFormset(post_query)
    else:
        form = forms.ContrattoForm()
#        formset = PianoTariffarioFormset(instance=models.Contratto())                
    
    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_object_pt(request):  
    if not request.session["contratto"]:
        return HttpResponseRedirect(reverse("add_contratto_info"))
    
    template = "contratto/modelform_pianotariffario.html"
    action = "add"
    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
                                                   models.PianoTariffario, 
                                                   forms.PianoTariffarioForm,
                                                   formset = forms.PianoTariffarioInlineFormset,
                                                   can_delete=False,
                                                   extra=1,)
        
    if request.method == "POST":
        post_query = request.POST.copy()
        session = request.session
        
        form = forms.ContrattoForm(session["contratto"]["post"], 
                                   session["contratto"]["files"])
        contratto = form.save(commit=False)
        gestore = request.session["contratto"]["post"]["gestore"]
        pt_formset = PianoTariffarioFormset(post_query, 
                                            instance=contratto,
                                            gestore=gestore,)
        if pt_formset.is_valid():
            # memorizziamo i valori del POST che poi utlizzeremo per salvare i dati del
            # piano tariffario nel database; inoltre memorizziamo anche le informazioni
            # per le varie tariffe scelte.
            request.session["pianotariffario"] = {"post": {},"info": {}}
            for k, v in request.POST.iteritems():
                request.session["pianotariffario"]["post"][k] = v
            num_forms = int(request.POST["pianotariffario_set-TOTAL_FORMS"])
            for i in xrange(num_forms):
                tariffa = request.POST["pianotariffario_set-" + str(i) + "-tariffa"]
                if not tariffa:
                    break
                num = request.POST["pianotariffario_set-" + str(i) + "-num"]
                if request.POST.has_key("pianotariffario_set-" + str(i) + "-opzione"):
                    opzione = 1
                else:
                    opzione = 0
                request.session["pianotariffario"]["info"][i] = {"tariffa": models.Tariffa.objects.get(pk=tariffa),
                                                                 "num": num,
                                                                 "opzione": opzione,}
            
            return HttpResponseRedirect(reverse("add_contratto_dati"))    
    else:
        gestore = request.session["contratto"]["post"]["gestore"]
        pt_formset = PianoTariffarioFormset(instance=models.Contratto(), 
                                            gestore=gestore,)               
    data = {"action": action, "ptmodelformset": pt_formset,}# "datoptmodelformset": dati_formset}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_object_dati(request):  
    if not request.session["contratto"]:
        return HttpResponseRedirect(reverse("add_contratto_info"))
    if not request.session["pianotariffario"]:
        return HttpResponseRedirect(reverse("add_contratto_info"))
    
    template = "contratto/modelform_dati.html"
    action = "add"
    
    DatoPianoTariffarioFormset = inlineformset_factory(models.PianoTariffario, 
                                                       models.DatoPianoTariffario, 
                                                       forms.DatoPianoTariffarioForm,
                                                       can_delete=False,
                                                       extra=0,)

    dati_formsets = []
#    dati_formsets = [(request.session["pianotariffario"]["info"][k],
#                      DatoPianoTariffarioFormset(instance=models.PianoTariffario(), prefix=str(k),),)
#                     for k in request.session["pianotariffario"]["info"].iterkeys()]
    for k in request.session["pianotariffario"]["info"].iterkeys():
        formset = DatoPianoTariffarioFormset(instance=models.PianoTariffario(),
                                             prefix=str(k),)
        dati_formsets.append((request.session["pianotariffario"]["info"][k], formset))
    
#    print(request.session["pianotariffario"]["info"])
#    print(dati_formsets)
    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
                                                   models.PianoTariffario, 
                                                   forms.PianoTariffarioForm,
                                                   formset = forms.PianoTariffarioInlineFormset,
                                                   can_delete=False,
                                                   extra=1,)
        
    if request.method == "POST":
        post_query = request.POST.copy()
        session = request.session
        form = forms.ContrattoForm(session["contratto"]["post"], 
                                   session["contratto"]["files"])
        contratto = form.save(commit=False)
        gestore = request.session["contratto"]["post"]["gestore"]
        pt_formset = PianoTariffarioFormset(request.session["pianotariffario"]["post"], 
                                            instance=contratto,
                                            gestore=gestore,)
        
        if pt_formset.is_valid():
            pts = pt_formset.save(commit=False)
            i = 0
            valid = False
            formsets = []
            for pt in pts:
                formset = DatoPianoTariffarioFormset(post_query,
                                                     instance=pt,
                                                     prefix=str(i),)
                i += 1
                formsets.append(formset)
                if formset.is_valid():
                    valid = True
                else:
                    valid = False
            if valid:
                new_obj = form.save()
                pt_formset.save()
                for formset in formsets:
                    formset.save()
                logger.debug("{}: aggiunto il contratto {} [id={}]"
                             .format(request.user, new_obj, new_obj.id))
                messages.add_message(request, messages.SUCCESS, 'Contratto aggiunto')
                if request.POST.has_key("add_another"):              
                    return HttpResponseRedirect(reverse("add_contratto_info")) 
                else:
                    return HttpResponseRedirect(reverse("init_contratto"))
            else:
                # FIXME: sistemare il caso di errori
                messages.add_message(request, messages.ERROR, 'Errore nell\'inserimento dati')
#                dati_formsets = [(request.session["pianotariffario"]["info"][i], formsets) 
#                                 for i in xrange(len(formsets))]    
    
    data = {"action": action, 
            "pianotariffario": request.session["pianotariffario"]["info"],
            "dati_formsets": dati_formsets,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_object_info(request, object_id):  
    template = "contratto/modelform_info.html"
    action = "mod"
#    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
#                                                   models.PianoTariffario, 
#                                                   forms.PianoTariffarioForm,
#                                                   formset = forms.PianoTariffarioInlineFormset,
#                                                   can_delete=False,
#                                                   extra=1,)
        
    if request.method == "POST":
        obj = get_object_or_404(models.Contratto, pk=object_id)
        form = forms.ContrattoForm(request.POST, request.FILES, instance=obj)
        
        if form.is_valid():
#            request.session["contratto"] = {"post": {}, "files": {}}
#            for k, v in request.POST.iteritems():
#                request.session["contratto"]["post"][k] = v
#            for k, v in request.FILES.iteritems():
#                request.session["contratto"]["files"][k] = v
            
#            contratto = form.save(commit=False)
#            formset = PianoTariffarioFormset(post_query, instance=contratto)
#            
#            if formset.is_valid():
            form.save()    
                
            logger.debug("{}: modificate le informazioni del contratto {} [id={}]"
                         .format(request.user, obj, obj.id))
            messages.add_message(request, messages.SUCCESS, 'Informazioni contratto modifcate')
            return HttpResponseRedirect(reverse("view_contratto", 
                                                args=[object_id,]))
#            return HttpResponseRedirect(reverse("mod_contratto_pt", 
#                                                args=[object_id,]))
#        else:
#            formset = PianoTariffarioFormset(post_query)
    else:
        obj = get_object_or_404(models.Contratto, pk=object_id)
        form = forms.ContrattoForm(instance=obj)
#        formset = PianoTariffarioFormset(instance=models.Contratto())                
    
    data = {"modelform": form, "action": action, "contratto": obj}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_object_pt(request, object_id):  
#    if not request.session["contratto"]:
#        return HttpResponseRedirect(reverse("add_contratto_info"))
    
    template = "contratto/modelform_pianotariffario.html"
    action = "mod"
    
    obj = get_object_or_404(models.Contratto, pk=object_id)
    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
                                                   models.PianoTariffario, 
                                                   forms.PianoTariffarioForm,
                                                   formset = forms.PianoTariffarioInlineFormset,
                                                   can_delete=False,
                                                   extra=0,)
    if request.method == "POST":
        post_query = request.POST.copy()
        session = request.session
        
#        form = forms.ContrattoForm(post_query,
#                                   instance=obj)
#        contratto = form.save(commit=False)
        gestore = obj.gestore
#        gestore = request.session["contratto"]["post"]["gestore"]
        pt_formset = PianoTariffarioFormset(post_query, 
                                            instance=obj,
                                            gestore=gestore,)
        
        if pt_formset.is_valid():
#            contratto.save()
            pt_formset.save()
            # memorizziamo i valori del POST che poi utlizzeremo per salvare i dati del
            # piano tariffario nel database; inoltre memorizziamo anche le informazioni
            # per le varie tariffe scelte.
#            request.session["pianotariffario"] = {"post": {},"info": {}}
#            for k, v in request.POST.iteritems():
#                request.session["pianotariffario"]["post"][k] = v
#            num_forms = int(request.POST["pianotariffario_set-TOTAL_FORMS"])
#            for i in xrange(num_forms):
#                tariffa = request.POST["pianotariffario_set-" + str(i) + "-tariffa"]
#                if not tariffa:
#                    break
#                num = request.POST["pianotariffario_set-" + str(i) + "-num"]
#                if request.POST.has_key("pianotariffario_set-" + str(i) + "-opzione"):
#                    opzione = 1
#                else:
#                    opzione = 0
#                request.session["pianotariffario"]["info"][i] = {"tariffa": models.Tariffa.objects.get(pk=tariffa),
#                                                                 "num": num,
#                                                                 "opzione": opzione,}
            return HttpResponseRedirect(reverse("view_contratto", 
                                                args=[object_id,]))
#            return HttpResponseRedirect(reverse("mod_contratto_dati", 
#                                                args=[object_id,]))    
    else:
        gestore = obj.gestore
#        gestore = request.session["contratto"]["post"]["gestore"]
        pt_formset = PianoTariffarioFormset(instance=obj, 
                                            gestore=gestore,) 
    data = {"action": action, "ptmodelformset": pt_formset, "contratto": obj}
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_object_dati(request, object_id):  
#    if not request.session["contratto"]:
#        return HttpResponseRedirect(reverse("add_contratto_info"))
#    if not request.session["pianotariffario"]:
#        return HttpResponseRedirect(reverse("add_contratto_info"))
    
    template = "contratto/modelform_dati.html"
    action = "mod"
    
    obj = get_object_or_404(models.Contratto, pk=object_id)
    DatoPianoTariffarioFormset = inlineformset_factory(models.PianoTariffario, 
                                                       models.DatoPianoTariffario, 
                                                       forms.DatoPianoTariffarioForm,
                                                       can_delete=False,
                                                       extra=0,)

    dati_formsets = []
    #print(request.session["pianotariffario"])
    pts = models.PianoTariffario.objects.filter(contratto=obj)
    for pt in pts:
        formset = DatoPianoTariffarioFormset(instance=pt,)
        dati_formsets.append((pt, formset))
#        dati_formsets.append((request.session["pianotariffario"]["info"][k], formset))
#    for k in request.session["pianotariffario"]["info"].iterkeys():
#        formset = DatoPianoTariffarioFormset(instance=models.PianoTariffario(),
#                                             prefix=str(k),)
#        dati_formsets.append((request.session["pianotariffario"]["info"][k], formset))
    
#    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
#                                                   models.PianoTariffario, 
#                                                   forms.PianoTariffarioForm,
#                                                   formset = forms.PianoTariffarioInlineFormset,
#                                                   can_delete=False,
#                                                   extra=0,)
        
    if request.method == "POST":
        post_query = request.POST.copy()
#        session = request.session
#        form = forms.ContrattoForm(post_query)
#        contratto = form.save(commit=False)
#        gestore = obj.gestore
#        gestore = request.session["contratto"]["post"]["gestore"]
#        print(ciao)
#        pt_formset = PianoTariffarioFormset(post_query, 
#                                            instance=obj,)
#        
#        if pt_formset.is_valid():
#        pts = pt_formset.save(commit=False)
        pts = models.PianoTariffario.objects.filter(contratto=obj)
        i = 0
        valid = False
        formsets = []
        for pt in pts:
            formset = DatoPianoTariffarioFormset(post_query,
                                                 instance=pt,)
            i += 1
            formsets.append(formset)
            if formset.is_valid():
                valid = True
            else:
                valid = False
        if valid:
#                new_obj = form.save()
#                pt_formset.save()
            for formset in formsets:
                formset.save()
            logger.debug("{}: modificati i dati aggiuntivi del contratto {} [id={}]"
                         .format(request.user, obj, obj.id))
            messages.add_message(request, messages.SUCCESS, 'Contratto modificato')
            return HttpResponseRedirect(reverse("view_contratto", 
                                         args=[object_id,]))
#                if request.POST.has_key("add_another"):              
#                    return HttpResponseRedirect(reverse("add_contratto_info")) 
#                else:
#                    return HttpResponseRedirect(reverse("init_contratto"))
        else:
            # FIXME: sistemare il caso di errori
            messages.add_message(request, messages.ERROR, 'Errore nell\'inserimento dati')
#                pass
    
    print(dati_formsets)        
    data = {"action": action, 
#            "pianotariffario": request.session["pianotariffario"]["info"],
            "dati_formsets": dati_formsets,
            "contratto": obj}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

#@login_required
##@user_passes_test(lambda user: not u.is_telefonista(user),)
#@user_passes_test(lambda user: u.get_group(user) != "telefonista")
#def mod_object(request, object_id):
#    template = TMP_FORM
#    action = "mod"
#    PianoTariffarioFormset = inlineformset_factory(models.Contratto, 
#                                                   models.PianoTariffario, 
#                                                   forms.PianoTariffarioForm,
#                                                   formset = forms.PianoTariffarioInlineFormset,
#                                                   can_delete=True,
#                                                   extra=0,)
#    
#    if request.method == "POST":
#        post_query = request.POST.copy()
#                
#        obj = get_object_or_404(models.Contratto, pk=object_id)
#        form = forms.ContrattoForm(post_query, request.FILES, instance=obj)
#        
#        if form.is_valid():
#            contratto = form.save(commit=False)
#            formset = PianoTariffarioFormset(post_query, instance=contratto)
#            
#            if formset.is_valid():
#                new_obj = form.save()
#                formset.save() 
#                
#                logger.debug("{}: modificato il contratto {} [id={}]"
#                             .format(request.user, new_obj, new_obj.id))
#                messages.add_message(request, messages.SUCCESS, 'Contratto modificato')
#                if request.POST.has_key("add_another"):              
#                    return HttpResponseRedirect(reverse("add_contratto")) 
#                else:
#                    return HttpResponseRedirect(reverse("view_contratto", 
#                                                        args=[object_id,]))
#        else:
#            formset = PianoTariffarioFormset(post_query, instance=obj)
#    else:
#        obj = get_object_or_404(models.Contratto, pk=object_id)
#        form = forms.ContrattoForm(instance=obj)
#        formset = PianoTariffarioFormset(instance=obj)        
#    
#    data = {"modelform": form, "action": action, "modelformset": formset, "contratto": obj} 
#    return render_to_response(template,
#                              data,
#                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def del_object(request):
    template = TMP_DEL
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.Contratto.objects.filter(id__in=ids).delete()
            
            if len(ids) == 1:
                logger.debug("{}: eliminato il contratto [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Contratto eliminato')
            elif len(ids) > 1:
                logger.debug("{}: eliminato i contratti [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Contratti eliminati')
            url = reverse("init_contratto")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Contratto.objects.filter(id__in=ids)
    
    logger.debug("{}: ha intenzione di eliminare i contratti {}"
                 .format(request.user, [(str(obj), "id=" + str(obj.id)) for obj in objs]))
    
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_child_object(request, field_name):
    action = "Aggiungi" 
    
    def get_child_form(field_name):  
        f = field_name.capitalize() + "Form"
        if field_name == "cliente":
            t = "contratto/cliente_modelform.html"
        elif field_name == "agente":
            t = "contratto/agente_modelform.html"
        elif field_name == "tariffa":
            t = "contratto/tariffa_modelform.html"        
        return getattr(forms, f), t  
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form_class, template = get_child_form(field_name)
        form = form_class(post_query)
        
        if form.is_valid():
            try:
                new_obj = form.save()
                if field_name == "agente":
                    logger.debug("{}: aggiunto l'agente {} [id={}][chiave esterna di contratto]"
                                 .format(request.user, new_obj, new_obj.id))
                elif field_name == "cliente":
                    logger.debug("{}: aggiunto il cliente {} [id={}][chiave esterna di contratto]"
                                 .format(request.user, field_name, new_obj, new_obj.id))
                elif field_name == "tariffa":
                    logger.debug("{}: aggiunto la tariffa {} [id={}][chiave esterna di contratto]"
                                 .format(request.user, field_name, new_obj, new_obj.id))
            except form.ValidationError:
                new_obj = None
                                
            if new_obj: 
                return HttpResponse('''
                    <script type="text/javascript">
                        opener.closeSubModelform(window, "{}", "{}");
                    </script>'''.format(new_obj.pk, new_obj))
    else:
        form_class, template = get_child_form(field_name)
        if field_name == "tariffa":
            gestore = request.session["contratto"]["post"]["gestore"]
            form = form_class(gestore=gestore)
        else:
            form = form_class()
      
    data = {"modelform": form, "action": action,}     
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def send_file(request, object_id):
    # informazioni file
    pdffile = models.Contratto.objects.get(pk=object_id).pdf_contratto
    pdffile_path = settings.MEDIA_ROOT + pdffile.name
    basename = os.path.basename(pdffile_path)
    size = pdffile.size
    m = mimetypes.guess_type(pdffile_path)
    mimetype = m[0]
    encoding = m[1]
    
    # filewrapper è un funzione che divide il file in chunck così da non caricare
    # tutto in memoria
    wrapper = FileWrapper(file(pdffile_path))
    response = HttpResponse(wrapper,)
    response['Content-Type'] = mimetype
    response['Content-Length'] = size
    response['Content-Encoding'] = encoding
    response['Content-Disposition'] = 'attachment; filename=' + basename
    
    return response
