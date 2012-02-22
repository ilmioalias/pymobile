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
    # 1 - nuovi contratti stipulati
    contratti = models.Contratto.objects.filter(data_stipula__gte=period[0],
                                                data_stipula__lte=period[1]).order_by("data_stipula")
    
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
    objs_out ={}
    
    if contratti.exists(): 
        # calcoliamo entrate/uscite dovute ai contratti
        # quindi: provvigione dai contratti/provvigione agenti e bonus telefonisti
        dates = contratti.values("data_stipula").distinct()
        for d in dates:
            
            # contratti
            stipulati = contratti.filter(data_stipula=d)
            attivati = stipulati.filter(attivato=True)
            
            # entrate
            obj_in = {"data": d.strftime("%d/%m/%Y"),
                      "stip_n": {"stip": 0, "inv": 0, "car": 0, "att": 0},
                      "entrate": {"stip_in": 0, "att_in": 0}}
            
            # conteggio
            obj_in["stip_n"]["stip"] = stipulati.count()
            obj_in["stip_n"]["inv"] = stipulati.filter(inviato=True).count()
            obj_in["stip_n"]["car"] = stipulati.filter(caricato=True).count()
            obj_in["stip_n"]["att"] = attivati.count()
            
            # calcolo entrate stipulati (previste) e attivati (reali)
            pt_stipulati = models.PianoTariffario.objects.filter(contratto__in=stipulati)
            in_stipulati = 0
            in_attivati = 0
            for pt in pt_stipulati:
                income = pt.tariffa.sac * pt.num
                in_stipulati += income
                if pt.contratto.attivato:
                    in_attivati += income 
            
            obj_in["entrate"]["stip_in"] = in_stipulati
            obj_in["entrate"]["att_in"] = in_attivati    
            
            objs_in.append(obj_in)
            
            # uscite
            tot_p_contratto_agenti = 0 # provvigione X contratto totale della giornata dovuta agli agenti
            tot_p_contratto_telefonisti = 0 # provvigione X contratto totale della giornata dovuta ai telefonisti
            tot_p_bonus_agenti = 0 # provvigione bonus totale della giornata dovuta agli agenti
            tot_p_bonus_telefonisti = 0 # provvigione bonus totale della giornata dovuta ai telefonisti
            income = 0 # entrate totali della giornata
            
            for stipulato in stipulati:
                pt_stipulato = stipulato.piano_tariffario__set.all()
                
                agente = stipulato.agente
                telefonista = stipulato.telefonista
                
                # provvigione per contratto
                p_contratto_agente = agente.provvigione_contratto # per agente è valore percentuale
                p_contratto_telefonista = telefonista.provvigione_contratto # per telefonista è valore in euro
                
                # provvigione bonus
                p_bonus_agente = agente.provvigione_bonus # per agente è valore percentuale
                p_bonus_telefonista = telefonista.provvigione_bonus # per telefonista è valore in euro               
                
                # controlliamo se è stata inserita una variazione mensile della provvigione 
                # per quel giorno
                y = d.year
                m = d.month
                var_p_agente = models.ProvvigioneDipendente.objects.get(dipendente=agente,
                                                                        data=y + "-" + m + "-1")
                var_p_telefonista = models.ProvvigioneDipendente.objects.get(dipendente=telefonista,
                                                                             data=y + "-" + m + "-1")
                if var_p_agente.exists():
                    if var_p_agente.provvigione_contratto:
                        p_contratto_agente = var_p_agente.provvigione_contratto
                    if var_p_agente.provvigione_bonus:
                        p_bonus_agente = var_p_agente.provvigione_bonus
                if var_p_telefonista.exists():
                    if var_p_telefonista.provvigione_contratto:
                        p_contratto_telefonista = var_p_telefonista.provvigione_contratto
                    if var_p_telefonista.provvigione_bonus:
                        p_bonus_telefonista = var_p_telefonista.provvigione_bonus 
                
                # totale entrate dal contratto selezionato
                for pt in pt_stipulato:
                    income += pt.tariffa.sac * pt.num
                    
                # calcoliamo la provvigione x contratto dovuta all'agente/telefonista
                tot_p_contratto_agenti += float(income) * p_contratto_agente / 100
                tot_p_contratto_telefonisti += income * p_contratto_telefonista                           
                
            data = d.strftime("%d/%m/%Y")
    
    # calcoliamo i totali rispettivamente delle entrate e delle uscite
    # entrate:
    totals_in = [0, 0, 0, 0, 0, 0]    
    for obj in objs_in:
        totals_in[0] += obj["stip_n"]["stip"]
        totals_in[1] += obj["stip_n"]["inv"]
        totals_in[2] += obj["stip_n"]["car"]
        totals_in[3] += obj["stip_n"]["att"]
        totals_in[4] += obj["entrate"]["stip_in"]
        totals_in[5] += obj["entrate"]["att_in"]        
    
    # uscite
    totals_out = [0, 0, 0]    
    for obj in objs_out:
        totals_out[0] += obj["prov_agt"]
        totals_out[1] += obj["prov_tel"]
        totals_out[2] += obj["tot"]       
    
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
