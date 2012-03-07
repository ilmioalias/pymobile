# -*- coding: utf-8 -*-

#import operator
from django.http import HttpResponse 
import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
import pymobile.administration.forms as forms
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from decimal import Decimal, getcontext
from datetime import datetime, date

TMP_INIT= "statistiche/obiettivi_trimestrali_admin.html"
TMP_TABLE="statistiche/obiettivi_trimestrali_snippet_table.html"
TMP_FORM="statistiche/obiettivi_trimestrali_modelform.html"
TMP_DEL="statistiche/obiettivi_trimestrali_deleteform.html"

def init_obiettivo_trimestrale(request):
    template = TMP_INIT
   
    obiettivi = models.Obiettivo.objects.all().order_by("-data_inizio")
    
    today = datetime.today().date()
    
    # creaiamo un dizionario con tutte le variazioni e le retribuzioni
    objs = {}
    # variazioni
    if obiettivi.exists():
        date_max = obiettivi[0].data_inizio if obiettivi[0].data_inizio > today else today
        date_min = obiettivi[obiettivi.count() - 1].data_inizio

        for obiettivo in obiettivi:
            date_cur = obiettivo.data_inizio
            parameters = obiettivo.parametri
            k = date_cur.strftime("%Y-%m-%d")
            if k in objs:
                objs[k].append(parameters)
            else:
                objs[k] = [parameters,]    
    else:
        today = datetime.today()
        y = today.year
        date_max = date(y, 10, 31)
        date_min = date(y, 1, 1)
    
    # creiamo i dati per la tabella della gestion obiettivi 
    rows = [] 
    date_cur = date_max
    while date_cur >= date_min:
        month_cur = date_cur.month
        year_cur = date_cur.year
        
        if 1 <= month_cur <= 3:
            quarter_cur = (1, (date(year_cur, 1, 1), date(year_cur, 3, 31)))
        elif 4 <= month_cur <= 6:
            quarter_cur = (2, (date(year_cur, 4, 1), date(year_cur, 6, 30)))
        elif 7 <= month_cur <= 9:
            quarter_cur = (3, (date(year_cur, 7, 1), date(year_cur, 9, 30)))
        elif 10 <= month_cur <= 12:
            quarter_cur = (4, (date(year_cur, 10, 1), date(year_cur, 12, 31)))
        
        k = date_cur.strftime("%Y-%m-%d")
        if not k in objs:
            rows.append({"anno": year_cur, "quarto": quarter_cur})
        else:
            rows.append({"anno": year_cur, "quarto": quarter_cur, "parametri": objs[k]})
        
        # aggiorniamo il contatore della data "date_cur"
        month_cur -= 3 
        if month_cur < 0:
            # il conto è alla rovescia, dalla data più recente a quella meno recente
            # scaliamo di 3 mesi in 3 mesi, quando arriviamo a gennaio dobbiamo
            # scalare di un anno
            month_cur = 10 # ottobre
            year_cur = year_cur - 1
        date_cur = date(year_cur, month_cur, 1)
        
    if request.is_ajax():
        template = TMP_TABLE
        data = {"rows": rows, "period": (date_min, date_max)}
        return render_to_response(template,
                                  data,
                                  context_instance=RequestContext(request))        
    
    data = {"rows": rows, "period": (date_min, date_max)}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def add_obiettivo_trimestrale(request):  
    template = TMP_FORM
    action = "Aggiungi"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.ObiettivoForm(post_query)
        
        if form.is_valid():
            form.save()
            
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_obiettivo_trimestrale")) 
            else:
                url = reverse("init_obiettivo_trimestrale")
                return HttpResponse('''
                    <script type='text/javascript'>
                        opener.redirectAfter(window, '{}');
                    </script>'''.format(url))   
    else:
        form = forms.ObiettivoForm()    
        
    data = {"modelform": form, "action": action,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

def mod_obiettivo_trimestrale(request, object_id):
    template = TMP_FORM
    action = "Modifica"
    
    if request.method == "POST":
        post_query = request.POST.copy()
        obj = get_object_or_404(models.Obiettivo, pk=object_id)
        form = forms.ObiettivoForm(post_query, instance=obj)
    
        if form.is_valid():
            form.save()
            
            if request.POST.has_key("add_another"):              
                return HttpResponseRedirect(reverse("add_obiettivo_trimestrale")) 
            else:
                url = reverse("init_obiettivo_trimestrale", args=[object_id])
                return HttpResponse('''
                    <script type='text/javascript'>
                        opener.redirectAfter(window, '{}');
                    </script>'''.format(url))                    
    else:
        obj = get_object_or_404(models.Obiettivo, pk=object_id) 
        form = forms.ObiettivoForm(instance=obj)
    
    data = {"modelform": form, "action": action,}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def del_obiettivo_trimestrale(request):
    template = TMP_DEL
    
    if request.method == "POST":
        query_post = request.POST.copy()
        
        if query_post.has_key("id"):
            # cancelliamo
            ids = query_post.getlist("id")
            models.Obiettivo.objects.filter(id__in=ids).delete()
            url = reverse("init_obiettivo_trimestrale")
            
            return HttpResponse('''
                <script type='text/javascript'>
                    opener.redirectAfter(window, '{}');
                </script>'''.format(url))
    
    query_get = request.GET.copy()
    ids = query_get.getlist("id")      
    objs = models.Obiettivo.objects.filter(id__in=ids)
    
    data = {"objs": objs}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))
