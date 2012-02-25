# -*- coding: utf-8 -*-

import operator
from django.http import HttpResponse 
import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
import pymobile.administration.forms as forms
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404, render
from django.db.models import Sum
from django.template import RequestContext
from datetime import datetime
from django.db.models import Q

def entrate_uscite(request):
    template = "statistiche/entrate_uscite.html"
    
    if request.method == "GET" and request.GET.has_key("fperiodo"):
        period = u.get_period(request.GET)
    else:
        period = u.get_current_month()
        
    # entrate
    # 1 - contratti stipulati
    contratti = models.Contratto.objects.filter(data_stipula__gte=period[0],
                                                data_stipula__lte=period[1])\
                                                .order_by("data_stipula")\
                                                .prefetch_related("piano_tariffario")
    
    # ricaviamo contratti solo degli agenti selezionati 
    if request.method == "GET" and request.GET.has_key("fagente"):
        agenti_ids = u.get_agenti_ids(request.GET)
    
        if agenti_ids:
            contratti = contratti.filter(agente__in=agenti_ids) 
    if request.method == "GET" and request.GET.has_key("ftelefonista"):
        tel_ids = u.get_telefonisti_ids(request.GET)
        if tel_ids:
            contratti = contratti.filter(telefonista__in=tel_ids)    
    
    objs_in = []
    objs_out = []
    
    if contratti.exists():
        date = contratti.values("data_stipula").distinct()
        for data in date:
            in_tot_day = 0 
            contratti_day = contratti.filter(data_stipula=data).iterator()
            n = 0
            for contratto in contratti_day:
                # informazioni utili
                agente = contratto.agente
                telefonista = None
                if contratto.appuntamento.exists():
                    telefonista = contratto.appuntamento.telefonista
                
                # determiniamo il piano tariffario
                pts = contratto.piano_tariffario.iterator()
                in_tot_contratto = 0
                for pt in pts:
                    tariffa = pt.tariffa
                    q = pt.num
                    sac = tariffa.sac
                    
                    # determiniamo le entrate dovute al contratto considerato
                    in_tot_contratto += sac * q
                
                # determiniamo le entrate della giornata
                in_tot_day += in_tot_contratto
                
                n += 1
                
            # inseriamo i dati per la tabella delle entrate
            obj_in = {"data": data, "n_stipulati": n, "entrate": in_tot_day}
            objs_in.append(obj_in)
    
    # creiamo le tabelle 
    table_in = tables.InTable(objs_in, prefix="in")
    table_in.paginate(page=request.GET.get("in-page", 1))
    table_in.order_by = request.GET.get("in-sort")
    table_out = tables.OutTable(objs_out, prefix="out")
    table_out.paginate(page=request.GET.get("out-page", 1))
    table_out.order_by = request.GET.get("out-sort")
    
    if request.is_ajax():
        data = {"table_in": table_in,
                "table_out": table_out,
                "totals_in": totals_in,
                "totals_out": totals_out,
                "period": [datetime.strptime(period[0], "%Y-%m-%d").strftime("%d/%m/%Y"),
                           datetime.strptime(period[1], "%Y-%m-%d").strftime("%d/%m/%Y")]}
        return render_to_response("statistiche/inouttable_snippet.html", data,
                                  context_instance=RequestContext(request))   
    
    filterform = forms.InOutFilterForm()
    
    data = {"table_in": table_in,
            "table_out": table_out,
            "totals_in": totals_in,
            "totals_out": totals_out,
            "filterform": filterform,
            "period": [datetime.strptime(period[0], "%Y-%m-%d").strftime("%d/%m/%Y"),
                       datetime.strptime(period[1], "%Y-%m-%d").strftime("%d/%m/%Y")]}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))  

def calc_provvigione(dipendente, tariffa, data):
    # determiniamo la modalità di calcolo della retribuzione per il dipendente
    # prima verifichiamo se vi una variazione della retribuzione, altrimenti usiamo
    # la retribuzione standard corrente
    retribuzione = models.Retribuzione.objects.get(variazione=True, 
                                                   data_inizio__lte=data,
                                                   data_fine__gte=data)
    if not retribuzione.exists():
        retribuzione = models.Retribuzione.objects.filter(variazione=False,
                                                          data_inizio__lte=data)\
                                                          .order_by("-data_inizio")[0]
  
    provvigione_contratto = retribuzione.provvigione_contratto
    provvigione_bonus = retribuzione.provvigione_bonus
    
    # calcoliamo la provvigione per il contratto, intesa come singola tariffa
    if dipendente.tipo == "agt":
        # provvigione contratto è un valore percentuale
        ret_contratto = tariffa.sac * provvigione_contratto / 100
    elif dipendente.tipo == "tel":
        ret_contratto = provvigione_contratto
    
    # calcoliamo la provvigione bonus (se presente)
    if provvigione_bonus:
        pass
        