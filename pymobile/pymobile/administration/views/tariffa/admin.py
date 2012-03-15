# -*- coding: utf-8 -*-

from django.http import HttpResponse          
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.contrib import messages

import pymobile.administration.models as models
import pymobile.administration.forms as forms
import pymobile.administration.tables as tables
import pymobile.administration.utils as u

# Create your views here.

TMP_ADMIN="tariffa/admin.html"
TMP_FORM="tariffa/modelform.html"
TMP_DEL="tariffa/deleteform.html"
TMP_VIEW="tariffa/view.html"

def init(request):
    template = TMP_ADMIN
    objs = models.Tariffa.objects.all()
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
        
    table = tables.TariffaTable(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = forms.TariffaFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))

def add_object(request):  
    template = TMP_FORM
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.TariffaForm(post_query)
        
        if form.is_valid():
            form.save()
            
            messages.add_message(request, messages.SUCCESS, 'Tariffa aggiunta')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_tariffa")) 
            else:
                return HttpResponseRedirect(reverse("init_tariffa"))
    else:
        form = forms.TariffaForm()    

    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

def mod_object(request, object_id):
    template = TMP_FORM
    action = "mod"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(models.Tariffa, pk=object_id)
        form = forms.TariffaForm(post_query, instance=obj)
    
        if form.is_valid():
            form.save()
            
            messages.add_message(request, messages.SUCCESS, 'Tariffa modificata')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_tariffa")) 
            else:
                return HttpResponseRedirect(reverse("view_tariffa", 
                                                    args=[object_id]))
    else:
        obj = get_object_or_404(models.Tariffa, pk=object_id) 
        form = forms.TariffaForm(instance=obj)
    
    data = {"modelform": form, "action": action, "tariffa": obj,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def del_object(request):
    template = TMP_DEL
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.Tariffa.objects.filter(id__in=ids).delete()
            url = reverse("init_tariffa")
            
            if len(ids) == 1:
                messages.add_message(request, messages.SUCCESS, 'Tariffa eliminata')
            elif len(ids) > 1:
                messages.add_message(request, messages.SUCCESS, 'Tariffe eliminate')
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Tariffa.objects.filter(id__in=ids)
    
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))


def add_child_object(request, field_name):
    action = "Aggiungi" 
    
    def get_child_form(field_name):    
        
        if field_name.startswith("tipo_"):
            g = field_name[5:].capitalize()
            f = "TipologiaTariffaForm"
            t = "tariffa/tipologia_modelform.html"
        elif field_name.startswith("fascia_"):
            g = field_name[7:].capitalize() 
            f = "FasciaTariffaForm"
            t = "tariffa/fascia_modelform.html"
        elif field_name.startswith("servizio_"):
            g = field_name[9:].capitalize() 
            f = "ServizioTariffaForm"
            t = "tariffa/servizio_modelform.html"
        
        return getattr(forms, f), g, t
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form_class, gestore, template = get_child_form(field_name)
        form = form_class(post_query)
        
        if form.is_valid():
            try:
                new_obj = form.save()
            except form.ValidationError:
                new_obj = None
                                
            if new_obj: 
                return HttpResponse('''
                    <script type="text/javascript">
                        opener.closeSubModelform(window, "{}", "{}");
                    </script>'''.format(new_obj.pk, new_obj))
    else:
        form_class, gestore, template = get_child_form(field_name)
        form = form_class(post_query)
      
    data = {"modelform": form, "action": action, "gestore": gestore,}     
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

def init_attribute(request, attribute):
    template = "tariffa/attribute_admin.html"
    model = get_model("administration", attribute + "tariffa")
    objs = model.objects.all()
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
        
    table = u.get_table(attribute + "tariffatable")(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = u.get_form(attribute + "tariffafilterform")(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform, "attributo": attribute,}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))

def add_attribute(request, attribute):  
    template = "tariffa/attribute_modelform.html"
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = u.get_form(attribute + "tariffaform")(post_query)
        
        if form.is_valid():
            form.save()
            
            if attribute == "servizio":
                messages.add_message(request, messages.SUCCESS, '{} aggiunto'.format(attribute.title()))
            else:
                messages.add_message(request, messages.SUCCESS, '{} aggiunta'.format(attribute.title()))
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_tariffa")) 
            else:
                return HttpResponseRedirect(reverse("init_attribute", 
                                                    args=[attribute]))
    else:
        form = u.get_form(attribute + "tariffaform")()

    data = {"modelform": form, "action": action, "attributo": attribute,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

def mod_attribute(request, attribute, object_id):
    template = "tariffa/attribute_modelform.html"
    action = "mod"
    model = get_model("administration", attribute + "tariffa")
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(model, pk=object_id)
        form = u.get_form(attribute + "tariffaform")(post_query, instance=obj)
    
        if form.is_valid():
            form.save()

            if attribute == "servizio":
                messages.add_message(request, messages.SUCCESS, '{} modificato'.format(attribute.title()))
            else:
                messages.add_message(request, messages.SUCCESS, '{} modificata'.format(attribute.title()))            
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_tariffa")) 
            else:
                return HttpResponseRedirect(reverse("init_attribute", 
                                                    args=[attribute]))
    else:
        obj = get_object_or_404(model, pk=object_id)         
        form = u.get_form(attribute + "tariffaform")(instance=obj)
    
    data = {"modelform": form, "action": action, "attributo": attribute,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def del_attribute(request, attribute):
    template = "tariffa/attribute_deleteform.html"
    model = get_model("administration", attribute + "tariffa")
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            model.objects.filter(id__in=ids).delete()
            
            if attribute == "servizio" :
                if len(ids) == 1:
                    messages.add_message(request, messages.SUCCESS, 'Servizio eliminato')
                elif len(ids) > 1:
                    messages.add_message(request, messages.SUCCESS, 'Servizi eliminati')
            else:
                if len(ids) == 1:
                    messages.add_message(request, messages.SUCCESS, '{} eliminata'.format((attribute[:-1] + "e").title()))
                elif len(ids) > 1:
                    messages.add_message(request, messages.SUCCESS, '{} eliminate'.format((attribute[:-1] + "e").title()))
            url = reverse("init_attribute", args=[attribute,])
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = model.objects.filter(id__in=ids)
    
    data = {"objs": objs, "attributo": attribute}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))
    