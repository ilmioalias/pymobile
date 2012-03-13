# -*- coding: utf-8 -*-

'''
Created on 27/nov/2011

@author: luigi
'''

import django_tables2 as tables
from django_tables2.utils import A
import pymobile.administration.models as models
from django.utils.safestring import mark_safe
from django.conf import settings


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

class DipendenteTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_dipendente record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_dipendente %}?id={{ record.pk }}">Elimina</a>
    '''    
#    TMP_PRO='''
#        {{ record.provvigione }}{% if record.ruolo == "agt" %}% (x contratto){% else %}€ (x appuntamento){% endif %}
#    '''
    
#    attivo = BooleanColumn()  
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    data_licenziamento = NullColumn()
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.Dipendente
        attrs = {"id": "modeltable"}
        exclude = ("id", "creazione", "modifica", "telefono", "cellulare",)
        empty_text = "Nessun Dipendente"
        sequence = ("selection", "...")
        order_by = ("cognome", "nome")

#class RetribuzioneTable(tables.Table):
#    TMP_DATA='''
#        {% if record.data_fine != record.data_inizio %}{{ record.data_fine }}</br></br></br>{% endif %}{{ record.data_inizio }} 
#    '''
#    
#    TMP_FISSO='''
#        {% if record.fisso %}{{ record.fisso }}&euro;{% endif %}
#    '''
#
#    TMP_PROV='''
#        {% if record.provvigione_contratto %}
#        {{ record.fisso }}&euro;{% endif %}
#    '''
#        
#    TMP_OP='''
#        {% if record.tipo == "operazioni" %}
#            <a class="addrow" href="{% url add_vartmp record.dipendente_id %}?data_inizio={{ record.d_inizio }}{% if record.d_fine %}&data_fine={{ record.d_fine }}{% endif %}">aggiungi variazione temporanea</a></br>
#            <a class="addrow" href="{% url add_retribuzione record.dipendente_id %}?data_inizio={{ record.d_inizio }}{% if record.d_fine %}&data_fine={{ record.d_fine }}{% endif %}">aggiungi variazione retribuzione</a>
#        {% else %}
#            {% if record.variazione %}
#                <a class="modifyrow" href="{% url mod_vartmp record.dipendente_id record.id %}">modifica</a>
#                <a class="deleterow" href="{% url del_vartmp record.dipendente_id %}?id={{ record.id }}">elimina</a>
#            {% else %}
#                <a class="modifyrow" href="{% url mod_retribuzione record.dipendente_id record.id %}">modifica</a>
#                <a class="deleterow" href="{% url del_retribuzione record.dipendente_id %}?id={{ record.id }}">elimina</a>
#            {% endif %}
#        {% endif %}         
#    '''
#    
#    data = tables.TemplateColumn(TMP_DATA, sortable=False, verbose_name="Periodi")
#    fisso = tables.TemplateColumn(TMP_FISSO, sortable=False)
#    provvigione_contratto = tables.Column(sortable=False, verbose_name="Prov. x contratto")
#    provvigione_bonus = tables.Column(sortable=False, verbose_name="Prov. bonus")
#    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
#    
#    class Meta:
#        empty_text = "Tabella vuota" 

class RetribuzioneTable(tables.Table):
    retribuzione = tables.Column(sortable=False, verbose_name="Retribuzioni")
    variazioni = tables.Column(sortable=False, verbose_name="Variazioni Temporanee")
    
    class Meta:
        empty_text = "Tabella vuota" 

class ClienteTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_cliente record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_cliente %}?id={{ record.pk }}">Elimina</a>
    '''
    
    blindato = BooleanColumn()    
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.Cliente
        attrs = {"id": "modeltable"}
        exclude = ("id", "creazione", "modifica", "nota", "indirizzo", "telefono", "cellulare", "fax",)
        empty_text = "Nessun Cliente"
        sequence = ("selection", "...")
        order_by = ("denominazione", "cognome")

class TipologiaTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "tipologia" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "tipologia" %}?id={{ record.pk }}">Elimina</a>
    '''
    
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"id": "modeltable"}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class FasciaTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "fascia" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "fascia" %}?id={{ record.pk }}">Elimina</a>
    '''

    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"id": "modeltable"}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class ServizioTariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="mod_id_{{ record.pk }}" class="modifyrow" href="{% url mod_attribute "servizio" record.pk %}">Modifica</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_attribute "servizio" %}?id={{ record.pk }}">Elimina</a>
    '''

    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.TipologiaTariffa
        attrs = {"id": "modeltable"}
        exclude = ("id",)
        empty_text = "Nessuna Tipologia"
        sequence = ("selection", "...")
        order_by = ("gestore", "denominazione")

class TariffaTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_tariffa record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_tariffa %}?id={{ record.pk }}">Elimina</a>
    '''
    
    tipo = NullColumn()
    fascia = NullColumn()
    servizio = NullColumn()
    attivo = BooleanColumn()
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.Tariffa
        attrs = {"id": "modeltable"}
        exclude = ("id", "creazione", "modifica",)
        empty_text = "Nessuna Tariffa"
        sequence = ("selection", "gestore", "profilo", "tipo", "fascia", "servizio","...",)
        order_by = ("gestore", "profilo", "fascia",)

class AppuntamentoTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_appuntamento record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_appuntamento %}?id={{ record.pk }}">Elimina</a>
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
        
    cliente = tables.LinkColumn("view_cliente", args=[A("pk")],)
    telefonista = tables.LinkColumn("view_dipendente", args=[A("pk")])
    agente = tables.TemplateColumn(TMP_AGT)
    referente = tables.TemplateColumn(TMP_REF)
    richiamare = BooleanColumn()
    contratto = tables.TemplateColumn(TMP_CONTRATTO, sortable=False)
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.Appuntamento
        attrs = {"id": "modeltable"}
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
        <a id="view_id_{{ record.pk }}" href="{% url view_contratto record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_contratto %}?id={{ record.pk }}">Elimina</a>
    '''
    
    cliente = tables.LinkColumn("view_cliente", args=[A("cliente.pk")],)
    agente = tables.LinkColumn("view_dipendente", args=[A("agente.pk")])
    piano_tariffario = tables.TemplateColumn(TMP_PT, sortable=False, verbose_name="Piano tariffario")
    completo = BooleanColumn()
    inviato = BooleanColumn()
    caricato = BooleanColumn()
    attivato = BooleanColumn()
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    
    class Meta:
        model = models.Contratto
        attrs = {"id": "modeltable"}
        exclude = ("id", "creazione", "modifica", "appuntamento", "pdf_contratto", "nota",
                   "data_rescissione", "data_completato", "data_inviato", "data_caricato", 
                   "data_attivato", "vas_telefonista", "vas_agente",)
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
    
    data = tables.TemplateColumn(TMP_DATA)
    n_stipulati = tables.Column(verbose_name="Stipulati")
    entrate = tables.Column()

    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "entratetable"}

class OutTable(tables.Table):
    TMP_DATA='''
        {% load tags %}
        <a href="{% url init_contratto %}?fdata_stipula=={{ record.data|get_date }}">{{ record.data }}</a>
    '''
    
    data = tables.TemplateColumn(TMP_DATA)
    n_stipulati = tables.Column(verbose_name="Stipulati")
    prov_agt = tables.Column(verbose_name="Prov. agente")
    prov_bonus_agt = tables.Column(verbose_name="Prov. bonus agente")
    prov_tel = tables.Column(verbose_name="Prov. tel.")
    prov_bonus_tel = tables.Column(verbose_name="Prov. bonus tel.")
    uscite = tables.Column()
    
    class Meta:
        empty_text = "Tabella vuota"
        attrs = {"id": "uscitetable"}

class ObiettivoTable(tables.Table):
    TMP_OP='''
        {% load tags %}
        <a id="view_id_{{ record.pk }}" href="{% url view_obiettivo_trimestrale record.pk %}">Visualizza</a>
        <a id="del_id_{{ record.pk }}" class="deleterow" href="{% url del_obiettivo_trimestrale %}?id={{ record.pk }}">Elimina</a>
    '''
    
    data_fine = NullColumn()
    operazioni = tables.TemplateColumn(TMP_OP, sortable=False)
    selection = tables.CheckBoxColumn(accessor=A('pk'), attrs={"class": "selection"}, 
                                      header_attrs={"class": "selection_header"},
                                      sortable=False,)
    
    class Meta:
        model = models.Obiettivo
        sequence = ("selection", "...", )
        exclude = ("id", "creazione", "modifica",)
