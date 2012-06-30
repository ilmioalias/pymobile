# -*- coding: utf-8 -*-

'''
Created on 03/dic/2011

@author: luigi
'''

from django import template
from pymobile.administration import models
import calendar
import locale

locale.setlocale(locale.LC_ALL, "it_IT.utf8")

register = template.Library()

@register.filter(name="isfk")
def isfk(field):
    try: 
        if field.field.widget.attrs.has_key("class"):
            v = field.field.widget.attrs["class"]
            clss = v.split(" ")
            if "fk" in clss:
                return True
            return False
    except NameError: 
        return

@register.filter(name="isdate")
def isdate(field):
    try: 
        if field.field.widget.attrs.has_key("class"):
            v = field.field.widget.attrs["class"]
            clss = v.split(" ")
            if ("date" in clss or "datetime" in clss
                or "date_start" in clss or "date_end" in clss):
                return True
            return False
    except NameError: 
        return


@register.filter(name="to_hide")
def to_hide(field):
    try: 
        if field.field.widget.attrs.has_key("class"):
            v = field.field.widget.attrs["class"]
            clss = v.split(" ")
            if "hidden" in clss:
                return True
            return False
    except NameError: 
        return

@register.filter(name="get_class_name")
def get_class_name(record):
    return record.__class__.__name__.lower()


@register.filter(name="get_pt")
def get_pt(contratto):
    pt = models.PianoTariffario.objects.filter(contratto=contratto)
    return pt

@register.filter(name="get_pt_dati")
def get_pt_dati(piano_tariffario):
    dati = models.DatoPianoTariffario.objects.filter(piano_tariffario=piano_tariffario)
    return dati

@register.filter(name="get_pt_tariffa")
def get_pt_tariffa(pk):
    tariffa = models.Tariffa.objects.get(pianotariffario=pk)
    return tariffa

@register.filter(name="get_pt_tariffa_pk")
def get_pt_tariffa_pk(pk):
    tariffa = models.Tariffa.objects.get(pianotariffario=pk)
    return tariffa.pk

@register.filter(name="get_month_name")
def get_month_name(month_num):
    month_name = calendar.month_name[month_num]
    return month_name

@register.filter(name="get_prov")
def get_prov(objs, i):
    return objs.get(i, "")

@register.filter(name="get_date")
def get_date(date):
    return date.strftime("%d/%m/%Y")

@register.filter(name="get_data")
def get_data(d, obiettivo):
    key = obiettivo.denominazione
    if d.has_key(key):
        return d[key]["data"]
    else:
        return ""
    
@register.filter(name="get_contratti")
def get_contratti(d, obiettivo):
    if isinstance(obiettivo, str) or isinstance(obiettivo, unicode):
        key = obiettivo
    else:
        key = obiettivo.denominazione
    if d.has_key(key):
        return d[key]["contratti"]
    else:
        return ""

@register.filter(name="get_punteggio")
def get_punteggio(d, obiettivo):
    if isinstance(obiettivo, str) or isinstance(obiettivo, unicode):
        key = obiettivo
    else:
        key = obiettivo.denominazione
    if d.has_key(key):
        return d[key]["punteggio"]
    else:
        return ""
    
@register.filter(name="get_msg")
def get_msg(d, obiettivo):
    if isinstance(obiettivo, str) or isinstance(obiettivo, unicode):
        key = obiettivo
    else:
        key = obiettivo.denominazione
    if d.has_key(key):
        return d[key]["msg"]
    else:
        return ""

@register.filter(name="get_group")
def get_group(user):
    if user:
        return user.groups.all()[0].name
    else:
        return ""

@register.filter(name="get_pdf")
def get_pdf(contratto):
    if contratto:
        return contratto.pdf_contratto
    else:
        return ""

@register.filter(name="get_cliente_app")
def get_cliente_app(cliente):
    if cliente:
        return cliente.__unicode__()
    else:
        return ""

@register.filter(name="get_referente")
def get_referente(referente):
    if referente:
        return referente.__unicode__()
    else:
        return ""

@register.filter(name="get_formset")
def get_formset(formsets, k):
    return formsets[int(k)]
