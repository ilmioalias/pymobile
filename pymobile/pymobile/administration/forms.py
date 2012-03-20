# -*- coding: utf-8 -*-

#FIXME: controllare tutti i field da localizzare

from django import forms
from django.contrib.auth.models import User, Group
from django.forms.models import inlineformset_factory
from django.utils.datetime_safe import datetime

import pymobile.administration.models as models

#-------------------------------------------------------------------------------
# AMMINISTRAZIONE

class AccountForm(forms.ModelForm):
    profile = forms.ModelChoiceField(queryset=models.Dipendente.objects.filter(ruolo="tel",
                                                                               account__isnull=True,), 
                                     widget=forms.Select(attrs={"class": "tel"}),
                                     required=False,
                                     label="Profilo", 
                                     help_text="profilo del telefonista collegato all'account")
    groups = forms.ModelChoiceField(queryset=Group.objects.exclude(name="guest"), 
                                    initial="amministratore",
                                    label="Gruppo",)
    password_confirm = forms.CharField(widget=forms.PasswordInput(), 
                                       label="Conferma password", required=False)
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        # hack per inserire nel queryset di profile nel caso di modifca anche 
        # il telefonista corrente 
        if kwargs.has_key("instance"): 
            instance = kwargs["instance"]
            group = instance.groups.all()[0]
            if group.name == "telefonista":
                # devo usare il seguente stratagemma perché l'operatore "or" funziona 
                # solo su queryset 
                profile_cur = models.Dipendente.objects.filter(id=instance.dipendente.id)
                
                self.fields["profile"].queryset = self.fields["profile"].queryset | profile_cur
                self.initial["profile"] = profile_cur[0]
                
    def clean(self):
        cdata = self.cleaned_data
        group = cdata.get("groups")
        profile = cdata.get("profile")
        nome = cdata.get("first_name")
        cognome = cdata.get("last_name")
        email = cdata.get("email")

        if group:
            if group.name == "telefonista":
                if not profile:
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "è necessario selezionare un profilo telefonista collegato "\
                        "all'account che si sta creando"
                    self.errors["profile"] = self.error_class([msg])
                # nel caso in cui siano stati inseriti dati superflei cancelliamoli
                if nome:
                    cdata["nome"] = ""
                if cognome:
                    cdata["cognome"] = ""
                if email:
                    cdata["email"] = ""
            elif group.name == "amministratore":
                if not nome:
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "è necessario indicare il nome"
                    self.errors["first_name"] = self.error_class([msg])
                if not cognome:
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "è necessario indicare il cognome "
                    self.errors["last_name"] = self.error_class([msg])
                if not email:
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "è necessario inserire un indirizzo email"
                    self.errors["email"] = self.error_class([msg])
                if profile:
                    cdata["profile"] = ""
            else:
                raise forms.ValidationError("Gruppo non valido")
            
            # questo è un hack perché django si aspettta una sequenza di gruppi
            cdata["groups"] = [group,]
        
        if not self.instance.pk:
            password = cdata.get("password")
            password_confirm = cdata.get("password_confirm")
            if password:
                if password != password_confirm:
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "la password e la conferma della password non coincidono"
                    self.errors["password"] = self.error_class([msg])
                    self.errors["password_confirm"] = self.error_class([msg])
            
        return cdata
    
    def save(self, commit=True):
        cdata = self.cleaned_data
        group = cdata.get("groups")
        profile = cdata.get("profile")
        password = cdata.get("password")
        
        instance = forms.ModelForm.save(self, commit=False)
        instance.set_password(password)
        
        if commit:
            instance.save()
            # save_m2m ci serve per salvare il gruppo che è una chiave manytomany 
            self.save_m2m()
            
            if group[0]:
                if group[0].name == "telefonista" and profile:
                    # colleghiamo il profilo del dipendente teloefonista all'account
                    profile.account = instance
                    profile.save()      
            
        return instance
            
    class Media:
        js = ("js/modelform.js", "js/modelform_account.js")
    
    class Meta:
        model = User
        exclude = ("is_staff", "is_superuser", "user_permissions", "last_login", "date_joined",)
        widgets = {"first_name": forms.TextInput(attrs={"class": "admin"}),
                   "last_name": forms.TextInput(attrs={"class": "admin"}),
                   "email": forms.TextInput(attrs={"class": "admin"}),
                   "password": forms.PasswordInput(),}
        fields = ("username", "last_name", "first_name", "email", "groups", 
                  "is_active", "profile", "password", "password_confirm",)

class AccountFilterForm(forms.ModelForm):
    # "initial" contiene i valori degli id dei gruppi
    groups = forms.ModelChoiceField(queryset=Group.objects.exclude(name="guest"), 
                                    initial=[1, 2, 3],
                                    label="Gruppo",
                                    widget=forms.CheckboxSelectMultiple(),)
    
    class Meta:
        model = User
        exclude = ("last_login", "date_joined", "password", "is_staff", "is_superuser", "user_permissions",)

class AccountModPasswordForm(forms.Form):
    account_id = forms.CharField(widget=forms.HiddenInput())
    password_new = forms.CharField(widget=forms.PasswordInput(), 
                                   label="Nuova password",
                                   help_text="inserisci la nuova password")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), 
                                   label="Conferma password",
                                   help_text="conferma la nuova password")
    
    def clean(self):
        cdata = self.cleaned_data
        print(cdata)
        password_new = cdata.get("password_new")
        password_confirm = cdata.get("password_confirm")
        
        if password_new and password_confirm:
            if password_new != password_confirm:
                raise forms.ValidationError("la nuova password e la corfema non coincidono")
        
        return cdata
    
    def save(self):
        cdata = self.cleaned_data
        account_id = cdata.get("account_id")
        password_new = cdata.get("password_new")
        if account_id and password_new:
            account = User.objects.get(pk=account_id)
            account.set_password(password_new)
            account.save()
    
class DipendenteForm(forms.ModelForm):     
    def clean(self):
        cdata = self.cleaned_data
        data_assunzione = cdata.get("data_assunzione")
        data_licenziamento = cdata.get("data_licenziamento")
        if data_assunzione and data_licenziamento:
            if data_assunzione >= data_licenziamento:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "Data licenziamento precedente o uguale alla data di assunzione"
                self.errors["data_licenziamento"] = self.error_class([msg])
        
        return cdata
        
    class Media:
        js = ("js/modelform.js", "js/modelform_dipendente.js")
    
    class Meta:
        model = models.Dipendente
        exclude = ("account",)
        widgets = {"data_assunzione": forms.DateInput(format="%d/%m/%Y", attrs={"class": "date",}),
                   "data_licenziamento": forms.DateInput(format="%d/%m/%Y", attrs={"class": "date",}),}
        
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
        exclude = ("account", "provvigione_contratto", "provvigione_speciale", "fisso", 
                   "data_assunzione", "data_licenziamento", )  
        
class RetribuzioneBaseForm(forms.ModelForm):
    def values_from_provvigione_bonus_field(self, provvigione_bonus):
        provvigione_bonus = provvigione_bonus.strip()
        if not provvigione_bonus:
            return []
        
        values = []
        vs = provvigione_bonus.split(";")
        for var in vs:
            if var:
                d = {}
                opts = var.split(",")
                for opt in opts:
                    item = opt.split(":")
                
                    if len(item) == 2:
                        k = item[0].strip()
                        v = item[1].strip()
                        d[k] = v             
                values.append(d)
                
        return values    
    
    def get_provvigione_bonus_cleaned(self, values):
        if not values:
            return
        
        provvigione_bonus = ""
        for d in values:
            if d:
                for k, v in d.iteritems():
                    provvigione_bonus += str(k) + ":" + str(v) + ","
                provvigione_bonus = provvigione_bonus[:-1] + ";"
    
        return provvigione_bonus  

    def check_values(self, values):
        if not values:
            raise forms.ValidationError("provvigione bonus non valida, controlla la sintassi")
        
        for d in values:
            if not "provvigione" in d:
                provvigione_bonus = self.get_provvigione_bonus_cleaned([d])
                raise forms.ValidationError("in <b>{}</b> non è stata indicata la chiave "\
                                            "obbligatoria <b>provvigione</b>".format(provvigione_bonus))                
            
            if len(d) < 2:
                raise forms.ValidationError("in <b>{}</b> oltre alla chiave obbligatoria "\
                                            "<b>provvigione</b> devi indicare un'altra chiave".format(provvigione_bonus))
            
            for k, v in d.iteritems():
                # controlliamo le chiavi e i loro valori
                if k == "provvigione":
                    v = d["provvigione"]
                    try:
                        v = float(v)
                        if v < 0:
                            raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve essere un numero maggiore o uguale di 0".format(v))                                             
                    except:
                        raise forms.ValidationError("il valore <b>{}</b> della chiave <b>provvigione</b> deve un numero maggiore o uguale di 0".format(v))                         
                    d["provvigione"] = v                    
                elif k == "gestore":
                    if not models.Gestore.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il gestore <b>{}</b> non esiste nel DATABASE".format(v))
                elif k == "profilo":
                    if not models.Tariffa.objects.filter(profilo=v).exists():
                        raise forms.ValidationError("la tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                elif k == "tipo":
                    if not models.TipologiaTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il tipo di tariffa <b>{}</b> non esiste nel DATABASE".format(v))
                elif k == "fascia":
                    if not models.FasciaTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("la fascia <b>{}</b> non esiste nel DATABASE".format(v))   
                elif k == "servizio":
                    if not models.ServizioTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il servizio <b>{}</b> non esiste nel DATABASE".format(v))
                elif k == "blindato":
                    try:
                        v = int(v)
                    except : 
                        raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))                                                 
                    if v < 0:
                        raise forms.ValidationError("il valore <b>{}</b> della chiave <b>blindato</b> deve essere un intero maggiore o uguale di 0".format(v))
                    d[k] = v
                else:
                    raise forms.ValidationError("la chiave <b>{}</b> non è ammessa".format(k))                                                                     
            
        return True

    def clean_provvigione_bonus(self):     
        cdata = self.cleaned_data
        provvigione_bonus = cdata.get("provvigione_bonus")
        if provvigione_bonus:
            values = self.values_from_provvigione_bonus_field(provvigione_bonus)
            self.check_values(values)
            return self.get_provvigione_bonus_cleaned(values)
        else:
            return ""
   
    class Media:
        js = ("js/modelform_retribuzione.js",)
    
    class Meta:
        model = models.RetribuzioneDipendente

class RetribuzioneForm(RetribuzioneBaseForm):
    def clean(self):
        cdata = self.cleaned_data
        
        # controlliamo che non vi sia un'altra variazione della retribuzione per la
        # stessa data
        if not self.instance.pk:
            data_inizio = cdata.get("data_inizio")
            dipendente = cdata.get("dipendente")
            if data_inizio and dipendente:
                if models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                variazione=False,
                                                                data_inizio=data_inizio).exists():
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "Esiste già una variazione alla retribuzione assegnata in "\
                        "questa data <b>{}</b>".format(data_inizio.strftime("%d/%m/%Y"))
                    self.errors["data_inizio"] = self.error_class([msg])
        else:
            data_inizio = cdata.get("data_inizio")
            dipendente = cdata.get("dipendente")
            if data_inizio and dipendente:
                if models.RetribuzioneDipendente.objects.filter(dipendente=dipendente,
                                                                variazione=False,
                                                                data_inizio=data_inizio).exclude(pk=self.instance.pk).exists():
                    # creiamo il msg di errore per il campo "data_inizo"
                    msg = "Esiste già una variazione alla retribuzione assegnata in "\
                        "questa data <b>{}</b>".format(data_inizio.strftime("%d/%m/%Y"))
                    self._errors["data_inizio"] = self.error_class([msg])        
        
        return cdata
                         
    class Meta:
        model = models.RetribuzioneDipendente
        widgets = {"dipendente": forms.HiddenInput(),
                   "data_inizio": forms.DateInput(format="%d/%m/%Y", 
                                                  attrs={"class": "date",}),
                   "principale": forms.HiddenInput(),}
        exclude = ("data_fine", "variazione",)

RetribuzioneFormset = inlineformset_factory(models.Dipendente, 
                                            models.RetribuzioneDipendente, 
                                            RetribuzioneForm,
                                            extra=1,
                                            can_delete=False)

class VariazioneRetribuzioneForm(RetribuzioneBaseForm):
        
    class Meta:
        model = models.RetribuzioneDipendente
        exclude = ("fisso",)
        widgets = {"dipendente": forms.HiddenInput(),
                   "data_inizio": forms.DateInput(format="%d/%m/%Y", 
                                                  attrs={"class": "date",}),
                   "data_fine": forms.DateInput(format="%d/%m/%Y", 
                                                attrs={"class": "date",}),
                   "variazione": forms.HiddenInput(),
                   "principale": forms.HiddenInput(),}

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
        
        gestore = cdata.get("gestore")        
        if gestore:
            if str(gestore) == "tim":
                cdata["tipo"] = cdata.get("tipo_tim")
                cdata["fascia"] = cdata.get("fascia_tim")
                cdata["servizio"] = cdata.get("servizio_tim")
            elif str(gestore) == "telecom":
                cdata["tipo"] = cdata.get("tipo_telecom")
                cdata["fascia"] = cdata.get("fascia_telecom")
                cdata["servizio"] = cdata.get("servizio_telecom")
            elif str(gestore) == "edison":
                cdata["tipo"] = cdata.get("tipo_edison")
                cdata["fascia"] = cdata.get("fascia_edison")         
        
        return cdata
    
    class Media:
        js = ("js/modelform.js", "js/modelform_tariffa.js",)
    
    class Meta:
        model = models.Tariffa
        widgets = {"tipo": forms.HiddenInput(),
                   "fascia": forms.HiddenInput(),
                   "servizio": forms.HiddenInput()}
#        widgets = {"sic": forms.TextInput(attrs={"class": "hidden edison"}),
#                   "sic_anni": forms.TextInput(attrs={"class": "hidden edison"}),}
        fields = ("gestore", "profilo", "tipo_tim", "fascia_tim", "servizio_tim", 
                  "tipo_telecom", "fascia_telecom", "servizio_telecom", 
                  "tipo_edison", "fascia_edison", "sac", "attivo", "punteggio",
                  "tipo", "fascia", "servizio",)
        

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

class TipologiaTariffaFilterForm(forms.ModelForm):
    
    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.TipologiaTariffa
   
class FasciaTariffaForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.FasciaTariffa

class FasciaTariffaFilterForm(forms.ModelForm):

    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.FasciaTariffa

class ServizioTariffaForm(forms.ModelForm):

    class Media:
        js = ("js/modelform.js",)
    
    class Meta:
        model = models.ServizioTariffa

class ServizioTariffaFilterForm(forms.ModelForm):

    class Media:
        js = ("js/filterform.js",)
    
    class Meta:
        model = models.ServizioTariffa

class AppuntamentoForm(forms.ModelForm):           
    def clean(self):
        cdata = self.cleaned_data
        agente = cdata.get("agente")
        data = cdata.get("data")
        if agente and data:
            data_assunzione = agente.data_assunzione
            data_licenziamento = agente.data_licenziamento
            if data_assunzione and data_assunzione > data.date():
                # creiamo il msg di errore per il campo "data"
                msg = "La data dell'appuntamento è precedente alla data di assunzione "\
                    "dell'agente assegnato"
                self.errors["agente"] = self.error_class([msg])
            if data_licenziamento and data_licenziamento < data.date():
                # creiamo il msg di errore per il campo "data"
                msg = "La data dell'appuntamento è successiva alla data di licenziamento "\
                    "dell'agente assegnato"
                self.errors["assegnato"] = self.error_class([msg])
        
        print(cdata)
        return cdata
    
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
    
    def clean(self):
        cdata = self.cleaned_data
        agente = cdata.get("agente")
        data = cdata.get("data")
        if data and agente:
            # controlliamo che l'agente selezionato sia assunto per la data dell'appuntamento
            data_assunzione = agente.data_assunzione
            if data_assunzione and data < data_assunzione:
                # creiamo il msg di errore per il campo "data"
                msg = "La data dell'appuntamento è precedente alla data di assunzione "\
                    "dell'agente selezionato"
                self.errors["agente"] = self.error_class([msg])
            data_licenziamento = agente.data_licenziamento
            if data_licenziamento and data > data_licenziamento:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "La data dell'appuntamento è successiva alla data di licenziamento "\
                    "dell'agente selezionato"
                self.errors["agente"] = self.error_class([msg])
                
        return forms.ModelForm.clean(self)
    
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

class PianoTariffarioInlineFormset(forms.models.BaseInlineFormSet):   
    def clean(self):
        # ci serve questo hack per fare in modo che almeno un piano tariffario,
        # all'inserimento del contratto, sia inserito
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    count += 1
            except AttributeError:
                pass
        if count < 1:
            raise forms.ValidationError("è necessario aggiungere almeno un piano tariffario "\
                                        "per ogni contratto inserito")
        
class ContrattoForm(forms.ModelForm):
    appuntamento = forms.ModelChoiceField(queryset=models.Appuntamento.objects.filter(contratto__isnull=True),
                                          required=False)
    
    class Media:
        js = ("js/modelform.js", "js/modelform_contratto.js",)
    
    def clean(self):
        cdata = self.cleaned_data
        
        # controlliamo le date
        data_stipula = cdata.get("data_stipula")
        data_scadenza = cdata.get("data_scadenza") 
        data_rescissione = cdata.get("data_rescissione")
        if data_scadenza and data_stipula:
            if data_scadenza <= data_stipula:            
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "La data di scadenza è precedente alla data di stiupula"
                self._errors["data_scadenza"] = self.error_class([msg])
        if data_rescissione:
            if data_rescissione <= data_stipula or data_rescissione >= data_scadenza:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "La data di rescissione è precedente alla data di stiupula "\
                    "o successiva alla data di scadenza"
                self._errors["data_rescissione"] = self.error_class([msg])
        
        # controlliamo che l'agente selezionato non sia stato "assunto" successivamente 
        # alla stipula del contratto
        agente = cdata.get("agente")
        if agente:
            data_assunzione = agente.data_assunzione
            if data_assunzione > data_stipula:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "la data di assunzione dell'agente selezionato è successiva "\
                    "alla data di stipula del contratto"
                self._errors["agente"] = self.error_class([msg])
            
            data_licenziamento = agente.data_licenziamento
            if data_licenziamento and data_licenziamento <= data_stipula:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "la data di licenziamento dell'agente selezionato è precendente "\
                    "alla data di stipula del contratto"
                self._errors["agente"] = self.error_class([msg])
            
            
        # controlliamo se l'appuntamento selezionato è plausibile, cioè le date
        # corrispondono e il cliente è lo stesso del contratto
        appuntamento = cdata.get("appuntamento")
        cliente = cdata.get("cliente")
        if appuntamento and data_stipula:
            data_appuntamento = appuntamento.data
            if data_appuntamento.date() > data_stipula:
                # creiamo il msg di errore per il campo "data_inizo"
                msg = "la data dell'appuntamento selezionato è successiva alla "\
                    "data di stipula del contratto"
                self._errors["appuntamento"] = self.error_class([msg])
        if appuntamento and cliente:            
            if appuntamento.cliente != cliente:
            # creiamo il msg di errore per il campo "data_inizo"
                msg = "il cliente dell'appuntamento selezionato è diverso dal "\
                    "cliente con cui si è stipulato il contratto"
                self._errors["appuntamento"] = self.error_class([msg])

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

class ObiettivoForm(forms.ModelForm):
    anno_inizio = forms.ChoiceField(choices=[("", "")], 
                                    label="Anno d'inizio")
    quarto_inizio = forms.ChoiceField(choices=[("", "")], 
                                      label="Quarto d'inizio")
    anno_fine = forms.ChoiceField(choices=[("", "")], label="Anno di fine", 
                                  help_text="lasciare il campo vuoto se l'obbiettivo è ancora in uso",
                                  required=False)
    quarto_fine = forms.ChoiceField(choices=[("", "")], label="Quarto di fine",
                                    help_text="lasciare il campo vuoto se l'obbiettivo è ancora in uso",
                                    required=False)
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        # hack per aggiungere ai campi "fine" la possibilità della scelta vuota
        QUARTERS = [("", ""), (1, "1°"), (2, "2°"), (3, "3°"), (4, "4°")]
        YEARS = [(y, y) for y in xrange(2012, datetime.today().year + 2)]
        YEARS.insert(0, ("", ""))
        self.fields["anno_inizio"].choices = YEARS
        self.fields["quarto_inizio"].choices = QUARTERS
        self.fields["anno_fine"].choices = YEARS
        self.fields["quarto_fine"].choices = QUARTERS
        
        if kwargs.has_key("instance"): 
            instance = kwargs["instance"]
            
            data_inizio = instance.data_inizio
            y = data_inizio.year
            m = data_inizio.month
            if 1 <= m <= 3:
                q = 1
            elif 4 <= m <= 6:
                q = 2
            elif 7 <= m <= 9:
                q = 3
            elif 10 <= m <= 12:
                q = 4
            
            self.initial["anno_inizio"] = y
            self.initial["quarto_inizio"] = q
            
            data_fine = instance.data_fine
            if data_fine:
                y = data_fine.year
                m = data_fine.month
                if 1 <= m <= 3:
                    q = 1
                elif 4 <= m <= 6:
                    q = 2
                elif 7 <= m <= 9:
                    q = 3
                elif 10 <= m <= 12:
                    q = 4
                
                self.initial["anno_fine"] = y
                self.initial["quarto_fine"] = q
            
    def values_from_parametri_field(self, parametri):
        parametri = parametri.strip()
        if not parametri:
            return []
        
        d = {}
        opts = parametri.split(",")

        for opt in opts:
            item = opt.split(":")

            if len(item) == 2:
                k = item[0].strip()
                v = item[1].strip()
                if k in d:
                    d[k].append(v)
                else:    
                    d[k] = [v,]             
            
        return d
    
    def get_parametri_cleaned(self, values):
        if not values:
            return
        if not isinstance(values, dict):
            raise Exception("non è un dizionario!")
        
        parametri = ""
        for k, vs in values.iteritems():
            for v in vs:
                parametri += str(k) + ":" + str(v) + ","
    
        return parametri  

    def check_values(self, values):
        if not values:
            raise forms.ValidationError("parametri non validi, controlla la sintassi")
            
        for k, vs in values.iteritems():
            # controlliamo le chiavi e i loro valori
            if k == "gestore":
                for v in vs:
                    if not models.Gestore.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il gestore <b>{}</b> non esiste nel DATABASE".format(v))
            elif k == "profilo":
                for v in vs:
                    if not models.Tariffa.objects.filter(profilo=v).exists():
                        raise forms.ValidationError("la tariffa <b>{}</b> non esiste nel DATABASE".format(v))
            elif k == "tipo":
                for v in vs:
                    if not models.TipologiaTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il tipo di tariffa <b>{}</b> non esiste nel DATABASE".format(v))
            elif k == "fascia":
                for v in vs:
                    if not models.FasciaTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("la fascia <b>{}</b> non esiste nel DATABASE".format(v))   
            elif k == "servizio":
                for v in vs:
                    if not models.ServizioTariffa.objects.filter(denominazione=v).exists():
                        raise forms.ValidationError("il servizio <b>{}</b> non esiste nel DATABASE".format(v))
            else:
                raise forms.ValidationError("la chiave <b>{}</b> non è ammessa".format(k))                                                                     
            
        return True    
    
    def clean_parametri(self):
        cdata = self.cleaned_data
        
        # controlliamo che la data di fine, se presente, sia maggiore della data
        # di inizio
        y = cdata.get("anno_fine")
        q = cdata.get("quarto_fine")
        
        if y and q:
            y = int(y)
            q = int(q)
            
            if q == 1:
                m = 1
            elif q == 2:
                m = 4
            elif q == 3:
                m = 7
            elif q == 4:
                m = 10
            
            data_fine = datetime(y, m, 1).date()                

            y = int(cdata.get("anno_inizio"))
            q = int(cdata.get("quarto_inizio"))
        
            if q == 1:
                m = 1
            elif q == 2:
                m = 4
            elif q == 3:
                m = 7
            elif q == 4:
                m = 10
            
            data_inizio = datetime(y, m, 1).date()                
            if data_fine < data_inizio:
                # creiamo il msg di errore per i campi "fine"
                raise forms.ValidationError("la data di fine inserita è precedente "\
                                            "alla data di inizio")
                    
        parametri = cdata.get("parametri")
        if parametri:
            values = self.values_from_parametri_field(parametri)
            self.check_values(values)
            return self.get_parametri_cleaned(values)
        else:
            return ""
    
    def save(self, commit=True):
        # devo "subclassare" il metodo save() perché non riesco ad aggiungere a 
        # self.cleaned_data le date di inizio e fine, quindi qualche linea di codice
        # si ripete con clean
        instance = forms.ModelForm.save(self, commit=False)
        
        cdata = self.cleaned_data
        y = int(cdata.get("anno_inizio"))
        q = int(cdata.get("quarto_inizio"))
        
        if q == 1:
            m = 1
        elif q == 2:
            m = 4
        elif q == 3:
            m = 7
        elif q == 4:
            m = 10
        
        data_inizio = datetime(y, m, 1).date()                
        instance.data_inizio = data_inizio
        
        y = cdata.get("anno_fine")
        q = cdata.get("quarto_fine")
        
        if y and q:
            
            y = int(y)
            q = int(q)
            
            if q == 1:
                m = 1
            elif q == 2:
                m = 4
            elif q == 3:
                m = 7
            elif q == 4:
                m = 10
            
            data_fine = datetime(y, m, 1).date()                
            instance.data_fine = data_fine
        
        if commit:
            instance.save()       
        
        return instance
            
    class Media:
        js = ("js/modelform.js",)    

    class Meta:
        model = models.Obiettivo
        fields = ("denominazione", "anno_inizio", "quarto_inizio", "anno_fine", 
                  "quarto_fine", "parametri", "punteggio",)

class ObiettivoFilterForm(forms.Form):
    anno = forms.ChoiceField(choices=[("", "")], 
                             label="Anno")
    quarto = forms.ChoiceField(choices=[("", "")], 
                               label="Quarto")

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        
        # hack per aggiungere ai campi "fine" la possibilità della scelta vuota
        QUARTERS = [("", ""), (1, "1°"), (2, "2°"), (3, "3°"), (4, "4°")]
        YEARS = [(y, y) for y in xrange(2012, datetime.today().year + 2)]
        YEARS.insert(0, ("", ""))
        self.fields["anno"].choices = YEARS
        self.fields["quarto"].choices = QUARTERS
