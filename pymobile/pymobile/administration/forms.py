# -*- coding: utf-8 -*-

#FIXME: controllare tutti i field da localizzare

import pymobile.administration.models as models
from django import forms
from django.forms.models import inlineformset_factory
from datetime import datetime
import calendar
import operator
from django.db.models import Q
from django.db.models.loading import get_model
from django.forms.models import BaseInlineFormSet


#-------------------------------------------------------------------------------
# AMMINISTRAZIONE

class DipendenteForm(forms.ModelForm): 
    
    class Media:
        js = ("js/modelform.js", "js/modelform_dipendente.js")
    
    class Meta:
        model = models.Dipendente

class RetribuzioneForm(forms.ModelForm):
    data_inizio = forms.DateField(widget=forms.DateInput(format="%d/%m/%Y"), label="Data")
    
    def clean(self):
        cdata = self.cleaned_data
        if not self.instance.pk:
            data_inizio = cdata["data_inizio"]
            dipendente = cdata["dipendente"]
            if models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                            variazione=False,
                                                            data_inizio=data_inizio).exists():
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "Esiste già una variazione alla retribuzione assegnata in questa data <b>{}</b>".format(data_inizio.strftime("%d/%m/%Y"))
                self._errors["data_inizio"] = self.error_class([msg])
        else:
            data_inizio = cdata["data_inizio"]
            dipendente = cdata["dipendente"]
            if models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                            variazione=False,
                                                            data_inizio=data_inizio).exclude(pk=self.instance.pk).exists():
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "Esiste già una variazione alla retribuzione assegnata in questa data <b>{}</b>".format(data_inizio.strftime("%d/%m/%Y"))
                self._errors["data_inizio"] = self.error_class([msg])        
        return cdata
             
    def clean_provvigione_bonus(self):        
        cdata = self.cleaned_data
        provvigioni_bonus = cdata["provvigione_bonus"]
        
        if provvigioni_bonus:
            provvigioni_bonus = provvigioni_bonus.split(";")
            
            for provvigione_bonus in provvigioni_bonus:
                provvigione_bonus = provvigione_bonus.strip()
                if provvigione_bonus:
                    if ",provvigione:" not in provvigione_bonus.replace(" ", ""):
                        raise forms.ValidationError("in <b>{}</b> non è stata indicata la chiave obbligatoria <b>provvigione</b>".format(provvigione_bonus))
                        
                    # determiamo le opzioni scelte
                    opts = provvigione_bonus.split(",")
                    for opt in opts:
                        c = opt.split(":")
                        # chiave
                        k = c[0].strip()
                        # valore
                        v = c[1].strip()
                        if k != "provvigione":
                            # controlliamo le chiavi e i loro valori
                            if k == "gestore":
                                if not models.Gestore.objects.get(denominazione=v):
                                    raise forms.ValidationError("il gestore <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "profilo":
                                if not models.Tariffa.objects.get(profilo=v):
                                    raise forms.ValidationError("la tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "tipo":
                                if not models.TipologiaTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("il tipo di tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "fascia":
                                if not models.FasciaTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("la fascia <b>{}</b> non esiste nel DATABASE".format(v))   
                            elif k == "servizio":
                                if not models.ServizioTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("il servizio <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "blindato":
                                try:
                                    x = int(v)
                                    if v < 0:
                                        raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))
                                except : 
                                    raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))                                                 
                            else:
                                raise forms.ValidationError("la chiave <b>{}</b> non è ammessa".format(k))                                                                     
                        else:
                            try:
                                x = float(v)
                                if v < 0:
                                    raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve essere un numero maggiore o uguale di 0".format(v))                                             
                            except:
                                raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve un numero maggiore o uguale di 0".format(v))
            
        return cdata["provvigione_bonus"].strip()     
    
    class Media:
        js = ("js/modelform_retribuzione.js",)
    
    class Meta:
        model = models.RetribuzioneDipendente
        widgets = {"dipendente": forms.HiddenInput(),
                   "principale": forms.HiddenInput(),}
        exclude = ("data_fine", "variazione",)

RetribuzioneFormset = inlineformset_factory(models.Dipendente, 
                                            models.RetribuzioneDipendente, 
                                            RetribuzioneForm,
                                            extra=1,
                                            can_delete=False)
        
class VariazioneRetribuzioneForm(forms.ModelForm):

    def clean_provvigione_bonus(self):        
        cdata = self.cleaned_data
        provvigioni_bonus = cdata["provvigione_bonus"]
        
        if provvigioni_bonus:
            provvigioni_bonus = provvigioni_bonus.split(";")
            
            for provvigione_bonus in provvigioni_bonus:
                provvigione_bonus = provvigione_bonus.strip()
                if provvigione_bonus:
                    if ",provvigione:" not in provvigione_bonus.replace(" ", ""):
                        raise forms.ValidationError("in <b>{}</b> non è stata indicata la chiave obbligatoria <b>provvigione</b>".format(provvigione_bonus))
                        
                    # determiamo le opzioni scelte
                    opts = provvigione_bonus.split(",")
                    for opt in opts:
                        c = opt.split(":")
                        # chiave
                        k = c[0].strip()
                        # valore
                        v = c[1].strip()
                        if k != "provvigione":
                            # controlliamo le chiavi e i loro valori
                            if k == "gestore":
                                if not models.Gestore.objects.get(denominazione=v):
                                    raise forms.ValidationError("il gestore <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "profilo":
                                if not models.Tariffa.objects.get(profilo=v):
                                    raise forms.ValidationError("la tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "tipo":
                                if not models.TipologiaTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("il tipo di tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "fascia":
                                if not models.FasciaTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("la fascia <b>{}</b> non esiste nel DATABASE".format(v))   
                            elif k == "servizio":
                                if not models.ServizioTariffa.objects.get(denominazione=v):
                                    raise forms.ValidationError("il servizio <b>{}</b> non esiste nel DATABASE".format(v))
                            elif k == "blindato":
                                try:
                                    x = int(v)
                                    if v < 0:
                                        raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))
                                except : 
                                    raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))                                                 
                            else:
                                raise forms.ValidationError("la chiave <b>{}</b> non è ammessa".format(k))                                                                     
                        else:
                            try:
                                x = float(v)
                                if v < 0:
                                    raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve essere un numero maggiore o uguale di 0".format(v))                                             
                            except:
                                raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve un numero maggiore o uguale di 0".format(v)) 
        
        return cdata["provvigione_bonus"]   
    
    class Media:
        js = ("js/modelform.js", "js/modelform_retribuzione.js",)
    
    class Meta:
        model = models.RetribuzioneDipendente
        exclude = ("fisso",)
        widgets = {"dipendente": forms.HiddenInput(),
                   "data_inizio": forms.DateInput(format="%d/%m/%Y"),
                   "data_fine": forms.DateInput(format="%d/%m/%Y"),
                   "variazione": forms.HiddenInput(),
                   "principale": forms.HiddenInput(),}

class TelefonistaForm(DipendenteForm):
    
    class Meta(DipendenteForm.Meta):
        widgets = {"ruolo": forms.HiddenInput(attrs={"value": "tel"})}

class AgenteForm(DipendenteForm):
        
    class Meta(DipendenteForm.Meta):
        widgets = {"ruolo": forms.HiddenInput(attrs={"value": "agt"})}

class DipendenteFilterForm(forms.ModelForm):
    ATTIVO=((0, "No"), (1, "Sì"))
    
    ruolo = forms.MultipleChoiceField(choices=models.Dipendente.RUOLI,
                                      initial=["adm", "tel", "agt"],
                                      widget=forms.CheckboxSelectMultiple())
    attivo = forms.MultipleChoiceField(choices=ATTIVO,
                                       initial=[0, 1],
                                       widget=forms.CheckboxSelectMultiple()) 

    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.Dipendente
        exclude = ("provvigione_contratto", "provvigione_speciale", "fisso",)  

#class ProvvigioneForm(forms.ModelForm):
#    anno = forms.ChoiceField(initial=datetime.now().year)
#    mese = forms.ChoiceField(initial=datetime.now().month)
#
#    def __init__(self, *args, **kwargs):
#        forms.ModelForm.__init__(self, *args, **kwargs)
#        now = datetime.now()
#        self.fields["anno"].choices = [(y, y) for y in xrange(2012, now.year+1)]
#        self.fields["mese"].choices = [(m, calendar.month_name[m]) for m in xrange(1, 13)]
#        self.fields["mese"].localize = True
#        self.fields["mese"].widget.is_localized = True
#        self.fields["provvigione"].localize = True
#        self.fields["provvigione"].widget.is_localized = True
#    
#    def clean(self):
#        cdata = self.cleaned_data
#        y = cdata["anno"]
#        m = cdata["mese"]
#        cdata["data"] = datetime(y, m, 1)
#        
#        return cdata
#    
#    class Media:
#        js = ("js/modelform.js",)
#    
#    class Meta:
#        model = models.ProvvigioneDipendente
#        widgets = {"dipendente": forms.HiddenInput(),} 
#        fields = ("mese", "anno", "provvigione", "dipendente",)
#        exclude = ("data",)
        
class ClienteForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)    

    class Meta:
        model = models.Cliente

class ClienteFilterForm(forms.ModelForm):
    BLINDATO=((0, "No"), (1, "Sì"))
    
    tipo = forms.MultipleChoiceField(choices=models.Cliente.TIPI,
                                     initial=["bus", "pri"],
                                     widget=forms.CheckboxSelectMultiple())
    blindato = forms.MultipleChoiceField(choices=BLINDATO,
                                         initial=[0, 1],
                                         widget=forms.CheckboxSelectMultiple()) 

    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.Cliente
        exclude = ("nota", "telefono", "cellulare", "fax", "indirizzo",)

class TariffaForm(forms.ModelForm):   
    
    tipo_tim = forms.ModelChoiceField(queryset=models.TipologiaTariffa.objects.filter(gestore="tim"),
                                      widget=forms.Select(attrs={"class": "hidden tim fk"}),
                                      required=False)
    tipo_telecom = forms.ModelChoiceField(queryset=models.TipologiaTariffa.objects.filter(gestore="telecom"),
                                      widget=forms.Select(attrs={"class": "hidden telecom fk"}),
                                      required=False)
    tipo_edison = forms.ModelChoiceField(queryset=models.TipologiaTariffa.objects.filter(gestore="edison"),
                                      widget=forms.Select(attrs={"class": "hidden edison fk"}),
                                      required=False)
    
    fascia_tim = forms.ModelChoiceField(queryset=models.FasciaTariffa.objects.filter(gestore="tim"),
                                      widget=forms.Select(attrs={"class": "hidden tim fk"}),
                                      required=False)
    fascia_telecom = forms.ModelChoiceField(queryset=models.FasciaTariffa.objects.filter(gestore="telecom"),
                                      widget=forms.Select(attrs={"class": "hidden telecom fk"}),
                                      required=False)
    fascia_edison = forms.ModelChoiceField(queryset=models.FasciaTariffa.objects.filter(gestore="edison"),
                                      widget=forms.Select(attrs={"class": "hidden edison fk"}),
                                      required=False)    

    servizio_tim = forms.ModelChoiceField(queryset=models.ServizioTariffa.objects.filter(gestore="tim"),
                                      widget=forms.Select(attrs={"class": "hidden tim fk"}),
                                      required=False)
    servizio_telecom = forms.ModelChoiceField(queryset=models.ServizioTariffa.objects.filter(gestore="telecom"),
                                      widget=forms.Select(attrs={"class": "hidden telecom fk"}),
                                      required=False)
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        if kwargs.has_key("instance"): 
            instance = kwargs["instance"]
            
            if str(instance.gestore) == "tim":
                self.initial["tipo_tim"] = instance.tipo
                self.initial["fascia_tim"] = instance.fascia
                self.initial["servizio_tim"] = instance.servizio
            elif str(instance.gestore) == " telecom":
                self.initial["tipo_telecom"] = instance.tipo
                self.initial["fascia_telecom"] = instance.fascia
                self.initial["servizio_telecom"] = instance.servizio
            elif str(instance.gestore) == "edison":
                self.initial["tipo_edison"] = instance.tipo
                self.initial["fascia_edison"] = instance.fascia       
    
    def clean(self):
        cdata = self.cleaned_data
 
        if str(self.cleaned_data["gestore"]) == "tim":
            cdata["tipo"] = cdata["tipo_tim"]
            cdata["fascia"] = cdata["fascia_tim"]
            cdata["servizio"] = cdata["servizio_tim"]
        elif str(self.cleaned_data["gestore"]) == "telecom":
            cdata["tipo"] = cdata["tipo_telecom"]
            cdata["fascia"] = cdata["fascia_telecom"]
            cdata["servizio"] = cdata["servizio_telecom"]
        elif str(self.cleaned_data["gestore"]) == "edison":
            cdata["tipo"] = cdata["tipo_edison"]
            cdata["fascia"] = cdata["fascia_edison"]         
        
        return cdata
    
    class Media:
        js = ("js/modelform.js", "js/modelform_tariffa.js",)
    
    class Meta:
        model = models.Tariffa
#        widgets = {"sic": forms.TextInput(attrs={"class": "hidden edison"}),
#                   "sic_anni": forms.TextInput(attrs={"class": "hidden edison"}),}
        fields = ("gestore", "profilo", "tipo_tim", "fascia_tim", "servizio_tim", 
                  "tipo_telecom", "fascia_telecom", "servizio_telecom", 
                  "tipo_edison", "fascia_edison", "sac", "attivo", "punteggio",)
        

class TariffaFilterForm(forms.ModelForm):
    ATTIVO=((0, "No"), (1, "Sì"))
    
    gestore = forms.ModelChoiceField(queryset=models.Gestore.objects.all(), 
                                     required=False)
    attivo = forms.MultipleChoiceField(choices=ATTIVO,
                                       initial=[0, 1],
                                       widget=forms.CheckboxSelectMultiple()) 

    class Media:
        js = ("js/filterform.js",)
      
    class Meta:
        model = models.Tariffa
        exclude = ("punteggio", "sac",)

class TipologiaTariffaForm(forms.ModelForm):
    
    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.TipologiaTariffa
   
class FasciaTariffaForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.FasciaTariffa

class ServizioTariffaForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.ServizioTariffa

class AppuntamentoForm(forms.ModelForm):           

    class Media:
        js = ("js/modelform.js",)

    class Meta:
        model = models.Appuntamento
        widgets = {"telefonista": forms.Select(attrs={"class": "fk", }),
                   "cliente": forms.Select(attrs={"class": "fk", }),
                   "referente": forms.Select(attrs={"class": "fk", }),
                   "agente": forms.Select(attrs={"class": "fk", }),
                   "data": forms.DateTimeInput(format="%d/%m/%Y %H:%M", attrs={"class": "datetime",}),}       

class AppuntamentoFilterForm(forms.ModelForm):
    
    # FIXME: aggiungere tasto mail dopo assegnazione
    RICHIAMARE=((0, "No"), (1, "Sì"))  
    richiamare = forms.MultipleChoiceField(choices=RICHIAMARE, 
                                           label="Da richiamare",
                                           initial=[0, 1],
                                           widget=forms.CheckboxSelectMultiple())
    telefonista = forms.ModelChoiceField(queryset=models.Dipendente.objects.filter(ruolo="tel"))
    agente = forms.ModelChoiceField(queryset=models.Dipendente.objects.filter(ruolo="agt"))
    
    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.Appuntamento
        fields = ("cliente", "telefonista", "agente", "richiamare")

class ReferenteForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.Referente

class PianoTariffarioForm(forms.ModelForm): 

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.PianoTariffario
        widgets = {"tariffa": forms.Select(attrs={"class": "fk"})}


PianoTariffarioFormSet = inlineformset_factory(models.Contratto, 
                                               models.PianoTariffario, 
                                               PianoTariffarioForm,
                                               extra=1)

class ContrattoForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js", "js/modelform_contratto.js",)
    
    def clean(self):
        cdata = self.cleaned_data
        data_stipula = cdata.get("data_stipula")
        data_scadenza = cdata.get("data_scadenza") 
        data_rescissione = cdata.get("data_rescissione")
        
        if data_scadenza <= data_stipula:
            raise forms.ValidationError('La data di scadenza è precedente alla data di stiupula.')    
        
        if data_rescissione:
            if data_rescissione <= data_stipula or data_rescissione >= data_scadenza:
                raise forms.ValidationError('''
                        La data di rescissione è precedente alla data di stiupula o
                        successiva alla data di scadenza.
                    ''')
        
        return cdata      
    
    class Meta:
        model = models.Contratto
        exclude = ("piano_tariffario",)
        widgets = {"cliente": forms.Select(attrs={"class": "fk"}),
                   "agente": forms.Select(attrs={"class": "fk"}),
                   "data_stipula": forms.DateInput(format="%d/%m/%Y", attrs={"class": "date",}),
                   "data_scadenza": forms.DateInput(format="%d/%m/%Y", attrs={"class": "date",}),
                   "data_rescissione": forms.DateInput(format="%d/%m/%Y", attrs={"class": "date",}),}      

class ContrattoFilterForm(forms.ModelForm):
    CHOICES=((0, "No"), (1, "Sì"))
    
    attivato = forms.MultipleChoiceField(choices=CHOICES,
                                         initial=[0, 1],
                                         widget=forms.CheckboxSelectMultiple())    
    completo = forms.MultipleChoiceField(choices=CHOICES,
                                         initial=[0, 1],
                                         widget=forms.CheckboxSelectMultiple())
    caricato = forms.MultipleChoiceField(choices=CHOICES,
                                         initial=[0, 1],
                                         widget=forms.CheckboxSelectMultiple())
    inviato = forms.MultipleChoiceField(choices=CHOICES,
                                        initial=[0, 1],
                                        widget=forms.CheckboxSelectMultiple())                
    piano_tariffario = forms.ModelChoiceField(queryset=models.Tariffa.objects.all(),
                                              label="Tariffa")
    agente = forms.ModelChoiceField(queryset=models.Dipendente.objects.filter(ruolo="agt"))
      
    class Media:
        js = ("js/filterform.js",)
            
    class Meta:
        model = models.Contratto
        exclude = ("appuntamento", "pdf_contratto", "nota", "data_stipula", "data_scadenza", 
                   "data_rescissione",)
        fields = ("cliente", "agente", "piano_tariffario", "attivato", "completo", "caricato", 
                  "inviato",)


#-------------------------------------------------------------------------------
# STATISTICHE

class CanvasFilterForm(forms.Form):
    CHOICHES=(("", ""), ("yesterday", "ieri"), ("today", "oggi"), ("month", "mese"), 
              ("quarter", "quarto"), ("year", "anno"), ("manual", "ricerca manuale"))
    
    periodo = forms.ChoiceField(choices=CHOICHES, initial="")
    agente = forms.ModelMultipleChoiceField(queryset=models.Dipendente.objects.filter(ruolo="agt"),
                                            label="Selezione Agenti")

class InOutFilterForm(forms.Form):
    CHOICHES=(("", ""), ("yesterday", "ieri"), ("today", "oggi"), ("month", "mese"), 
              ("quarter", "quarto"), ("year", "anno"), ("manual", "ricerca manuale"))
    
    periodo = forms.ChoiceField(choices=CHOICHES, initial="")
    agente = forms.ModelMultipleChoiceField(queryset=models.Dipendente.objects.filter(ruolo="agt"),
                                            label="Selezione Agenti")
    telefonista = forms.ModelMultipleChoiceField(queryset=models.Dipendente.objects.filter(ruolo="tel"),
                                            label="Selezione Telefonisti")

    