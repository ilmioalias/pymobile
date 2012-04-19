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
from pymobile.administration.views.opzione.admin import get_default_options
from datetime import datetime, timedelta
from copy import deepcopy
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

# Create your views here.

TMP_ADMIN="dipendente/admin.html"
TMP_FORM="dipendente/modelform.html"
TMP_DEL="dipendente/deleteform.html"
TMP_VIEW="dipendente/view.html"
TMP_PROV="dipendente/provvigione_admin.html"
TMP_PROV_CONTRATTO_FORM="dipendente/provvigione_modelform.html"
TMP_PROV_BONUS_FORM="dipendente/provvigione_modelform.html"
TMP_PROV_CONTRATTO_DELFORM="dipendente/provvigione_deleteform.html"
TMP_PROV_BONUS_DELFORM="dipendente/provvigione_deleteform.html"
TMP_PROV_TABLE="dipendente/provvigione_table_snippet.html"
TMP_PROV_VARTMP_CONF="dipendente/provvigione_variazione_conferma.html"
TMP_PROV_RETR_CONF="dipendente/provvigione_retribuzione_conferma.html"

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def init(request):
    template = TMP_ADMIN
    objs = models.Dipendente.objects.all()
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
        
    table = tables.DipendenteTable(objs, order_by=(ordering,))
    table.paginate(page=pag)
    
    if request.is_ajax():
        template = table.as_html()
        return HttpResponse(template)
        
    filterform = forms.DipendenteFilterForm(initial=initial)
    
    data = {"modeltable": table, "filterform": filterform}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_object(request):  
    template = TMP_FORM
    action = "add"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.DipendenteForm(post_query)
        
        if form.is_valid():
            dipendente = form.save(commit=False)
            formset = forms.RetribuzioneFormset(post_query, instance=dipendente)
            if formset.is_valid():
                new_obj = form.save()
                formset.save()        
                
                logger.debug("{}: aggiunto il dipendente {} [id={}]"
                             .format(request.user, new_obj, new_obj.id))
                messages.add_message(request, messages.SUCCESS, 'Dipendente aggiunto')
                if request.POST.has_key("add_another"):              
                    return HttpResponseRedirect(reverse("add_dipendente")) 
                else:
                    return HttpResponseRedirect(reverse("init_dipendente"))
        else:
            formset = forms.RetribuzioneFormset(post_query)
    else:
        form = forms.DipendenteForm()    
        formset = forms.RetribuzioneFormset(instance=models.Dipendente())
        # sistemiano i valori iniziali
        data = {"principale": True}
        for subform in formset.forms:
            subform.initial = data
    
    default_opts = get_default_options()
    provvigione_bonus_agente = default_opts["provvigione_bonus_agente"]
    provvigione_bonus_telefonista = default_opts["provvigione_bonus_telefonista"]
        
    data = {"modelform": form, 
            "modelformset": formset, 
            "action": action,
            "provvigione_bonus_agente": provvigione_bonus_agente,
            "provvigione_bonus_telefonista": provvigione_bonus_telefonista}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_object(request, object_id):
    template = TMP_FORM
    action = "mod"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(models.Dipendente, pk=object_id)
        form = forms.DipendenteForm(post_query, instance=obj)
    
        if form.is_valid():
            new_obj = form.save()
            
            logger.debug("{}: modificato il dipendente {} [id={}]"
                         .format(request.user, new_obj, new_obj.id))
            messages.add_message(request, messages.SUCCESS, 'Dipendente modificato')
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_dipendente")) 
            else:
                return HttpResponseRedirect(reverse("view_dipendente", 
                                                    args=[object_id]))
    else:
        obj = get_object_or_404(models.Dipendente, pk=object_id) 
        form = forms.DipendenteForm(instance=obj)
    
    data = {"modelform": form, "action": action, "dipendente": obj}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

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
            models.Dipendente.objects.filter(id__in=ids).delete()
            
            if len(ids) == 1:
                logger.debug("{}: eliminato il dipendente [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Dipendente eliminato')
            elif len(ids) > 1:
                logger.debug("{}: eliminati i dipendenti [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Dipendenti eliminati')
            url = reverse("init_dipendente")
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Dipendente.objects.filter(id__in=ids)
    
    logger.debug("{}: ha intenzione di eliminare i dipendenti {}"
                 .format(request.user, [(str(obj), "id=" + str(obj.id)) for obj in objs]))      
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def init_provvigione(request, object_id):
    # FIXME: data licenziamento non è presa in considerazione
    # da correggere, non ora però
    template = TMP_PROV
    
    dipendente = get_object_or_404(models.Dipendente, pk=object_id)
    
    period = u.get_current_quarter()
    
    data_inizio = request.GET.get("fdata_inizio", "")
    data_fine = request.GET.get("fdata_fine", "")
    
    retribuzioni = models.RetribuzioneDipendente.objects.filter(
                            dipendente=object_id, variazione=False,).order_by("-data_inizio")
    earliest_retribuzione = retribuzioni[retribuzioni.count()-1] if retribuzioni.exists() else None
    
    variazioni = models.RetribuzioneDipendente.objects.filter(
                            dipendente=object_id, variazione=True,).order_by("-data_inizio")                                                     
    
    data_min = datetime.strptime(data_inizio, "%d/%m/%Y").date() if data_inizio else period[0]
    data_min = data_min if data_min >= earliest_retribuzione.data_inizio else earliest_retribuzione.data_inizio
    data_max = datetime.strptime(data_fine, "%d/%m/%Y").date() if data_fine else period[1]
    retribuzioni = retribuzioni.filter(data_fine__gte=data_min, 
                                       data_inizio__lte=data_max)
    variazioni = variazioni.filter(data_fine__gte=data_min,
                                   data_inizio__lte=data_max)
    
    days = (data_max - data_min).days
    
    # creaiamo un dizionario con tutte le variazioni e le retribuzioni
    objs = {}
    # variazioni
    if variazioni.exists():          
        for index, var_cur in enumerate(variazioni):
            obj = {"anno": None,
                   "mese": None,
                   "retribuzione": None,
                   "variazione": None,
                   "rowspan_r": None,
                   "rowspan_v": None,} 
            obj["variazione"] = var_cur       
            if data_max < var_cur.data_fine:
                row = 0
                obj["rowspan_v"] = (data_max - var_cur.data_inizio).days + 1
            else:           
                row = (data_max - var_cur.data_fine).days
                obj["rowspan_v"] = (var_cur.data_fine - var_cur.data_inizio).days + 1
            objs[row] = obj
    # retribuzioni
    if retribuzioni.exists():
        for index, ret_cur in enumerate(retribuzioni):
            obj = {"anno": None,
                   "mese": None,
                   "retribuzione": None,
                   "variazione": None,
                   "rowspan_r": None,
                   "rowspan_v": None,} 
            obj["retribuzione"] = ret_cur       
            row = (data_max - ret_cur.data_fine).days
            obj["rowspan_r"] = (ret_cur.data_fine - ret_cur.data_inizio).days + 1
            if row in objs:
                objs[row]["retribuzione"] = obj["retribuzione"]
                objs[row]["rowspan_r"] = obj["rowspan_r"]
            else:
                objs[row] = obj
    
    # creiamo la lista di righe di dati da inserire nella tabella.
    rows = []
    data_cur = data_max
    y_cur = data_cur.year
    m_cur = data_cur.month
    for i in xrange(days + 1):
        data_cur -= timedelta(1)
        if y_cur != data_cur.year:
            year = data_cur.year
            y_cur = year
            month = (m_cur, )
        else:
            year = None
        if m_cur != data_cur.month:
            month = (m_cur, )
            year = data_cur.year
            m_cur = data_cur.month
        else:
            month = None
        if i in objs:
            objs[i]["anno"] = year
            objs[i]["mese"] = month
            rows.append(objs[i])
            del objs[i]
        else:
            rows.append({"anno": year,
                         "mese": month,
                         "retribuzione": None,
                         "variazione": None,
                         "rowspan_r": None,
                         "rowspan_v": None,})   
    # aggiungiamo la data iniziale e finale
    rows[0]["anno"] = data_max.year
    rows[0]["mese"] = (data_max.month, data_max)
    rows[len(rows)-1]["anno"] = data_min.year
    rows[len(rows)-1]["mese"] = (data_min.month, data_min)
    
    if request.is_ajax():
        template = TMP_PROV_TABLE
        data = {"rows": rows, "days": range(days), "period": (data_min, data_max)}
        return render_to_response(template,
                                  data,
                                  context_instance=RequestContext(request))        
    
    data = {"dipendente": dipendente, "rows": rows, "period": (data_min, data_max)}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_retribuzione(request, object_id):
    template = TMP_PROV_CONTRATTO_FORM
    action = "add"
    
    dipendente_id = object_id 
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)
    
    # data_inizio indica la data di prima retribuzione/assunzione, cioè prima della quale
    # non possono essere assegnate variazioni di retribuzione/variazioni temporanee
    data_inizio = dipendente.data_assunzione.strftime("%d/%m/%Y")
    # data_fine, se esiste, è la data di licenziamento del dipendente, cioè la data
    # oltre la quale non è possibile assegnare variazioni di retribuzuione/variazioni temporanee
    if dipendente.data_licenziamento:
        data_fine = dipendente.data_licenziamento.strftime("%d/%m/%Y")
    else:
        data_fine = ""
            
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.RetribuzioneForm(post_query)
        
        if form.is_valid():
            new_obj = form.save()
            
            logger.debug("{}: aggiunto la retribuzione {} [id={}] per il dipendente {}"
                         .format(request.user, new_obj, new_obj.id, dipendente))
            messages.add_message(request, messages.SUCCESS, 'Retribuzione aggiunta')
            return HttpResponseRedirect(reverse("init_provvigione", args=[dipendente_id]))
    else:
        # recuperiamo le provvigioni iniziali, corrispondono a quelle della retribuzione precedente
        last_retribuzione = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                             variazione=False,).order_by("-data_inizio")[0]     
        form = forms.RetribuzioneForm(initial={"dipendente": dipendente_id,
                                               "fisso": last_retribuzione.fisso, 
                                               "provvigione_contratto": last_retribuzione.provvigione_contratto,
                                               "provvigione_bonus": last_retribuzione.provvigione_bonus,},)

    data = {"tipo":"ret",
            "modelform": form, 
            "action": action, 
            "dipendente": dipendente,
            "data_inizio": data_inizio,
            "data_fine": data_fine}              
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))    

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def add_vartmp(request, object_id):
    template = TMP_PROV_BONUS_FORM
    action = "add"
    
    dipendente_id = object_id 
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)

    # data_inizio indica la data di prima retribuzione/assunzione, cioè prima della quale
    # non possono essere assegnate variazioni di retribuzione/variazioni temporanee
    data_inizio = dipendente.data_assunzione.strftime("%d/%m/%Y")
    # data_fine, se esiste, è la data di licenziamento del dipendente, cioè la data
    # oltre la quale non è possibile assegnare variazioni di retribuzuione/variazioni temporanee
    if dipendente.data_licenziamento:
        data_fine = dipendente.data_licenziamento.strftime("%d/%m/%Y")
    else:
        data_fine = ""
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.VariazioneRetribuzioneForm(post_query)

        if form.is_valid():
            #FIXME: usiamo una transaction?
            # controlliamo se vengono modifcate o cancellate altre variazioni temporanee
            # 1 - quelle da modifcare
            d_i = datetime.strptime(post_query["data_inizio"], "%d/%m/%Y").date()
            d_f = datetime.strptime(post_query["data_fine"], "%d/%m/%Y").date()
            # troviamo le variazioni che contengo le date scelte nel form
            variazioni = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                  variazione=True)
            vartmp_mod_i = variazioni.filter(data_inizio__lte=d_i, data_fine__gte=d_i)
            vartmp_mod_f = variazioni.filter(data_inizio__lte=d_f, data_fine__gte=d_f)
            # quelle da cancellare
            vartmp_del = variazioni.filter(data_inizio__gte=d_i,
                                           data_fine__lte=d_f,)
            # FIXME: aggiungere un avviso se altre var. tmp. vengono modficate
#            if not post_query.get("verified", False) and (vartmp_del.exists() or vartmp_mod_i.exists() or vartmp_mod_f.exists()):
#                if vartmp_mod_i.exists() and vartmp_mod_f.exists() and vartmp_mod_f[0] == vartmp_mod_i[0]:
#                    vartmp_mod_f = None
#                data = {"action": action,
#                        "dipendente": dipendente, 
#                        "vartmp_mod_i": vartmp_mod_i,
#                        "vartmp_mod_f": vartmp_mod_f, 
#                        "vartmp_del": vartmp_del,
#                        "variazione": post_query["variazione"],
#                        "principale": post_query["principale"],
#                        "data_inizio": post_query["data_inizio"],
#                        "data_fine": post_query["data_fine"],
#                        "provvigione_contratto": post_query["provvigione_contratto"],
#                        "provvigione_bonus": post_query["provvigione_bonus"],}
#                html = render_to_string(TMP_PROV_VARTMP_CONF,
#                                        data,)
#                url = reverse("confirm_vartmp")
#                return HttpResponse('''
#                    <script type='text/javascript'>
#                        var name = 'confirm';
#                        var win = window.open('{}', name, 'height=600,width=800,resizable=yes,scrollbars=yes');
#                        win.focus();
#                    </script>'''.format(url))
#                return render_to_response(TMP_PROV_VARTMP_CONF,
#                                          data,
#                                          context_instance=RequestContext(request))             
#            else:
            vartmp_new = form.save(commit=False)
            mod_del = False
            # eseguiamo le modifiche al databse
            # eliminiamo 
            if vartmp_del.exists():
                mod_del = True
                vartmp_del.delete()
            # modifichiamo
            if vartmp_mod_i.exists() and vartmp_mod_f.exists():
                mod_del = True
                if vartmp_mod_i[0] == vartmp_mod_f[0]:
                    # questo è il caso in cui la nuova variazione abbia il periodo completamente 
                    # compreso in un'altra variazione: dobbiamo creare due nuove variazione
                    # più la nuova variazione
                    # 1 - creiamo una nuova istanza 
                    new = deepcopy(vartmp_mod_f[0])
                    new.pk = None
                    new.data_inizio = vartmp_new.data_fine + timedelta(1)
                    new.save()
                else:
                    t = vartmp_new.data_fine + timedelta(1)
                    vartmp_mod_f.update(data_inizio=t)
                t = vartmp_new.data_inizio - timedelta(1)
                vartmp_mod_i.update(data_fine=t)                    
            elif vartmp_mod_i.exists() and not vartmp_mod_f.exists():
                mod_del = True
                t = vartmp_new.data_inizio - timedelta(1)
                vartmp_mod_i.update(data_fine=t)
            elif not vartmp_mod_i.exists() and vartmp_mod_f.exists():
                mod_del = True
                t = vartmp_new.data_fine + timedelta(1)
                vartmp_mod_f.update(data_inizio=t)
            vartmp_new.save()
                
            logger.debug("{}: aggiunto la variazione temporanea alla retribuzione {} [id={}] per il dipendente {}"
                     .format(request.user, vartmp_new, vartmp_new.id, dipendente))
            if mod_del:
                messages.add_message(request, messages.SUCCESS, 'Variazione temporanea aggiunta '\
                                     '(Sono state apportate delle modfiche)')
            else:
                messages.add_message(request, messages.SUCCESS, 'Variazione temporanea aggiunta')
            return HttpResponseRedirect(reverse("init_provvigione", args=[dipendente_id])) 

    else:   
        # recuperiamo le provvigioni iniziali, corrispondono a quelle della retribuzione precedente
        last_retribuzione = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                             variazione=False,).order_by("-data_inizio")[0]    
        form = forms.VariazioneRetribuzioneForm(initial={"dipendente": dipendente_id,
                                                         "variazione": True,
                                                         "provvigione_contratto": last_retribuzione.provvigione_contratto,
                                                         "provvigione_bonus": last_retribuzione.provvigione_bonus,},)

    data = {"tipo":"tmp",
            "modelform": form, 
            "action": action, 
            "dipendente": dipendente,
            "data_inizio": data_inizio,
            "data_fine": data_fine}              
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_retribuzione(request, object_id, provvigione_id):
    template = TMP_PROV_CONTRATTO_FORM
    action = "mod"
    
    dipendente_id = object_id
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)
    obj = get_object_or_404(models.RetribuzioneDipendente, pk=provvigione_id)
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.RetribuzioneForm(post_query, instance=obj)
    
        if form.is_valid():
            # se modifichiamo la retribuzione principale (cioè quella dell'assunzione)
            # dobbiamo verificare se devono essere mdoficate altre retribuzioni/variazioni
            if models.RetribuzioneDipendente.objects.get(pk=provvigione_id).principale:
                #FIXME: usiamo una transaction?
                # controlliamo se vengono modifcate o cancellate altre variazioni temporanee
                # 1 - quelle da modifcare
                d_i = datetime.strptime(post_query["data_inizio"], "%d/%m/%Y").date()
                # troviamo le variazioni che contengo le date scelte nel form
                variazioni = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                          variazione=True)
                retribuzioni = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                            variazione=False,)
                vartmp_mod = variazioni.filter(data_inizio__lte=d_i, data_fine__gte=d_i)
                # quelle da cancellare
                vartmp_del = variazioni.filter(data_fine__lte=d_i,)
                retr_del = retribuzioni.filter(data_inizio__lte=d_i).exclude(pk=provvigione_id)
                
#                if not post_query.get("verified", False) and (vartmp_del.exists() or vartmp_mod.exists() or retr_del.exists()):
#                    data = {"dipendente": dipendente,
#                            "retribuzione": obj,  
#                            "vartmp_mod": vartmp_mod,
#                            "retr_del": retr_del, 
#                            "vartmp_del": vartmp_del,
#                            "principale": post_query["principale"],
#                            "data_inizio": post_query["data_inizio"],
#                            "fisso": post_query["fisso"],
#                            "provvigione_contratto": post_query["provvigione_contratto"],
#                            "provvigione_bonus": post_query["provvigione_bonus"],}
#                    return render_to_response(TMP_PROV_RETR_CONF,
#                                              data,
#                                              context_instance=RequestContext(request)) 
#                else:
                retr_new = form.save(commit=False)
                mod_del = False
                # eseguiamo le modifiche al databse
                # eliminiamo 
                if vartmp_del.exists():
                    mod_del = True
                    vartmp_del.delete()
                if retr_del.exists():
                    mod_del = True
                    retr_del.delete()
                # modifichiamo
                if vartmp_mod.exists():
                    mod_del = True
                    vartmp_mod.update(data_inizio=retr_new.data_inizio)
                retr_new.save()
                
                logger.debug("{}: modficata la retribuzione {} [id={}] per il dipendente {}"
                             .format(request.user, retr_new, retr_new.id, dipendente))
                if mod_del:
                    messages.add_message(request, messages.SUCCESS, 'Retribuzione modificata '\
                                         '(Sono state apportate alcune modifiche)')
                else:
                    messages.add_message(request, messages.SUCCESS, 'Retribuzione modificata')
                return HttpResponseRedirect(reverse("init_provvigione", args=[dipendente_id]))                                     
            else:
                retr_new = form.save()
                
                logger.debug("{}: modficata la retribuzione {} [id={}] per il dipendente {}"
                             .format(request.user, retr_new, retr_new.id, dipendente)) 
                messages.add_message(request, messages.SUCCESS, 'Retribuzione modificata')
                return HttpResponseRedirect(reverse("init_provvigione", args=[dipendente_id]))                                
    else:
        form = forms.RetribuzioneForm(instance=obj)  
        
    if obj.principale:
        data_inizio = ""
    else:
        data_inizio = models.RetribuzioneDipendente.objects.get(dipendente=dipendente, 
                                                                principale=True).data_inizio.strftime("%d/%m/%Y")
    
    data = {"tipo": "ret",
            "modelform": form, 
            "action": action, 
            "dipendente": dipendente,
            "data_inizio": data_inizio,} 
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def mod_vartmp(request, object_id, provvigione_id):
    template = TMP_PROV_BONUS_FORM
    action = "mod"
    
    dipendente_id = object_id
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)
    obj = get_object_or_404(models.RetribuzioneDipendente, pk=provvigione_id)   
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.VariazioneRetribuzioneForm(post_query, instance=obj)
    
        if form.is_valid():
            #FIXME: usiamo una transaction?
            # controlliamo se vengono modifcate o cancellate altre variazioni temporanee
            # 1 - quelle da modifcare
            d_i = datetime.strptime(post_query["data_inizio"], "%d/%m/%Y").date()
            d_f = datetime.strptime(post_query["data_fine"], "%d/%m/%Y").date()
            # troviamo le variazioni che contengo le date scelte nel form
            variazioni = models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                      variazione=True).exclude(pk=provvigione_id)
            vartmp_mod_i = variazioni.filter(data_inizio__lte=d_i, data_fine__gte=d_i)
            vartmp_mod_f = variazioni.filter(data_inizio__lte=d_f, data_fine__gte=d_f)
            # quelle da cancellare
            vartmp_del = variazioni.filter(data_inizio__gte=d_i,data_fine__lte=d_f,)
            
#            if not post_query.get("verified", False) and (vartmp_del.exists() or vartmp_mod_i.exists() or vartmp_mod_f.exists()):
#                if vartmp_mod_i.exists() and vartmp_mod_f.exists() and vartmp_mod_f[0] == vartmp_mod_i[0]:
#                    vartmp_mod_f = None
#                data = {"dipendente": dipendente, 
#                        "vartmp_mod_i": vartmp_mod_i,
#                        "vartmp_mod_f": vartmp_mod_f, 
#                        "vartmp_del": vartmp_del,
#                        "variazione": post_query["variazione"],
#                        "principale": post_query["principale"],
#                        "data_inizio": post_query["data_inizio"],
#                        "data_fine": post_query["data_fine"],
#                        "provvigione_contratto": post_query["provvigione_contratto"],
#                        "provvigione_bonus": post_query["provvigione_bonus"],}
#                return render_to_response(TMP_PROV_VARTMP_CONF,
#                                          data,
#                                          context_instance=RequestContext(request)) 
#            else:
            vartmp_new = form.save(commit=False)
            mod_del = False
            # eseguiamo le modifiche al databse
            # eliminiamo 
            if vartmp_del.exists():
                mod_del = True
                vartmp_del.delete()
            # modifichiamo
            if vartmp_mod_i.exists() and vartmp_mod_f.exists():
                mod_del = True
                if vartmp_mod_i[0] == vartmp_mod_f[0]:
                    # questo è il caso in cui la nuova variazione abbia il periodo completamente 
                    # compreso in un'altra variazione: dobbiamo creare due nuove variazione
                    # più la nuova variazione
                    # 1 - creiamo una nuova istanza 
                    new = deepcopy(vartmp_mod_f[0])
                    new.pk = None
                    new.data_inizio = vartmp_new.data_fine + timedelta(1)
                    new.save()
                else:
                    t = vartmp_new.data_fine + timedelta(1)
                    vartmp_mod_f.update(data_inizio=t)
                t = vartmp_new.data_inizio - timedelta(1)
                vartmp_mod_i.update(data_fine=t)                    
            elif vartmp_mod_i.exists() and not vartmp_mod_f.exists():
                mod_del = True
                t = vartmp_new.data_inizio - timedelta(1)
                vartmp_mod_i.update(data_fine=t)
            elif not vartmp_mod_i.exists() and vartmp_mod_f.exists():
                mod_del = True
                t = vartmp_new.data_fine + timedelta(1)
                vartmp_mod_f.update(data_inizio=t)
            vartmp_new.save()
            
            logger.debug("{}: modficata la variazione temporanea della retribuzione {} [id={}] per il dipendente {}"
                         .format(request.user, vartmp_new, vartmp_new.id, dipendente))
            if mod_del:
                messages.add_message(request, messages.SUCCESS, 'Variazione temporanea modificata '\
                                     '(Sono state apportate delle modfiche)')
            else:
                messages.add_message(request, messages.SUCCESS, 'Variazione temporanea modificata')
            return HttpResponseRedirect(reverse("init_provvigione", args=[dipendente_id]))                      
    else: 
        form = forms.VariazioneRetribuzioneForm(instance=obj)

    data_inizio = models.RetribuzioneDipendente.objects.get(dipendente=dipendente, 
                                                            principale=True).data_inizio 
                                                                
    data = {"tipo": "tmp",
            "modelform": form, 
            "action": action, 
            "dipendente": dipendente,
            "data_inizio": data_inizio.strftime("%d/%m/%Y"),} 
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def del_retribuzione(request, object_id):
    template = TMP_PROV_CONTRATTO_DELFORM
    
    dipendente_id = object_id
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.RetribuzioneDipendente.objects.filter(id__in=ids).delete()
            
            if len(ids) == 1:
                logger.debug("{}: eliminata la retribuzione [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Retribuzione eliminata')
            elif len(ids) > 1:
                logger.debug("{}: eliminate le retribuzioni [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Retribuzioni eliminate')
            url = reverse("init_provvigione", args=[dipendente_id])
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.RetribuzioneDipendente.objects.filter(id__in=ids)
    
    logger.debug("{}: ha intenzione di eliminare le retribuzioni {} [id={}] per il dipendente {}"
                 .format(request.user, [(str(obj), "id=" + str(obj.id)) for obj in objs], ids, dipendente))
    
    data = {"dipendente": dipendente, "objs": objs, "tipo": "ret",}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def del_vartmp(request, object_id):
    template = TMP_PROV_BONUS_DELFORM
    
    dipendente_id = object_id
    dipendente = get_object_or_404(models.Dipendente, pk=dipendente_id)
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.RetribuzioneDipendente.objects.filter(id__in=ids).delete()
            
            if len(ids) == 1:
                logger.debug("{}: eliminata la variazione temporanea della retribuzione [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Variazione temporanea eliminata')
            elif len(ids) > 1:
                logger.debug("{}: eliminate le variazioni temporanee della retribuzione [id={}]"
                             .format(request.user, ids))
                messages.add_message(request, messages.SUCCESS, 'Variazioni temporanee eliminate')
            url = reverse("init_provvigione", args=[dipendente_id])
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.RetribuzioneDipendente.objects.filter(id__in=ids)
    print(objs)
    logger.debug("{}: ha intenzione di eliminare le varizioni temporanee della retribuzione {} [id={}] per il dipendente {}"
                 .format(request.user, [(str(obj), "id=" + str(obj.id)) for obj in objs], ids, dipendente))
    
    data = {"dipendente": dipendente, "objs": objs, "tipo": "tmp",}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))
