# -*- coding: utf-8 -*-

import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
import pymobile.administration.forms as forms
from decimal import Decimal, getcontext
from datetime import timedelta

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q


def get_daily_totals(contratti, date):
    in_tot_day = 0
    out_tot_day = 0
    in_detail_day = {}
    out_detail_day = {}
    n_stipulati_details = {}
    gestori = models.Gestore.objects.all()
    for gestore in gestori:
        g = str(gestore)
        in_detail_day[g] = 0
        out_detail_day[g] = 0
        n_stipulati_details[g] = 0
    out_tot_prov_agt_day = 0
    out_tot_prov_tel_day = 0
    out_tot_prov_bonus_agt_day = 0
    out_tot_prov_bonus_tel_day = 0
    out_tot_extra_agt = 0
    out_tot_extra_tel = 0
    
    n = 0
    a = 0
    c = 0
    i = 0
    cr = 0
    
    for contratto in contratti:
        # informazioni utili
        cliente = contratto.cliente
        agente = contratto.agente
        telefonista = None
        if contratto.appuntamento:
            telefonista = contratto.appuntamento.telefonista
        
        # uscite: bonus per agente/telefonista in base al contratto
        vas_agente = float(contratto.vas_agente)
        vas_telefonista = float(contratto.vas_telefonista)
        out_tot_extra_agt += vas_agente
        out_tot_extra_tel += vas_telefonista 
        
        # determiniamo il piano tariffario
        pts = models.PianoTariffario.objects.filter(contratto=contratto).iterator()

        for pt in pts:
            tariffa = pt.tariffa
            gestore = str(tariffa.gestore)
            q = pt.num
            sac = float(tariffa.sac)
            
            # determiniamo le entrate dovute alla tariffa del contratto considerato
            partial = sac * q
            in_detail_day[gestore] += partial
            in_tot_day += partial
            
            # determiniamo le uscite dovute alla tariffa del contratto considerato
            # 1: provvigione dovuta all'agente:                    
            prov_agente = calc_provvigione(agente, cliente, tariffa, date)
            o_agt_prov = prov_agente[0] * q
            out_tot_prov_agt_day += o_agt_prov
            o_agt_bonus = prov_agente[1] * q
            out_tot_prov_bonus_agt_day += o_agt_bonus
            out_detail_day[gestore] += o_agt_prov + o_agt_bonus 
            # 2: provvigione dovuta al telefonista
            if telefonista:
                prov_telefonista = calc_provvigione(telefonista, cliente, 
                                                    tariffa, 
                                                    date)
                o_tel_prov = prov_telefonista[0] * q
                out_tot_prov_tel_day += prov_telefonista[0] * q
                o_tel_bonus = prov_telefonista[1] * q
                out_tot_prov_bonus_tel_day += prov_telefonista[1] * q
                out_detail_day[gestore] += o_tel_prov + o_tel_bonus
            
        # determiniamo le uscite della giornata
        out_tot_day = out_tot_prov_agt_day + out_tot_prov_bonus_agt_day + \
            out_tot_prov_tel_day + out_tot_prov_bonus_tel_day + \
            vas_telefonista + vas_agente
                
        n += 1
        n_stipulati_details[gestore] += 1
        if contratto.attivato:
            a += 1
        if contratto.completo:
            c += 1
        if contratto.inviato:
            i += 1
        if contratto.caricato:
            cr += 1
    
    tot_detail_day = {}
    for gestore in gestori:
        g = str(gestore)
        tot_detail_day[g] =  in_detail_day[g] - out_detail_day[g]
    tot = {"entrate": {"total": in_tot_day,
                       "details": in_detail_day},
           "uscite": {"total": out_tot_day,
                      "details": out_detail_day},
           "totali": {"total": in_tot_day - out_tot_day,
                      "details": tot_detail_day}}
    tot_in = {"entrate": {"total":in_tot_day,
                          "details": in_detail_day}}
    tot_out = {"uscite": {"total": out_tot_day,
                          "details": out_detail_day},
               "prov_agt": out_tot_prov_agt_day, 
               "prov_bonus_agt": out_tot_prov_bonus_agt_day,
               "prov_tel": out_tot_prov_tel_day,
               "prov_bonus_tel": out_tot_prov_bonus_tel_day,
               "extra_agt": out_tot_extra_agt,
               "extra_tel": out_tot_extra_tel,}            
    
    t = {"stipulati": n, 
         "completi": c, 
         "inviati": i, 
         "caricati": cr, 
         "attivati": a, 
         "details": n_stipulati_details}
    return {"totali": tot, "entrate": tot_in, "uscite": tot_out, "contratti": t, }

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) == "amministratore")
def inout(request):
    #TODO: controllare che effettivamente i calcoli siano giusti
#    getcontext().prec = 2
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
                                                .select_related()
                                                  
    # ricaviamo contratti solo degli agenti selezionati 
    if request.method == "GET" and request.GET.has_key("fagente"):
        agenti_ids = u.get_agenti_ids(request.GET)
    
        if agenti_ids:
            contratti = contratti.filter(agente__in=agenti_ids) 
    if request.method == "GET" and request.GET.has_key("ftelefonista"):
        tel_ids = u.get_telefonisti_ids(request.GET)
        if tel_ids:
#            contratti = contratti.filter(telefonista__in=tel_ids)
            filter_ids = []
            telefonisti = models.Dipendente.objects.filter(id__in=tel_ids)
            for contratto in contratti:
                if contratto.appuntamento:
                    if contratto.appuntamento.telefonista in telefonisti:
                        filter_ids.append(contratto.id)
            if filter_ids:
                contratti = contratti.filter(id__in=filter_ids)
               
    # FIXME: implementare selezione gestori
    
    objs = []
    objs_in = []
    objs_out = []
    
    n_stipulati = 0
    n_completi = 0
    n_inviati = 0
    n_caricati = 0
    n_attivati = 0
    in_tot = 0
    out_tot = 0
    in_tot_detail = {}
    out_tot_detail = {}
    gestori = models.Gestore.objects.all()
    for gestore in gestori:
        g = str(gestore)
        in_tot_detail[g] = 0
        out_tot_detail[g] = 0
    out_tot_prov_agt = 0
    out_tot_prov_bonus_agt = 0
    out_tot_prov_tel = 0
    out_tot_prov_bonus_tel = 0
    
    if contratti.exists():
        dates = contratti.values("data_stipula").distinct()
        for date in dates:
            contratti_day = contratti.filter(data_stipula=date["data_stipula"]).iterator()
            
            daily_totals = get_daily_totals(contratti_day, date["data_stipula"]) 
            t = "{}/{}/{}/{}".format(daily_totals["contratti"]["stipulati"],
                                     daily_totals["contratti"]["completi"],
                                     daily_totals["contratti"]["inviati"],
                                     daily_totals["contratti"]["caricati"],
                                     daily_totals["contratti"]["attivati"])
            objs.append({"data": date["data_stipula"], 
                         "n_stipulati": t, 
                         "entrate": daily_totals["totali"]["entrate"], 
                         "uscite": daily_totals["totali"]["uscite"],
                         "totali": daily_totals["totali"]["totali"]})
            objs_in.append({"data": date["data_stipula"],
                            "n_stipulati": t,
                            "entrate": daily_totals["entrate"]["entrate"]})
            objs_out.append({"data": date["data_stipula"], 
                            "n_stipulati": t,
                            "uscite": daily_totals["uscite"]["uscite"],
                            "prov_agt": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_agt"])),
                            "prov_bonus_agt": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_bonus_agt"])),
                            "prov_tel": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_tel"])),
                            "prov_bonus_tel": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_bonus_tel"]))})

            # aggoiorniamo i totali
            in_tot += daily_totals["totali"]["entrate"]["total"]
            out_tot += daily_totals["totali"]["uscite"]["total"]
            # aggiorniamo i dettagli dei totali
            for gestore in gestori:
                g = str(gestore)
                in_tot_detail[g] += daily_totals["totali"]["entrate"]["details"][g]
                out_tot_detail[g] += daily_totals["totali"]["uscite"]["details"][g]
            out_tot_prov_agt += daily_totals["uscite"]["prov_agt"]
            out_tot_prov_bonus_agt += daily_totals["uscite"]["prov_bonus_agt"]
            out_tot_prov_tel += daily_totals["uscite"]["prov_tel"]
            out_tot_prov_bonus_tel += daily_totals["uscite"]["prov_bonus_tel"]
            
            n_stipulati += daily_totals["contratti"]["stipulati"]
            n_completi += daily_totals["contratti"]["completi"]
            n_inviati += daily_totals["contratti"]["inviati"]
            n_caricati += daily_totals["contratti"]["caricati"]
            n_attivati += daily_totals["contratti"]["attivati"]
    
    # aggiungiamo il fisso
    tot_fisso = calc_fisso(period)
    out_tot += tot_fisso
    
    tot_tot_detail = {}
    for gestore in gestori:
        g = str(gestore)
        tot_tot_detail[g] = in_tot_detail[g] - out_tot_detail[g]
    tot_tot_detail["fisso"] = tot_fisso
    out_tot_detail["fisso"] = tot_fisso
    
    totals = {"n_stipulati": "{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati),
              "entrate": {"total": in_tot,
                          "details": in_tot_detail},
              "uscite": {"total": out_tot,
                         "details": out_tot_detail},
              "totali": {"total": in_tot - out_tot,
                         "details": tot_tot_detail}}
    totals_in = {"n_stipulati": "{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati),
                 "entrate": {"total": in_tot,
                             "details": in_tot_detail}}
    totals_out = {"n_stipulati": "{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati),
                  "uscite": {"total": out_tot,
                             "details": out_tot_detail},
                  "prov_agt": out_tot_prov_agt,
                  "prov_bonus_agt": out_tot_prov_bonus_agt,
                  "prov_tel": out_tot_prov_tel,
                  "prov_bonus_tel": out_tot_prov_bonus_tel}
    
    # creiamo le tabelle 
    table = tables.InOutTotalsTable(objs, per_page_field=10,)
    table.paginate(page=request.GET.get("page", 1))
    table.order_by = request.GET.get("sort")    
    table_in = tables.InTable(objs_in, prefix="in-", per_page_field=10,)
    table_in.paginate(page=request.GET.get("in-page", 1))
    table_in.order_by = request.GET.get("in-sort")
    table_out = tables.OutTable(objs_out, prefix="out-", per_page_field=10,)
    table_out.paginate(page=request.GET.get("out-page", 1))
    table_out.order_by = request.GET.get("out-sort")
    
    if request.is_ajax():
        data = {"table": table,
                "table_in": table_in,
                "table_out": table_out,
                "totals": totals,
                "totals_in": totals_in,
                "totals_out": totals_out,
                "period": (period[0], period[1])}
        return render_to_response(template, 
                                  data,
                                  context_instance=RequestContext(request))   
    
    filterform = forms.InOutFilterForm()
    
    data = {"table": table,
            "table_in": table_in,
            "table_out": table_out,
            "totals": totals,
            "totals_in": totals_in,
            "totals_out": totals_out,
            "filterform": filterform,
            "period": (period[0], period[1])}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))  

# calcolare il fisso
def calc_fisso(period, dipendenti=None):
    # determiniamo i dipendenti attivi per il periodo di tempo consderato
    if not dipendenti:
        dipendenti = models.Dipendente.objects.filter(Q(data_assunzione__gte=period[0],
                                                        data_assunzione__lte=period[1]) |
                                                      Q(data_licenziamento__gte=period[0],
                                                        data_licenziamento__lte=period[1]) |
                                                      Q(data_assunzione__lte=period[0],
                                                        data_licenziamento__gte=period[1]))\
                                                     .distinct()\
                                                     .iterator()
    fisso_tot = 0
    for dipendente in dipendenti:
        retribuzioni = dipendente.retribuzionedipendente_set.filter(Q(data_inizio__gte=period[0], 
                                                                      data_inizio__lte=period[1]) |
                                                                    Q(data_fine__gte=period[0],
                                                                      data_fine__lte=period[1]) |
                                                                    Q(data_inizio__lte=period[0],
                                                                      data_fine__gte=period[1]),
                                                                    variazione=False,)\
                                                                    .distinct()\
                                                                    .order_by("data_inizio")
        start = period[0]
        if start < retribuzioni[0].data_inizio:
            start = retribuzioni[0].data_inizio
        for retribuzione in retribuzioni:
            end = retribuzione.data_fine
            if not end or end > period[1]:
                end = period[1]
            days = (end - start).days
            # fisso calcolato su 30 giorni
            fisso_tot += days * (retribuzione.fisso / 30)
            if not end:
                break
            start = retribuzione.data_inizio
    
    return float(fisso_tot)
            
        
def calc_provvigione(dipendente, cliente, tariffa, date):
    # determiniamo la modalità di calcolo della retribuzione per il dipendente
    # prima verifichiamo se vi una variazione della retribuzione, altrimenti usiamo
    # la retribuzione standard corrente
    retribuzione = models.RetribuzioneDipendente.objects.filter(variazione=True,
                                                                dipendente=dipendente, 
                                                                data_inizio__lte=date,
                                                                data_fine__gte=date)
    
    if not retribuzione.exists():
        retribuzione = models.RetribuzioneDipendente.objects.filter(variazione=False,
                                                                    dipendente=dipendente,
                                                                    data_inizio__lte=date,)\
                                                                    .order_by("-data_inizio")
    
        if not retribuzione.exists():
            # vuol dire che nella data scelta il dipendente non viene pagato
            return (0, 0)
    
    # prendiamo il primo elemento, perché filter ritorna una lista
    retribuzione = retribuzione[0]
    
    provvigione_contratto = float(retribuzione.provvigione_contratto)
    provvigione_bonus = retribuzione.provvigione_bonus
    sac = float(tariffa.sac)
    
    # calcoliamo la provvigione per il contratto, intesa come singola tariffa
    ret_contratto = 0
    if dipendente.ruolo == "agt":
        # provvigione contratto è un valore percentuale
        ret_contratto = sac * provvigione_contratto / 100
    elif dipendente.ruolo == "tel":
        ret_contratto = provvigione_contratto
    
    # calcoliamo la provvigione bonus (se presente)
    ret_bonus = 0
    if provvigione_bonus:
        values = u.values_from_provvigione_bonus(provvigione_bonus)
        
        for value in values:
            res = True
            pars = value["parameters"]
            for k, v in pars.iteritems():
                if k == "blindato":
                    if cliente.blindato != v:
                        res = False
                        break
                elif k == "gestore":
                    if tariffa.gestore.lower() != v:
                        res = False
                        break
                elif k == "profilo":
                    if tariffa.profilo.lower() != v:
                        res = False
                        break
                elif k == "tipo":
                    if tariffa.tipo.lower() != v:
                        res = False
                        break
                elif k == "fascia":
                    if tariffa.fascia.lower() != v:
                        res = False
                        break
                elif k == "servizio":
                    if tariffa.servizio.lower() != v:
                        res = False
                        break
            
            if res:
                ret_bonus += value["provvigione"]
        
    return (ret_contratto, ret_bonus)

@login_required
#@user_passes_test(lambda user: not u.is_telefonista(user),)
@user_passes_test(lambda user: u.get_group(user) != "telefonista")
def details(request):
    #TODO: controllare che effettivamente i calcoli siano giusti
#    getcontext().prec = 2
    template = "statistiche/dettaglio_dipendente.html"
    
    if request.method == "GET" and request.GET.has_key("fperiodo"):
        period = u.get_period(request.GET)
    else:
        period = u.get_current_month()
        
    # entrate
    # 1 - contratti stipulati
    contratti = models.Contratto.objects.filter(data_stipula__gte=period[0], 
                                                data_stipula__lte=period[1])\
                                                .order_by("data_stipula")\
                                                .select_related()
                                                  
    # ricaviamo contratti solo degli agenti selezionati
    dipendente = None 
    if request.method == "GET" and request.GET.has_key("fdipendente"):
        dipendente_id = request.GET["fdipendente"][1:]
        
        if dipendente_id:
            dipendente = models.Dipendente.objects.get(id=dipendente_id)
            if dipendente.ruolo == "agt":
                contratti = contratti.filter(agente=dipendente)
            else:
                filter_ids = []
                for contratto in contratti:
                    if contratto.appuntamento:
                        if contratto.appuntamento.telefonista == dipendente:
                            filter_ids.append(contratto.id)
                if filter_ids:
                    contratti = contratti.filter(id__in=filter_ids)
    
    n_stipulati = 0
#    n_completi = 0
#    n_inviati = 0
#    n_caricati = 0
#    n_attivati = 0
    in_tot = 0
    out_tot = 0
    tot_fisso = 0
    in_tot_detail = {}
    out_tot_detail = {}
    n_stipulati_details ={}
    gestori = models.Gestore.objects.all()
    for gestore in gestori:
        g = str(gestore)
        in_tot_detail[g] = 0
        out_tot_detail[g] = 0
        n_stipulati_details[g] = 0
    out_tot_prov_agt = 0
    out_tot_prov_bonus_agt = 0
    out_tot_extra_agt = 0
    out_tot_prov_tel = 0
    out_tot_prov_bonus_tel = 0
    out_tot_extra_tel = 0
    
    if contratti.exists() and dipendente:
        dates = contratti.values("data_stipula").distinct()
        for date in dates:
            contratti_day = contratti.filter(data_stipula=date["data_stipula"]).iterator()
            daily_totals = get_daily_totals(contratti_day, date["data_stipula"]) 
            
            n_stipulati += daily_totals["contratti"]["stipulati"]
            # aggoiorniamo i totali
            in_tot += daily_totals["totali"]["entrate"]["total"]
            if dipendente.ruolo == "agt":
                out_tot += (daily_totals["uscite"]["prov_agt"] + 
                            daily_totals["uscite"]["prov_bonus_agt"] +
                            daily_totals["uscite"]["extra_agt"])
                out_tot_extra_agt += daily_totals["uscite"]["extra_agt"]
            else:
                out_tot += (daily_totals["uscite"]["prov_tel"] + 
                            daily_totals["uscite"]["prov_bonus_tel"] +
                            daily_totals["uscite"]["extra_tel"])
                out_tot_extra_tel += daily_totals["uscite"]["extra_tel"]
            # aggiorniamo i dettagli dei totali
            for gestore in gestori:
                g = str(gestore)
                in_tot_detail[g] += daily_totals["totali"]["entrate"]["details"][g]
                out_tot_detail[g] += daily_totals["totali"]["uscite"]["details"][g]
                n_stipulati_details[g] += daily_totals["contratti"]["details"][g]
            out_tot_prov_agt += daily_totals["uscite"]["prov_agt"]
            out_tot_prov_bonus_agt += daily_totals["uscite"]["prov_bonus_agt"]
            out_tot_prov_tel += daily_totals["uscite"]["prov_tel"]
            out_tot_prov_bonus_tel += daily_totals["uscite"]["prov_bonus_tel"]

        # aggiungiamo il fisso
        tot_fisso = calc_fisso(period, [dipendente,])
        out_tot += tot_fisso
        
    tot_tot_detail = {}
    for gestore in gestori:
        g = str(gestore)
        tot_tot_detail[g] = in_tot_detail[g] - out_tot_detail[g]
    tot_tot_detail["fisso"] = tot_fisso
    out_tot_detail["fisso"] = tot_fisso
    
    details = {}
    if dipendente:
        details["stipulati"] = {}
        details["stipulati"]["tot"] = n_stipulati
        details["stipulati"]["details"] = n_stipulati_details
        details["economia"] = {}
        details["economia"]["tot_uscite"] = out_tot
        details["economia"]["tot_fisso"] = tot_tot_detail["fisso"]
        if dipendente.ruolo == "agt":
            details["economia"]["tot_prov"] = out_tot_prov_agt
            details["economia"]["tot_prov_bonus"] = out_tot_prov_bonus_agt
            details["economia"]["extra"] = out_tot_extra_agt
        else:
            details["economia"]["tot_prov"] = out_tot_prov_tel
            details["economia"]["tot_prov_bonus"] = out_tot_prov_bonus_tel
            details["economia"]["extra"] = out_tot_extra_tel
        details["economia"]["tot_entrate"] = in_tot
    
    if request.is_ajax():
        data = {"dipendente": dipendente,
                "details": details,
                "period": (period[0], period[1])}
        return render_to_response(template, 
                                  data,
                                  context_instance=RequestContext(request))   
    
    filterform = forms.DetailsForm()
    
    data = {"dipendente": dipendente,
            "details": details,
            "filterform": filterform,
            "period": (period[0], period[1])}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))  
