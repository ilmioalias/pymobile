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


@register.filter(name="get_pt_num")
def get_pt_num(tariffa, contratto):
    pt = models.PianoTariffario.objects.get(contratto=contratto, tariffa=tariffa)
    return pt.num

@register.filter(name="get_pt_opt")
def get_pt_opt(tariffa, contratto):
    pt = models.PianoTariffario.objects.get(contratto=contratto, tariffa=tariffa)
    return pt.opzione

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
