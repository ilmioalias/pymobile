# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse

import pymobile.administration.utils as u
import pymobile.administration.models as models
import pymobile.administration.tables as tables
from pymobile.administration.views.reports.business import get_daily_totals
from pymobile.administration.views.opzione.admin import get_default_options
from pymobile.administration.views.reports.rankings import get_tim_telecom_ranking
from pymobile.administration.views.reports.rankings import get_edison_ranking
from pymobile.administration.views.reports.goals import get_points

#from pymobile.administration.views.reports.business import calc_provvigione
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Get an instance of a logger
logger = logging.getLogger("file")

TMP_HOME="home.html"

@login_required
def init(request):
    template = TMP_HOME
    
    user = request.user
    
    today = datetime.today()
    week = ((today - timedelta(7)).date(), today.date())
    month = (today.date(), (today + timedelta(31)).date())
    # tabella prossimi appuntamenti
    if u.is_telefonista(user):
        appuntamenti = models.Appuntamento.objects.filter(data__gte=today,
                                                          telefonista=user).order_by("data")
    else:
        appuntamenti = models.Appuntamento.objects.filter(data__gte=today).order_by("data")        
    table_appuntamenti = tables.AppuntamentoReportTable(appuntamenti,
                                                  prefix="app-",
                                                  per_page_field=10,) 
    table_appuntamenti.order_by = request.GET.get("app-sort")
    table_appuntamenti.paginate(page=request.GET.get("app-page", 1))
    
    # tabella appuntamenti da richiamare
    if u.is_telefonista(user):
        appuntamenti_richiamare = models.Appuntamento.objects.filter(data_richiamare__gte=today,
                                                          telefonista=user).order_by("data")
    else:
        appuntamenti_richiamare = models.Appuntamento.objects.filter(data_richiamare__gte=today).order_by("data")        
    table_appuntamenti_richiamare = tables.AppuntamentoReportTable(appuntamenti_richiamare,
                                                  prefix="app_ric-",
                                                  per_page_field=10,) 
    table_appuntamenti_richiamare.order_by = request.GET.get("app_ric-sort")
    table_appuntamenti_richiamare.paginate(page=request.GET.get("app_ric-page", 1))
        
    # tabella ultimi contratti
    contratti = models.Contratto.objects.filter(data_stipula__gte=week[0],
                                                data_stipula__lte=week[1]).order_by("data_stipula")        
    table_contratti = tables.ContrattoReportTable(contratti,
                                            prefix="ctr-",
                                            per_page_field=10,) 
    table_contratti.order_by = request.GET.get("ctr-sort")
    table_contratti.paginate(page=request.GET.get("ctr-page", 1))
    
    # tabella prossimi contratti in scadenza
    contratti_scadenza = models.Contratto.objects.filter(data_scadenza__gte=month[0],
                                                         data_scadenza__lte=month[1]).order_by("-data_scadenza")        
    table_contratti_scadenza = tables.ContrattoReportTable(contratti_scadenza,
                                                     prefix="ctr_scd-",
                                                     per_page_field=10,) 
    table_contratti_scadenza.order_by = request.GET.get("ctr_scd-sort")
    table_contratti_scadenza.paginate(page=request.GET.get("ctr_scd-page", 1))
    
    if request.is_ajax():
        data = {"table_appuntamenti": table_appuntamenti,
                "table_appuntamenti_richiamare": table_appuntamenti_richiamare,
                "table_contratti": table_contratti,
                "table_contratti_scadenza": table_contratti_scadenza,}
        return render_to_response(template, 
                                  data,
                                  context_instance=RequestContext(request))   
        
    data = {"table_appuntamenti": table_appuntamenti,
            "table_appuntamenti_richiamare": table_appuntamenti_richiamare,
            "table_contratti": table_contratti,
            "table_contratti_scadenza": table_contratti_scadenza,}
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: u.get_group(user) != "telefonista",)
def send_report_mail(request):
    default_options = get_default_options()
    email = default_options["email_titolare"]
    if email:
        today = datetime.today().date()
        # spediamo nel testo dell'email, alcune informazioni:
        # incasso della giornata: entrate/uscite
        contratti = models.Contratto.objects.filter(data_stipula=today,)\
                                            .order_by("data_stipula")\
                                            .select_related("piano_tariffario")
                                                          
        # Finanze
        finances = get_daily_totals(contratti, today)
        # Classifiche
        period = u.get_current_quarter()
        contratti = models.Contratto.objects.filter(data_stipula__gte=period[0],
                                                    data_stipula__lte=period[1])
        contratti_tim_telecom = contratti.exclude(pianotariffario__tariffa__gestore="edison")
        dipendenti_tim_telecom = models.Dipendente.objects.filter(contratto__pk__in=contratti_tim_telecom)\
                                                            .distinct()\
                                                            .iterator()
        ranking_tim_telecom = get_tim_telecom_ranking(contratti_tim_telecom, 
                                                      dipendenti_tim_telecom)
        contratti_edison = contratti.exclude(pianotariffario__tariffa__gestore="tim")\
                                     .exclude(pianotariffario__tariffa__gestore="telecom")
        dipendenti_edison = models.Dipendente.objects.filter(contratto__pk__in=contratti_edison)\
                                                            .distinct()\
                                                            .iterator()
        ranking_edison = get_edison_ranking(contratti_edison, dipendenti_edison)
        # Obiettivi
        obiettivi = models.Obiettivo.objects.filter(data_inizio__lte=period[0])
        contratti_inviati = models.Contratto.objects.filter(data_inviato__gte=period[0], 
                                                            data_inviato__lte=period[1], 
                                                            inviato=True)\
                                                    .order_by("data_inviato")\
                                                    .select_related("piano_tariffario")
        ignore, goals = get_points(obiettivi, contratti_inviati)
        data = {"finanze": finances,
                "ranking_tim_telecom": ranking_tim_telecom,
                "ranking_edison": ranking_edison,
                "obiettivi": goals,}

        html_content = render_to_string('email.html', 
                                        data) 
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
        
        # create the email, and attach the HTML version as well.
        subject = 'Riepilogo Mobiltime {}'.format(today.strftime("%d/%m/%Y")) 
        from_email = 'agenzia' 
        to_email = email
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email,])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.debug("{}: Email riepilogativa inviata"
                         .format(request.user))
        messages.add_message(request, messages.SUCCESS, 'Email riepilogativa iniviata a {}'. format(email))
    else:
        logger.debug("{}: modificate le opzioni iniziali"
                         .format(request.user))
        messages.add_message(request, messages.ERROR, 'Email non iniviata: '\
                             'Inserire la password del titolare nella pagina delle opzioni')
    return HttpResponseRedirect(reverse("home"))

        