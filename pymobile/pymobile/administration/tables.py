# -*- coding: utf-8 -*-

import django_tables2 as tables
from django_tables2.utils import A
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.conf import settings

import pymobile.administration.models as models

#-------------------------------------------------------------------------------
# AMMINISTRAIONE

class BooleanColumn(tables.Column):
    def render(self, value):
        if value:
            return mark_safe("<img src='{}/img/checkbox_true.png' />".format(settings.STATIC_URL))
        else:
            return mark_safe("<img src='{}/img/checkbox_false.png' />".format(settings.STATIC_URL))

class NullColumn(tables.Column):
    def render(self, value):
        if value:
            return tables.Column.render(self, value)
        else:
            return mark_safe("")   

class AccountTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_account record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_account %}?id={{ record.pk }}">elimina</a>
    '''
    TMP_GROUPS='''
        {{ record.groups.all.0 }}
    '''
    TMP_TEL='''
        {% if record.groups.all.0.name == "telefonista" %}
        <a href="{% url view_dipendente record.dipendente.pk %}">{{ record.dipendente }}</a>
        {% endif %}
    '''
    
    groups = tables.TemplateColumn(TMP_GROUPS, verbose_name="Gruppo")
    profile = tables.TemplateColumn(TMP_TEL, orderable=False, verbose_name="Profilo")
    is_active = BooleanColumn()
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = User
        exclude = ("id", "password", "is_staff", "is_superuser",)
        sequence = ("selection", "username", "first_name", "last_name", "email", 
                    "groups", "...")
        empty_text = "Nessun Account"
        attrs = {"class": "modeltable",}
    
class DipendenteTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_dipendente record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_dipendente %}?id={{ record.pk }}">elimina</a>
    '''
    TMP_ACCOUNT='''
        {% if record.account %}
        <a id="view_account_{{ record.pk }}" href="{% url view_account record.account.pk %}">{{ record.account }}</a>
        {% endif %}
    '''    
#    TMP_PRO='''
#        {{ record.provvigione }}{% if record.ruolo == "agt" %}% (x contratto){% else %}€ (x appuntamento){% endif %}
#    '''
    
#    attivo = BooleanColumn()  
    account = tables.TemplateColumn(TMP_ACCOUNT, orderable=False,)
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)    
    data_licenziamento = NullColumn()
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.Dipendente
        attrs = {"id": "modeltable"}
        exclude = ("id", "creazione", "modifica", "telefono", "cellulare",)
        empty_text = "Nessun Dipendente"
        sequence = ("selection", "...")
        order_by = ("cognome", "nome")
        attrs = {"class": "modeltable",}


class RetribuzioneTable(tables.Table):
    retribuzione = tables.Column(orderable=False, verbose_name="Retribuzioni")
    variazioni = tables.Column(orderable=False, verbose_name="Variazioni Temporanee")
    
    class Meta:
        empty_text = "Tabella vuota" 

class ClienteTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_cliente record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_cliente %}?id={{ record.pk }}">elimina</a>
    '''
    
    blindato = BooleanColumn()    
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.Cliente
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica", "nota", "indirizzo", "telefono", "cellulare", "fax",)
        empty_text = "Nessun Cliente"
        sequence = ("selection", "...")
        order_by = ("denominazione", "cognome")

class TipologiaTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "tipologia" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "tipologia" %}?id={{ record.pk }}">elimina</a>
    '''
    
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"class": "modeltable",}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class FasciaTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "fascia" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "fascia" %}?id={{ record.pk }}">elimina</a>
    '''

    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"class": "modeltable",}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class ServizioTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "servizio" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "servizio" %}?id={{ record.pk }}">elimina</a>
    '''

    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"class": "modeltable",}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class TariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_tariffa record.pk %}">visualizza</a>
        {% if user|get_group == "amministratore" %}
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_tariffa %}?id={{ record.pk }}">elimina</a>
        {% endif %}
    '''
    
    tipo = NullColumn()
    fascia = NullColumn()
    servizio = NullColumn()
    attivo = BooleanColumn()
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.Tariffa
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica",)
        empty_text = "Nessuna Tariffa"
        sequence = ("selection", "gestore", "profilo", "tipo", "fascia", "servizio","...",)
        order_by = ("gestore", "profilo", "fascia",)

class AppuntamentoTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_appuntamento record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_appuntamento %}?id={{ record.pk }}">elimina</a>
    '''
    
    TMP_REF='''
       {% if record.referente %}<a href="{% url view_referente record.pk record.referente.pk %}">{{ record.referente }}</a>{% endif %} 
    '''
    
    TMP_AGT='''
       {% if record.agente %}<a href="{% url view_dipendente record.agente.pk %}">{{ record.agente }}</a>{% endif %} 
    '''    
    
    TMP_CONTRATTO='''
        {% load tags %}
        <table>
            {% for obj in record.contratto_set.all %}
            <tr>
                <td><a href="{% url view_contratto obj.pk %}">{{ obj }}</a></td>
            </tr>
            {% endfor %}
        </table>
    '''
        
    cliente = tables.LinkColumn("view_cliente", args=[A("cliente.pk")],)
    telefonista = tables.LinkColumn("view_dipendente", args=[A("telefonista.pk")])
    agente = tables.TemplateColumn(TMP_AGT)
    referente = tables.TemplateColumn(TMP_REF)
    richiamare = BooleanColumn()
    data_richiamare = NullColumn()
    contratto = tables.TemplateColumn(TMP_CONTRATTO, orderable=False)
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.Appuntamento
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica", "num_sim", "gestore_mob",
                   "gestore_fisso", "nota", "data_assegnazione", "nota_esito")
        sequence = ("selection", "data", "cliente", "...")
        empty_text = "Nessuna Appuntamento"
        order_by = ("-data",)

class ContrattoTable(tables.Table):
    TMP_PT='''
        {% load tags %}
        <table>            
            {% for pt in record|get_pt %}
            <tr>
                <td><a href="{% url view_tariffa pt|get_pt_tariffa_pk %}">{{ pt|get_pt_tariffa }}</a>({{ pt.num }}) {% if pt.opzione %}[opzione]{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
    '''
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_contratto record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_contratto %}?id={{ record.pk }}">elimina</a>
    '''
    
    cliente = tables.LinkColumn("view_cliente", args=[A("cliente.pk")],)
    agente = tables.LinkColumn("view_dipendente", args=[A("agente.pk")])
    piano_tariffario = tables.TemplateColumn(TMP_PT, orderable=False, verbose_name="Piano tariffario")
    completo = BooleanColumn()
    inviato = BooleanColumn()
    caricato = BooleanColumn()
    rifiutato = BooleanColumn()
    attivato = BooleanColumn()
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    
    class Meta:
        model = models.Contratto
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica", "appuntamento", "pdf_contratto", "nota",
                   "data_rescissione", "data_completato", "data_inviato", "data_caricato", 
                   "data_rifiutato", "data_attivato", "vas_telefonista", "vas_agente",)
        sequence = ("selection", "cliente", "agente", "piano_tariffario", "...")
        empty_text = "Nessuna Contratto"
        order_by = ("-data_stipula", "-data_scadenza",)

#-------------------------------------------------------------------------------
# STATISTICHE

class CanvasTable(tables.Table):
    agente = tables.LinkColumn("view_dipendente", args=[A("agente.pk")])
    sim = tables.Column(verbose_name="SIM")
    dati_opz = tables.Column(verbose_name="Dati/OPZ")
    nip_ull = tables.Column(verbose_name="NIP/ULL")
    adsl = tables.Column(verbose_name="ADSL")
    punti_tim = tables.Column(verbose_name="Punti TIM")
    punti_telecom = tables.Column(verbose_name="Punti Telecom")
    tot_punti = tables.Column(verbose_name="TOT Punti")
    posizione = tables.Column(verbose_name="Posizione")
    
    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "reporttable"}
        template = "statistiche/canvas_table_snippet.html"

class CanvasEdisonTable(tables.Table):
    agente = tables.LinkColumn("view_dipendente", args=[A("agente.pk")])
    bus_en = tables.Column(verbose_name="Bus. Energia")
    pri_en = tables.Column(verbose_name="Res. Energia")
    bus_gas = tables.Column(verbose_name="Bus. Gas")
    pri_gas = tables.Column(verbose_name="Res. Gas")
    tot = tables.Column(verbose_name="Totale")
    posizione = tables.Column(verbose_name="Posizione")
    
    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "reporttable"}
        template = "statistiche/canvas_table_snippet.html"

class InOutTotalsTable(tables.Table): 
    TMP_DATA='''
        {% load tags %}
        <a href="{% url init_contratto %}?fdata_stipula=={{ record.data|get_date }}">{{ record.data }}</a>
    '''
    TMP_IN='''
        {% load tags %}
        {{ record.entrate.total|stringformat:".2f" }}€
        <a class="view_details" href="#"><img src="{{ STATIC_URL }}/img/destra.png" /></a>
        <p class="info">
            {% for gestore, total in record.entrate.details.iteritems %}
            <b>{{ gestore }}</b>: {{ total|stringformat:".2f" }}€<br />
            {% endfor %}
        </p>
    '''
    TMP_OUT='''
        {% load tags %}
        {{ record.uscite.total|stringformat:".2f" }}€
        <a class="view_details" href="#"><img src="{{ STATIC_URL }}/img/destra.png" /></a>
        <p class="info">
            {% for gestore, total in record.uscite.details.iteritems %}
            <b>{{ gestore }}</b>: {{ total|stringformat:".2f" }}€<br />
            {% endfor %}
        </p>
    '''
    TMP_TOT='''
        {% load tags %}
        {{ record.totali.total|stringformat:".2f" }}€
        <a class="view_details" href="#"><img src="{{ STATIC_URL }}/img/destra.png" /></a>
        <p class="info">
            {% for gestore, total in record.totali.details.iteritems %}
            <b>{{ gestore }}</b>: {{ total|stringformat:".2f" }}€<br />
            {% endfor %}
        </p>
    '''
    
    data = tables.TemplateColumn(TMP_DATA)
    n_stipulati = tables.Column(verbose_name="S/Co/I/C/A", orderable=False,
                                attrs=tables.Attrs(th={"title": "stipulati/completati/inviati/caricati/attivati"}))
    entrate = tables.TemplateColumn(TMP_IN, accessor="record.entrate.total")
    uscite = tables.TemplateColumn(TMP_OUT, accessor="record.uscite.total")
    totali = tables.TemplateColumn(TMP_TOT, accessor="record.totali.total")

    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "totalitable"}
        template = "statistiche/totali_table_snippet.html"

class InTable(tables.Table):
#    TMP_N_STIP='''
#        {{ record.stip }}/{{ record.inv }}/{{ record.car }}/{{ record.att }}
#    '''
#    
#    TMP_IN='''
#        {{ record.stip_in }}/{{ record.att_in }}
#    '''    
    TMP_DATA='''
        {% load tags %}
        <a href="{% url init_contratto %}?fdata_stipula=={{ record.data|get_date }}">{{ record.data }}</a>
    '''
    TMP_IN='''
        {% load tags %}
        {{ record.entrate.total|stringformat:".2f" }}€
        <a class="view_details" href="#"><img src="{{ STATIC_URL }}/img/destra.png" /></a>
        <p class="info">
            {% for gestore, total in record.entrate.details.iteritems %}
            <b>{{ gestore }}</b>: {{ total|stringformat:".2f" }}€<br />
            {% endfor %}
        </p>
    '''
    
    data = tables.TemplateColumn(TMP_DATA)
    n_stipulati = tables.Column(verbose_name="S/Co/I/C/A", orderable=False)
    entrate = tables.TemplateColumn(TMP_IN, accessor="record.entrate.total")
    
    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "entratetable"}
        template = "statistiche/entrate_table_snippet.html"

class OutTable(tables.Table):
    TMP_DATA='''
        {% load tags %}
        <a href="{% url init_contratto %}?fdata_stipula=={{ record.data|get_date }}">{{ record.data }}</a>
    '''
    TMP_OUT='''
        {% load tags %}
        {{ record.uscite.total|stringformat:".2f" }}€
        <a class="view_details" href="#"><img src="{{ STATIC_URL }}/img/destra.png" /></a>
        <p class="info">
            {% for gestore, total in record.uscite.details.iteritems %}
            <b>{{ gestore }}</b>: {{ total|stringformat:".2f" }}€<br />
            {% endfor %}
        </p>
    '''
    
    data = tables.TemplateColumn(TMP_DATA)
    n_stipulati = tables.Column(verbose_name="S/Co/I/C/A", orderable=False)
    prov_agt = tables.Column(verbose_name="Prov. agente")
    prov_bonus_agt = tables.Column(verbose_name="Prov. bonus agente")
    prov_tel = tables.Column(verbose_name="Prov. tel.")
    prov_bonus_tel = tables.Column(verbose_name="Prov. bonus tel.")
    uscite = tables.TemplateColumn(TMP_OUT, accessor="record.uscite.total")
    
    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "uscitetable"}
        template = "statistiche/uscite_table_snippet.html"
         
class ObiettivoTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_obiettivo_trimestrale record.pk %}">visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_obiettivo_trimestrale %}?id={{ record.pk }}">elimina</a>
    '''
    
    data_fine = NullColumn()
    operazioni = tables.TemplateColumn(TMP_OP, orderable=False)
    selection = tables.CheckBoxColumn(accessor=A('pk'),
                                      attrs=tables.Attrs({"class": "selection"}), 
                                      orderable=False,)
    
    class Meta:
        model = models.Obiettivo
        sequence = ("selection", "...", )
        exclude = ("id", "creazione", "modifica",)

class AppuntamentoReportTable(tables.Table):
    TMP_REF='''
       {% if record.referente %}<a href="{% url view_referente record.pk record.referente.pk %}">{{ record.referente }}</a>{% endif %} 
    '''
    
    TMP_AGT='''
       {% if record.agente %}<a href="{% url view_dipendente record.agente.pk %}">{{ record.agente }}</a>{% endif %} 
    '''    
    
    TMP_CONTRATTO='''
        {% load tags %}
        <table>
            {% for obj in record.contratto_set.all %}
            <tr>
                <td><a href="{% url view_contratto obj.pk %}">{{ obj }}</a></td>
            </tr>
            {% endfor %}
        </table>
    '''
        
    cliente = tables.LinkColumn("view_cliente", args=[A("cliente.pk")],)
    telefonista = tables.LinkColumn("view_dipendente", args=[A("telefonista.pk")])
    agente = tables.TemplateColumn(TMP_AGT)
    referente = tables.TemplateColumn(TMP_REF)
    richiamare = BooleanColumn()
    contratto = tables.TemplateColumn(TMP_CONTRATTO, orderable=False)
    
    class Meta:
        model = models.Appuntamento
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica", "num_sim", "gestore_mob",
                   "gestore_fisso", "nota", "data_assegnazione", "nota_esito")
        sequence = ("data", "cliente", "...")
        empty_text = "Nessuna Appuntamento"
   
class ContrattoReportTable(tables.Table):
    TMP_PT='''
        {% load tags %}
        <table>            
            {% for pt in record|get_pt %}
            <tr>
                <td><a href="{% url view_tariffa pt|get_pt_tariffa_pk %}">{{ pt|get_pt_tariffa }}</a>({{ pt.num }}) {% if pt.opzione %}[opzione]{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
    '''
    
    cliente = tables.LinkColumn("view_cliente", args=[A("cliente.pk")],)
    agente = tables.LinkColumn("view_dipendente", args=[A("agente.pk")])
    piano_tariffario = tables.TemplateColumn(TMP_PT, orderable=False, verbose_name="Piano tariffario")
    completo = BooleanColumn()
    inviato = BooleanColumn()
    caricato = BooleanColumn()
    attivato = BooleanColumn()
    
    class Meta:
        model = models.Contratto
        attrs = {"class": "modeltable",}
        exclude = ("id", "creazione", "modifica", "appuntamento", "pdf_contratto", "nota",
                   "data_rescissione", "data_completato", "data_inviato", "data_caricato", 
                   "data_attivato", "vas_telefonista", "vas_agente",)
        sequence = ("cliente", "agente", "piano_tariffario", "...")
        empty_text = "Nessuna Contratto"
