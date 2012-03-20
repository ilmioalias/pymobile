# -*- coding: utf-8 -*-

from django.db.models import Q
import operator
from datetime import datetime, timedelta, date
import calendar
import tables
import forms
import django_tables2.tables as dt2
import django.forms.models as dfm

def filter_objs(objs, query):
    filters = []
    
    for k in query.keys():
        if k.startswith('f'):
            values = query.getlist(k)
            if values:
                field = k[1:]
                filters.append((field, values))
    
    # Apply keyword searches.
    def get_search(field_name, bit):
        if bit.startswith('^'):
            orm_lookup = "{}__istartswith".format(field_name)
            query = {orm_lookup: bit[1:]}
            return Q(**query)
        elif bit.startswith('='):
            orm_lookup = "{}".format(field_name)
            if "data" in field_name:
                d = datetime.strptime(bit[1:], '%d/%m/%Y')
            else:
                d = bit[1:]
            query = {orm_lookup: d}
            return Q(**query)
        elif bit.startswith('!'):
            orm_lookup = "{}".format(field_name)
            query = {orm_lookup: bit[1:]}
            return ~Q(**query)        
        elif bit.startswith('@'):
            orm_lookup = "{}__search".format(field_name)
            query = {orm_lookup: bit[1:]}
            return Q(**query)
        elif bit.startswith('>'):
            orm_lookup = "{}__gte".format(field_name)
            if "data" in field_name:
                d = datetime.strptime(bit[1:], '%d/%m/%Y')
            else:
                d = bit[1:]
            query = {orm_lookup: d}
            return Q(**query)
        elif bit.startswith('<'):
            orm_lookup = "{}__lte".format(field_name)
            if "data" in field_name:
                d = datetime.strptime(bit[1:], '%d/%m/%Y')
            else:
                d = bit[1:]
            query = {orm_lookup:d}
            return Q(**query)            
        else:
            orm_lookup = "%s__icontains" % field_name
            query = {orm_lookup: bit}
            return Q(**query)
        
    initial = {}
    if filters:
        for fltr in filters:
            field_name = fltr[0]
            values = fltr[1]
            queries = [get_search(str(field_name), value) for value in values]
            objs = objs.filter(reduce(operator.and_, queries))
            # per le chiavi esterne determiniamo il valore inziale, la richiesta 
            # potrebbe provenire da un'altra pagina
            # FIXME: sta cosa del valore iniziale va assolutamente ripensata 
            if field_name in ("tariffa", "piano_tariffario", "cliente", "contratto", 
                              "agente", "dipendente", "gestore",): 
                initial[field_name] = values[0][1:]
    
    return objs, initial

def get_current_quarter():
    now = datetime.now()
    y = now.year
    m = now.month
    
    q = [(str(y) + "-1-1", str(y) + "-3-31" ),
         (str(y) + "-4-1", str(y) + "-6-30"),
         (str(y) + "-7-1", str(y) + "-9-30"),
         (str(y) + "-10-1", str(y) + "-12-31")]

    if 1 <= m <= 3:
        return (datetime.strptime(q[0][0], "%Y-%m-%d").date(),
                datetime.strptime(q[0][1], "%Y-%m-%d").date())
    elif 4 <= m <= 6:
        return (datetime.strptime(q[1][0], "%Y-%m-%d").date(),
                datetime.strptime(q[1][1], "%Y-%m-%d").date())
    elif 7 <= m <= 9:
        return (datetime.strptime(q[2][0], "%Y-%m-%d").date(),
                datetime.strptime(q[2][1], "%Y-%m-%d").date())
    elif 10 <= m <= 12:
        return (datetime.strptime(q[3][0], "%Y-%m-%d").date(),
                datetime.strptime(q[3][1], "%Y-%m-%d").date())

def get_current_year():
    now = datetime.now()
    y = now.year
    return (date(y, 1, 1), date(y, 12, 31))
#    return (str(y) + "-1-1", str(y) + "-12-31")

def get_current_month():
    now = datetime.now()
    r = calendar.monthrange(now.year, now.month)
    a = date(now.year, now.month, 1)
    b = date(now.year, now.month, r[1]) 
    
    return (a, b)

def get_current_week():
    now = datetime.now()
    dw = now.weekday()
    a = (now - timedelta(dw)).date()
    b = (now + timedelta(6-dw)).date()
    
    return (a, b)

def get_current_day():
    d = datetime.today().date()
    return (d, d)

def get_yesterday():
    d = (datetime.today() - timedelta(1)).date()
    return (d, d)

def get_quarter(query):
    y = int(query["fanno"][1:])
    quarter = int(query["fquarto"][1:])
    
    q = [(str(y) + "-1-1", str(y) + "-3-31" ),
         (str(y) + "-4-1", str(y) + "-6-30"),
         (str(y) + "-7-1", str(y) + "-9-30"),
         (str(y) + "-10-1", str(y) + "-12-31")]

    if quarter == 1:
        return (datetime.strptime(q[0][0], "%Y-%m-%d").date(),
                datetime.strptime(q[0][1], "%Y-%m-%d").date())
    elif quarter == 2:
        return (datetime.strptime(q[1][0], "%Y-%m-%d").date(),
                datetime.strptime(q[1][1], "%Y-%m-%d").date())
    elif quarter == 3:
        return (datetime.strptime(q[2][0], "%Y-%m-%d").date(),
                datetime.strptime(q[2][1], "%Y-%m-%d").date())
    elif quarter == 4:
        return (datetime.strptime(q[3][0], "%Y-%m-%d").date(),
                datetime.strptime(q[3][1], "%Y-%m-%d").date())
    
def get_period(query):
    period = (date(2012, 1, 1), datetime.now())
#    period = ("2012-1-1", datetime.now().strftime("%Y-%m-%d"))
    
    if query["fperiodo"] == "=today":
        period = get_current_day()
    elif query["fperiodo"] == "=yesterday":
        period = get_yesterday()
    elif query["fperiodo"] == "=week":
        period = get_current_week()
    elif query["fperiodo"] == "=month":
        period = get_current_month()
    elif query["fperiodo"] == "=quarter":
        period = get_current_quarter()
    elif query["fperiodo"] == "=year":
        period = get_current_year()
    elif query["fperiodo"] == "=manual":
        # data "a" farloccha, "b" data odierna
        if query.has_key("fdata"):
            a = date(2012, 1, 1)
            b = datetime.now().date()
            for data in query.getlist("fdata"):
                if data.startswith(">"):
                    a = datetime.strptime(data[1:], "%d/%m/%Y").date()
                elif data.startswith("<"):
                    b = datetime.strptime(data[1:], "%d/%m/%Y").date()
                period = (a, b)
        else:
            period = get_current_quarter()

    return period

def get_agenti_ids(query):
    ids = [agente[1:] for agente in query.getlist("fagente")]
    
    return ids

def get_telefonisti_ids(query):
    ids = [tel[1:] for tel in query.getlist("ftelefonista")]
    
    return ids   

def values_from_provvigione_bonus(provvigione_bonus):
    provvigione_bonus = provvigione_bonus.strip()
    if not provvigione_bonus:
        return []
    
    values = []
    vs = provvigione_bonus.split(";")
    for var in vs:
        if var:
            opts = var.split(",")
            par = {}
            prov = None
            for opt in opts:
                item = opt.split(":")
            
                if len(item) == 2:
                    k = item[0].strip()
                    v = item[1].strip()
                    if k == "provvigione":
                        prov = float(v)                        
                    elif k == "blindato":
                        par[k] = int(v)
                    else:
                        par[k] = v
            
            d = {"parameters": par, "provvigione": prov}            
            values.append(d)
            
    return values    

def provvigione_bonus_from_values(values):
    if not values:
        return
    
    provvigione_bonus = ""
    for d in values:
        if d:
            for k, v in d["parameters"].iteritems():
                provvigione_bonus += str(k) + ":" + str(v) + ","
            provvigione_bonus += str(d["provvigione"]) + ";"

    return provvigione_bonus  

def values_from_parametri(parametri):
    parametri = parametri.strip()
    if not parametri:
        return []
    
    parametri = parametri.split(",")
    for parametro in parametri:
        opts = parametro.split(":")
        par = {}
        
        if len(opts) == 2:
            k = opts[0].strip()
            v = opts[1].strip()
            par[k] = v
            
        d = {"parameters": par}            
            
    return d   

def parametri_from_values(values):
    if not values:
        return
    
    parametri = ""
    for d in values:
        if d:
            for k, v in d["parameters"].iteritems():
                parametri += str(k) + ":" + str(v) + ","
            parametri = parametri[:-1]
            
    return parametri

def get_table(table_name):
    for k, v in tables.__dict__.iteritems():
        if k.lower() == table_name.lower():
            if isinstance(v, dt2.DeclarativeColumnsMetaclass):
                return v
    raise LookupError("Non esiste la tabella con nome '{}'".format(table_name))
        
def get_form(form_name):
    for k, v in forms.__dict__.iteritems():
        if k.lower() == form_name.lower():
            if isinstance(v, dfm.ModelFormMetaclass):
                return v
    raise LookupError("Non esiste il form con nome '{}'".format(form_name))

def is_telefonista(user):
    if user:
        if user.groups.filter(name="telefonista").count() > 0:
            return True
    return False
    