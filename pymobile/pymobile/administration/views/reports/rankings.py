# -*- coding: utf-8 -*-

import operator
#from django.http import HttpResponse 
import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
import pymobile.administration.forms as forms
from django.shortcuts import render_to_response
from django.db.models import Sum
from django.template import RequestContext
#from datetime import datetime

def canvas_tim_telecom(request):
    template = "statistiche/canvas_tim_telecom.html"
    
    if request.method == "GET" and request.GET.has_key("fperiodo"):
        period = u.get_period(request.GET)
    else:
        period = u.get_current_quarter()
    
    contratti = models.Contratto.objects.filter(data_stipula__gte=period[0],
                                                data_stipula__lte=period[1])
    contratti = contratti.exclude(pianotariffario__tariffa__gestore="edison")
    
    # ricaviamo gli agenti artefici dei contratti selezionati 
    if request.method == "GET" and request.GET.has_key("fagente"):
        agenti_ids = u.get_agenti_ids(request.GET)
        agenti = models.Dipendente.objects.filter(contratto__pk__in=contratti).filter(pk__in=agenti_ids).distinct().iterator()
    else:
        agenti = models.Dipendente.objects.filter(contratto__pk__in=contratti).distinct().iterator()
             
    ordering = None
    if request.method == "GET" and request.GET.has_key("sort"):
        ordering = request.GET["sort"]
    
    objs = []
    
    if contratti.exists(): 
        for agt in agenti:
            contratti_agt = contratti.filter(agente=agt)
            
            if contratti_agt.exists():
                # TIM
                pt_tim_agt = models.PianoTariffario.objects.filter(contratto__in=contratti_agt,
                    tariffa__gestore=models.Gestore.objects.get(denominazione="tim"))
                
                sim_tot = pt_tim_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="sim"),
                    opzione=False).aggregate(tot=Sum("num"))
                sim_tot = sim_tot["tot"] if sim_tot["tot"] else 0
                
                dati_tot = pt_tim_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="dati"),
                    opzione=False).aggregate(tot=Sum("num"))
                dati_tot = dati_tot["tot"] if dati_tot["tot"] else 0
                
                opz_tot = pt_tim_agt.filter(opzione=True).aggregate(tot=Sum("num"))
                opz_tot = opz_tot["tot"] if opz_tot["tot"] else 0

                # calcoliamo il punteggio ricavato dai contratti
                # 1 - estraiamo una lista con quantità delle tariffa * punteggio della tariffa
                # 2 - sommiamo i valori contenuti nella lista
                list_ptg = [ptar.tariffa.punteggio * ptar.num for ptar in pt_tim_agt]
                ptg_tim_tot = reduce(operator.add, list_ptg) if list_ptg else 0
                
                #TELECOM
                pt_telecom_agt = models.PianoTariffario.objects.filter(contratto__in=contratti_agt,
                    tariffa__gestore=models.Gestore.objects.get(denominazione="telecom")) 
                               
                nip_tot = pt_telecom_agt.filter(tariffa__servizio=models.ServizioTariffa.objects.get(denominazione="nip"),
                    opzione=False).aggregate(tot=Sum("num"))
                nip_tot = nip_tot["tot"] if nip_tot["tot"] else 0
                
                ull_tot = pt_telecom_agt.filter(tariffa__servizio=models.ServizioTariffa.objects.get(denominazione="ull"),
                    opzione=False).aggregate(tot=Sum("num"))
                ull_tot = ull_tot["tot"] if ull_tot["tot"] else 0
                
                adsl_tot = pt_telecom_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="adsl"),                                                 
                    opzione=False).aggregate(tot=Sum("num"))
                adsl_tot = adsl_tot["tot"] if adsl_tot["tot"] else 0
                
                # calcoliamo il punteggio ricavato dai contratti
                # 1 - estraiamo una lista con quantità delle tariffe * punteggio della tariffa
                # 2 - sommiamo i valori contenuti nella lista
                list_ptg = [ptar.tariffa.punteggio * ptar.num for ptar in pt_telecom_agt]
                ptg_telecom_tot = reduce(operator.add, list_ptg) if list_ptg else 0
                   
                objs.append({"agente": agt, 
                             "sim": sim_tot, 
                             "dati_opz": dati_tot + opz_tot,
                             "nip_ull": nip_tot + ull_tot,
                             "adsl": adsl_tot,
                             "punti_tim": ptg_tim_tot,
                             "punti_telecom": ptg_telecom_tot,
                             "tot_punti": ptg_tim_tot + ptg_telecom_tot,
                             "posizione": None})
                
        # selezioniamo solo i primi 15 agenti in base al totale dei punteggi
        objs = [ obj for obj in sorted(objs, key=lambda x: x["tot_punti"], reverse=True)[:15]]
        # aggiungiamo il valore della posizione
        # la posizione aumenta solo nel caso in cui il totale dei punti è minore
        pos = 1
        tot_punti_cur = 0
        for obj in objs:
            obj["posizione"] = pos
            if obj["tot_punti"] != tot_punti_cur:
                pos += 1
                tot_punti_cur = obj["tot_punti"]
    
    # calcoliamo i totali
    sim = 0
    dati_opz = 0
    nip_ull = 0
    adsl = 0
    punti_tim = 0
    punti_telecom = 0
    for obj in objs:
        sim += obj["sim"]
        dati_opz += obj["dati_opz"]
        nip_ull += obj["nip_ull"]
        adsl += obj["adsl"]
        punti_tim += obj["punti_tim"]
        punti_telecom += obj["punti_telecom"]
    totals = [sim, dati_opz, nip_ull, adsl, punti_tim, punti_telecom, punti_tim + punti_telecom]
    
    table = tables.CanvasTable(objs, order_by=(ordering,))
    
    if request.is_ajax():
#        template = "statistiche/reporttable_snippet.html"
        data = {"table": table, 
                "totals": totals, 
                "period": (period[0].strftime("%d/%m/%Y"), 
                           period[1].strftime("%d/%m/%Y"))}
        return render_to_response(template, 
                                  data,
                                  context_instance=RequestContext(request))   
    
    filterform = forms.CanvasFilterForm()
    
    data = {"table": table, 
            "totals": totals,
            "filterform": filterform,
            "period": (period[0].strftime("%d/%m/%Y"), 
                       period[1].strftime("%d/%m/%Y"))}
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))    
    
def canvas_edison(request):
    template = "statistiche/canvas_edison.html"
    
    if request.method == "GET" and request.GET.has_key("fperiodo"):
        period = u.get_period(request.GET)
    else:
        period = u.get_current_quarter()
    
    contratti = models.Contratto.objects.filter(pianotariffario__tariffa__gestore="edison",
                                                data_stipula__gte=period[0],
                                                data_stipula__lte=period[1])
    
    # ricaviamo gli agenti artefici dei contratti selezionati
    # ricaviamo gli agenti artefici dei contratti selezionati 
    if request.method == "GET" and request.GET.has_key("fagente"):
        agenti_ids = u.get_agenti_ids(request.GET)
        agenti = models.Dipendente.objects.filter(contratto__pk__in=contratti).filter(pk__in=agenti_ids).distinct().iterator()
    else:
        agenti = models.Dipendente.objects.filter(contratto__pk__in=contratti).distinct().iterator()
    
    ordering = None
    if request.method == "GET" and request.GET.has_key("sort"):
        ordering = request.GET["sort"]
    
    objs = []
    
    if contratti.exists(): 
        for agt in agenti:
            contratti_agt = contratti.filter(agente=agt)
            
            if contratti_agt.exists():
                pt_edison_agt = models.PianoTariffario.objects.filter(contratto__in=contratti_agt)
                bus_en_tot = pt_edison_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="luce"),
                                                  cliente__tipo="bus").aggregate(tot=Sum("num"))
                bus_en_tot = bus_en_tot["tot"] if bus_en_tot["tot"] else 0
                
                pri_en_tot = pt_edison_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="luce"),
                                                  cliente__tipo="pri").aggregate(tot=Sum("num"))
                pri_en_tot = pri_en_tot["tot"] if pri_en_tot["tot"] else 0
                
                bus_gas_tot = pt_edison_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="gas"),
                                                   cliente__tipo="bus").aggregate(tot=Sum("num"))
                bus_gas_tot = bus_gas_tot["tot"] if bus_gas_tot["tot"] else 0
                
                pri_gas_tot = pt_edison_agt.filter(tariffa__tipo=models.TipologiaTariffa.objects.get(denominazione="gas"),
                                                   cliente__tipo="pri").aggregate(tot=Sum("num"))
                pri_gas_tot = pri_gas_tot["tot"] if pri_gas_tot["tot"] else 0               
                   
                objs.append({"agente": agt, 
                            "bus_en": bus_en_tot, 
                            "pri_en": pri_en_tot,
                            "bus_gas": bus_gas_tot,
                            "pri_gas": pri_gas_tot,
                            "tot": bus_en_tot + bus_gas_tot + pri_en_tot + pri_gas_tot,
                            "posizione": None})
                
        # selezioniamo solo i primi 15 agenti in base al totale dei punteggi
        objs = [ obj for obj in sorted(objs, key=lambda x: x["tot"], reverse=True)[:15]]
        # aggiungiamo il valore della posizione
        # la posizione aumenta solo nel caso in cui il totale dei punti è minore
        pos = 1
        tot_punti_cur = 0
        for obj in objs:
            obj["posizione"] = pos
            if obj["tot_punti"] != tot_punti_cur:
                pos += 1
                tot_punti_cur = obj["tot_punti"]

    # calcoliamo i totali
    bus_en= 0
    pri_en = 0
    bus_gas = 0
    pri_gas = 0
    for obj in objs:
        bus_en += obj["bus_en"]
        pri_en += obj["pri_en"]
        bus_gas += obj["bus_gas"]
        pri_gas += obj["pri_gas"]
    totals = [bus_en, pri_en, bus_gas, pri_gas, bus_en + pri_en + bus_gas + pri_gas]
 
    table = tables.CanvasEdisonTable(objs, order_by=(ordering,))
    
    if request.is_ajax():
#        template = "statistiche/reporttable_snippet.html"
        data = {"table": table, 
                "totals": totals, 
                "period": (period[0].strftime("%d/%m/%Y"), 
                           period[1].strftime("%d/%m/%Y"))}
        return render_to_response(template, 
                                  data,
                                  context_instance=RequestContext(request))    
    
    filterform = forms.CanvasFilterForm()
    
    data = {"table": table, 
            "filterform": filterform,
            "period": (period[0].strftime("%d/%m/%Y"), 
                       period[1].strftime("%d/%m/%Y"))}
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))       
    