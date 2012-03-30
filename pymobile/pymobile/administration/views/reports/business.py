# -*- coding: utf-8 -*-

import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
import pymobile.administration.forms as forms
from decimal import Decimal, getcontext

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test

def get_daily_totals(contratti, date):
    in_tot_day = 0
    out_tot_day = 0
    out_tot_prov_agt_day = 0
    out_tot_prov_tel_day = 0
    out_tot_prov_bonus_agt_day = 0
    out_tot_prov_bonus_tel_day = 0
    
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
        
        # determiniamo il piano tariffario
        pts = models.PianoTariffario.objects.filter(contratto=contratto).iterator()
    
        in_tot_contratto = 0
        out_tot_prov_agt_contratto = 0
        out_tot_prov_tel_contratto = 0
        out_tot_prov_bonus_agt_contratto = 0
        out_tot_prov_bonus_tel_contratto = 0
        for pt in pts:
            tariffa = pt.tariffa
            q = pt.num
            sac = float(tariffa.sac)
            
            # determiniamo le entrate dovute alla tariffa del contratto considerato
            in_tot_contratto += sac * q
            
            # determiniamo le uscite dovute alla tariffa del contratto considerato
            # 1: provvigione dovuta all'agente:                    
            prov_agente = calc_provvigione(agente, cliente, tariffa, date)
            out_tot_prov_agt_contratto += prov_agente[0] * q
            out_tot_prov_bonus_agt_contratto += prov_agente[1] * q
            # 2: provvigione dovuta al telefonista
            if telefonista:
                prov_telefonista = calc_provvigione(telefonista, cliente, 
                                                    tariffa, 
                                                    date)
                out_tot_prov_tel_contratto += prov_telefonista[0] * q
                out_tot_prov_bonus_tel_contratto += prov_telefonista[1] * q
            
        # determiniamo le entrate della giornata
        in_tot_day += in_tot_contratto
        
        # determiniamo le uscite della giornata
        out_tot_prov_agt_day += out_tot_prov_agt_contratto
        out_tot_prov_bonus_agt_day += out_tot_prov_bonus_agt_contratto
        out_tot_prov_tel_day += out_tot_prov_tel_contratto
        out_tot_prov_bonus_tel_day += out_tot_prov_bonus_tel_contratto
        out_tot_day = out_tot_prov_agt_day + out_tot_prov_bonus_agt_day + \
            out_tot_prov_tel_day + out_tot_prov_bonus_tel_day + \
            vas_telefonista + vas_agente
        
        n += 1
        if contratto.attivato:
            a += 1
        if contratto.completo:
            c += 1
        if contratto.inviato:
            i += 1
        if contratto.caricato:
            cr += 1

    tot = {"entrate": in_tot_day,
           "uscite": out_tot_day,
           "totali": in_tot_day - out_tot_day}
    tot_in = {"entrate": in_tot_day}
    tot_out = {"uscite": out_tot_day,
               "prov_agt": out_tot_prov_agt_day, 
               "prov_bonus_agt": out_tot_prov_bonus_agt_day,
               "prov_tel": out_tot_prov_tel_day,
               "prov_bonus_tel": out_tot_prov_bonus_tel_day,}            
    
#    t = str(n) + "/" + str(c) + "/" + str(i) + "/" + str(cr) + "/" + str(a)
    t = {"stipulati": n, "completi": c, "inviati": i, "caricati": cr, "attivati": a,}
    return {"totali": tot, "entrate": tot_in, "uscite": tot_out, "contratti": t, }

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def inout(request):
    #TODO: controllare che effettivamente i calcoli siano giusti
    getcontext().prec = 2
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
                                                .select_related("piano_tariffario")
                                                  
    # ricaviamo contratti solo degli agenti selezionati 
    if request.method == "GET" and request.GET.has_key("fagente"):
        agenti_ids = u.get_agenti_ids(request.GET)
    
        if agenti_ids:
            contratti = contratti.filter(agente__in=agenti_ids) 
    if request.method == "GET" and request.GET.has_key("ftelefonista"):
        tel_ids = u.get_telefonisti_ids(request.GET)
        if tel_ids:
            contratti = contratti.filter(telefonista__in=tel_ids)    
    
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
    out_tot_prov_agt = 0
    out_tot_prov_bonus_agt = 0
    out_tot_prov_tel = 0
    out_tot_prov_bonus_tel = 0
    
    if contratti.exists():
        
        dates = contratti.values("data_stipula").distinct()
        for date in dates:
#            in_tot_day = 0
#            out_tot_day = 0
#            out_tot_prov_agt_day = 0
#            out_tot_prov_tel_day = 0
#            out_tot_prov_bonus_agt_day = 0
#            out_tot_prov_bonus_tel_day = 0

            contratti_day = contratti.filter(data_stipula=date).iterator()
            
#            n = 0
#            a = 0
#            c = 0
#            i = 0
#            cr = 0
#            for contratto in contratti_day:
#                # informazioni utili
#                cliente = contratto.cliente
#                agente = contratto.agente
#                telefonista = None
#                if contratto.appuntamento:
#                    telefonista = contratto.appuntamento.telefonista
#                
#                # uscite: bonus per agente/telefonista in base al contratto
#                vas_agente = float(contratto.vas_agente)
#                vas_telefonista = float(contratto.vas_telefonista)
#                
#                # determiniamo il piano tariffario
#                pts = models.PianoTariffario.objects.filter(contratto=contratto).iterator()
#            
#                in_tot_contratto = 0
#                out_tot_prov_agt_contratto = 0
#                out_tot_prov_tel_contratto = 0
#                out_tot_prov_bonus_agt_contratto = 0
#                out_tot_prov_bonus_tel_contratto = 0
#                for pt in pts:
#                    tariffa = pt.tariffa
#                    q = pt.num
#                    sac = float(tariffa.sac)
#                    
#                    # determiniamo le entrate dovute alla tariffa del contratto considerato
#                    in_tot_contratto += sac * q
#                    
#                    # determiniamo le uscite dovute alla tariffa del contratto considerato
#                    # 1: provvigione dovuta all'agente:                    
#                    prov_agente = calc_provvigione(agente, cliente, tariffa, date["data_stipula"])
#                    out_tot_prov_agt_contratto += prov_agente[0] * q
#                    out_tot_prov_bonus_agt_contratto += prov_agente[1] * q
#                    # 2: provvigione dovuta al telefonista
#                    if telefonista:
#                        prov_telefonista = calc_provvigione(telefonista, cliente, 
#                                                            tariffa, 
#                                                            date["data_stipula"])
#                        out_tot_prov_tel_contratto += prov_telefonista[0] * q
#                        out_tot_prov_bonus_tel_contratto += prov_telefonista[1] * q
#                    
#                # determiniamo le entrate della giornata
#                in_tot_day += in_tot_contratto
#                
#                # determiniamo le uscite della giornata
#                out_tot_prov_agt_day += out_tot_prov_agt_contratto
#                out_tot_prov_bonus_agt_day += out_tot_prov_bonus_agt_contratto
#                out_tot_prov_tel_day += out_tot_prov_tel_contratto
#                out_tot_prov_bonus_tel_day += out_tot_prov_bonus_tel_contratto
#                out_tot_day = out_tot_prov_agt_day + out_tot_prov_bonus_agt_day + \
#                    out_tot_prov_tel_day + out_tot_prov_bonus_tel_day + \
#                    vas_telefonista + vas_agente
#                
#                n += 1
#                n_stipulati += 1
#                if contratto.attivato:
#                    a += 1
#                    n_attivati += 1
#                if contratto.completo:
#                    c += 1
#                    n_completi += 1
#                if contratto.inviato:
#                    i += 1
#                    n_inviati += 1
#                if contratto.caricato:
#                    cr += 1
#                    n_caricati += 1
#                
#            # inseriamo i dati per la tabella delle entrate
#            t = str(n) + "/" + str(c) + "/" + str(i) + "/" + str(cr) + "/" + str(a)
#            obj = {"data": date["data_stipula"],
#                    "n_stipulati": t,
#                    "entrate": "{0:.2f}".format(Decimal(in_tot_day)),
#                    "uscite": "{0:.2f}".format(Decimal(out_tot_day)),
#                    "totali": "{0:.2f}".format(Decimal(in_tot_day - out_tot_day))}
#            obj_in = {"data": date["data_stipula"], 
#                      "n_stipulati": t, 
#                      "entrate": "{0:.2f}".format(Decimal(in_tot_day))}
#            obj_out = {"data": date["data_stipula"], 
#                       "n_stipulati": t, 
#                       "uscite": "{0:.2f}".format(Decimal(out_tot_day)),
#                       "prov_agt": "{0:.2f}".format(Decimal(out_tot_prov_agt_day)), 
#                       "prov_bonus_agt": "{0:.2f}".format(Decimal(out_tot_prov_bonus_agt_day)),
#                       "prov_tel": "{0:.2f}".format(Decimal(out_tot_prov_tel_day)),
#                       "prov_bonus_tel": "{0:.2f}".format(Decimal(out_tot_prov_bonus_tel_day)),}
            
            daily_totals = get_daily_totals(contratti_day, date["data_stipula"]) 
            
            t = "{}/{}/{}/{}".format(daily_totals["contratti"]["stipulati"],
                                     daily_totals["contratti"]["completi"],
                                     daily_totals["contratti"]["inviati"],
                                     daily_totals["contratti"]["caricati"],
                                     daily_totals["contratti"]["attivati"])
            objs.append({"data": date["data_stipula"], 
                         "n_stipulati": t, 
                         "entrate": "{0:.2f}".format(Decimal(daily_totals["totali"]["entrate"])), 
                         "uscite": "{0:.2f}".format(Decimal(daily_totals["totali"]["uscite"])),
                         "totali": "{0:.2f}".format(Decimal(daily_totals["totali"]["totali"])),})
            objs_in.append({"data": date["data_stipula"], 
                            "n_stipulati": t, 
                            "entrate": "{0:.2f}".format(Decimal(daily_totals["entrate"]["entrate"]))}) 
            objs_out.append({"data": date["data_stipula"], 
                            "n_stipulati": t, 
                            "uscite": "{0:.2f}".format(Decimal(daily_totals["uscite"]["uscite"])),
                            "prov_agt": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_agt"])),
                            "prov_bonus_agt": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_bonus_agt"])),
                            "prov_tel": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_tel"])),
                            "prov_bonus_tel": "{0:.2f}".format(Decimal(daily_totals["uscite"]["prov_bonus_tel"]))})
#            
#            objs.append(obj)
#            objs_in.append(obj_in)
#            objs_out.append(obj_out)
            
            # aggoirniamo i totali
            in_tot += daily_totals["totali"]["entrate"]
            out_tot += daily_totals["totali"]["uscite"]
            out_tot_prov_agt += daily_totals["uscite"]["prov_agt"]
            out_tot_prov_bonus_agt += daily_totals["uscite"]["prov_bonus_agt"]
            out_tot_prov_tel += daily_totals["uscite"]["prov_tel"]
            out_tot_prov_bonus_tel += daily_totals["uscite"]["prov_bonus_tel"]
            
            n_stipulati += daily_totals["contratti"]["stipulati"]
            n_completi += daily_totals["contratti"]["completi"]
            n_inviati += daily_totals["contratti"]["inviati"]
            n_caricati += daily_totals["contratti"]["caricati"]
            n_attivati += daily_totals["contratti"]["attivati"]
#            in_tot += in_tot_day
#            out_tot += out_tot_day
#            out_tot_prov_agt += out_tot_prov_agt_day
#            out_tot_prov_bonus_agt += out_tot_prov_bonus_agt_day
#            out_tot_prov_tel += out_tot_prov_tel_day
#            out_tot_prov_bonus_tel += out_tot_prov_bonus_tel_day
    
    totals = ["{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati), 
             "{0:.2f}".format(Decimal(in_tot)),
             "{0:.2f}".format(Decimal(out_tot)),
             "{0:.2f}".format(Decimal(in_tot - out_tot)),]
    totals_in = ["{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati), 
                 "{0:.2f}".format(Decimal(in_tot)),]
    totals_out = ["{}/{}/{}/{}/{}".format(n_stipulati, n_completi, n_inviati, n_caricati, n_attivati),
                  "{0:.2f}".format(Decimal(out_tot_prov_agt)),
                  "{0:.2f}".format(Decimal(out_tot_prov_bonus_agt)),
                  "{0:.2f}".format(Decimal(out_tot_prov_tel)),
                  "{0:.2f}".format(Decimal(out_tot_prov_bonus_tel)),
                  "{0:.2f}".format(Decimal(out_tot)),]
    
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
#        template = "statistiche/entrate_uscite_table_snippet.html"
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
                                                                    data_inizio__lte=date)\
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
                    if tariffa.gestore != v:
                        res = False
                        break
                elif k == "profilo":
                    if tariffa.profilo != v:
                        res = False
                        break
                elif k == "tipo":
                    if tariffa.tipo != v:
                        res = False
                        break
                elif k == "fascia":
                    if tariffa.fascia != v:
                        res = False
                        break
                elif k == "servizio":
                    if tariffa.servizio != v:
                        res = False
                        break
            
            if res:
                ret_bonus += value["provvigione"]
        
    return (ret_contratto, ret_bonus)
