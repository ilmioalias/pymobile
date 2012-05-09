# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, SET_NULL

import datetime
import operator
import md5

# Create your models here.

class Dipendente(models.Model):
    #FIXME: gestione fisso, come provvigioni?
    RUOLI = (("agt", "agente"), ("tel", "telefonista"))
    
    account = models.OneToOneField(User, null=True, blank=True, on_delete=SET_NULL)
    cognome = models.CharField(max_length=45, 
                               help_text="cognome del dipendente",
                               verbose_name="Cognome")    
    nome = models.CharField(max_length=45, 
                            help_text="nome del dipendente",
                            verbose_name="Nome")
    email = models.EmailField(help_text="email del dipendente",
                              verbose_name="EMail")
    telefono = models.CharField(max_length=45, blank=True)
    cellulare = models.CharField(max_length=45, blank=True)
    ruolo = models.CharField(max_length=3,
                             choices=RUOLI, 
                             help_text="ruolo del dipendente",
                             verbose_name="Ruolo")
#    attivo = models.BooleanField(verbose_name="In Attività", default=True)
    data_assunzione = models.DateField(verbose_name="Data assunzione")
    data_licenziamento = models.DateField(blank=True, null=True,
                                          verbose_name="Data licenziamento",
                                          help_text="lasciare vuoto il campo se il rapporto "\
                                          "di lavoro è ancora in corso")
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # controlliamo che il dipendente inserito non sia già presente nel database
        # se è presente controlliamo che casomai non sia stato licenziato ed ora
        # riassunto
        prev_all = Dipendente.objects.filter(email=self.email).exclude(pk=self.pk)
        if prev_all.exists():
            for prev in prev_all:
                if not prev.data_licenziamento:
                    raise ValidationError("un dipendente con la stessa email è "\
                                          "attualmente assunto")
                                                                 
        models.Model.clean(self)
    
    def __unicode__(self):
        msg = "{} {}".format(self.cognome, self.nome)
        if self.data_licenziamento:
            msg += "[{} - {}]".format(self.data_assunzione.strftime("%d/%m/%Y"), 
                                      self.data_licenziamento.strftime("%d/%m/%Y"))
        return msg
#        return "%s %s" % (self.cognome, self.nome)
    
    class Meta:
        ordering = ["cognome", "nome"]
        verbose_name_plural = "Dipendenti"

class Utente(Dipendente):
    username = models.CharField(max_length=128, unique=True,
                                help_text="username del dipendente")
    password = models.CharField(max_length=128,
                                help_text="password del dipendente")    

    class Meta:
        verbose_name_plural = "Utenti"

class RetribuzioneDipendente(models.Model):
    data_inizio = models.DateField(verbose_name="data inizio", 
                                   help_text="data di inizio dell'uso della retribuzione")
    data_fine = models.DateField(verbose_name="data fine", blank=True, null=True)
    dipendente = models.ForeignKey(Dipendente)
    # retribuzione fissa mensile
    fisso = models.DecimalField(max_digits=7, decimal_places=2, 
                                help_text="Retribuzione fissa mensile",
                                verbose_name="fisso",
                                default=200,
                                blank=True)    
    # provvigione X contratto di agente o telefonista
    provvigione_contratto = models.DecimalField(max_digits=5, decimal_places=2, 
                              help_text="percentuale o quota standard retribuita al dipendente per ogni contratto",
                              verbose_name="provvigione standard per contratto",)
    # provvigioni bonus
    provvigione_bonus = models.TextField(blank=True, default="",
                                         verbose_name="provvigioni bonus", 
                                         help_text='''
        Chiavi: <b>gestore</b>, <b>profilo</b>, <b>tipo</b>, <b>fascia</b>, <b>servizio</b>, <b>blindato</b>, <b>provvigione</b><br/> 
        La chiave <b>provvigione</b> (valore in euro) è obbligatoria, 
        ognuna delle altre chiavi è opzionale, ma almeno una deve essere presente oltre a <b>provvigione</b>.
        Le chiavi <b>gestore</b>, <b>profilo</b>, <b>tipo</b>, <b>fascia</b>, <b>servizio</b> si riferiscono alle tariffe, 
        mentre <b>blindato</b> al cliente firmatario del contratto; la chiave <b>blindato</b> accetta come valore un intero; 
        qualunque intero maggiore di 0 corrisponde a <i>vero</i>, 0 a <i>falso</i>. 
        <br/><b>ex:</b> se si volesse aggiungere per il dipendente selezionato una provvigione 
        bonus di 5€ per tutte le tariffe di tipo SIM e fascia LOW vendute ad un cliente <i>blindato</i>, basterà inserire: 
        <br/><b>tipo: sim, fascia: low, blindato: 1, provvigione: 5;</b><br/> 
        le chiavi devono essere separate dalla <i>virgola</i>, i <i>due punti</i> servono per indicare 
        il valore della chiave e il <i>punto e virgola</i> è usato come termine; è possibile inserire
        più di una provvigione speciale per un singolo dipendente; gli spazi e l'ordine  di inserimento delle chiavi non sono influenti.<br/>
        <b>NB:</b> Per i telefonisti sono pre-inserite le seguenti provvigioni bonus:
        <br/><b>tipo: sim, provvigione: 1;<br/> 
        gestore: telecom, servizio: ull, provvigione: 10;<br/>
        gestore: telecom, servizio: nip, provvigione: 10;<br/>
        tipo: adsl, provvigione: 5;<br/>
        tipo: adsl, fascia: premium, provvigione: 10;</b><br/>
        Mentre per gli agenti è pre-inserita la seguente provvgione bonus:
        <br/><b>blindato: 1, provvigione: 10;</b><br/> 
        ''',)
    variazione = models.BooleanField(default=False)
    # "principale" indica la prima retribuzione aasegnata al dipendente
    principale = models.BooleanField(default=False)
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)     
    
    def clean(self):
        # FIXME: data_fine delle retirbuzioni (non variazione) deve essere aggioranata 
        # automaticamente quando viene inserita una nuova retribuzione. deve avvenire
        # la stessa cosa che avviene cone le var.tmp. e nel template un colore deve 
        # definire i vari periodi
        if not self.variazione:
            self.data_fine = self.data_inizio
        if self.variazione:
            self.fisso = 0
        models.Model.clean(self)
        
    def __unicode__(self):
        if self.variazione:
            if self.dipendente.ruolo == "agt": 
                prov = "{}% per contratto".format(str(self.provvigione_contratto))
            else:
                prov = "{}€ per contratto".format(str(self.provvigione_contratto))
            if self.provvigione_bonus:
                prov += " + provvigione bonus"
            return "da {} a {}: {}".format(self.data_inizio, self.data_fine, prov)
        else:
            prov = "fisso={}".format(self.fisso)
            if self.dipendente.ruolo == "agt": 
                prov += " + {}% per contratto".format(str(self.provvigione_contratto))
            else:
                prov += " + {}€ per contratto".format(str(self.provvigione_contratto))
            if self.provvigione_bonus:
                prov += " + provvigione bonus"
            return "da {}: {}".format(self.data_inizio, prov)  
        
    class Meta:
        verbose_name_plural = "Retribuzuioni Dipendenti"
        ordering=["-data_inizio"]
        #unique_together = ["dipendente","data_inizio"]

class Cliente(models.Model):
    TIPI = (("bus", "business"), ("pri", "privato"))
    
    denominazione= models.CharField(max_length=45, 
                                    help_text="ragione sociale dell'impresa commerciale",
                                    verbose_name="Ragione sociale",
                                    blank=True)
    cognome = models.CharField(max_length=45, blank=True, 
                               verbose_name="cognome")
    nome = models.CharField(max_length=45, blank=True)
    tipo = models.CharField(max_length=3, choices=TIPI, default="pri")
    partiva_codfisc = models.CharField(max_length=11, unique=True, 
                                       verbose_name="part. iva / cod. fisc.")
    indirizzo = models.CharField(max_length=100, blank=True)
    residenza = models.CharField(max_length=45, blank=True, verbose_name="città")
    email = models.EmailField(help_text="email del cliente", blank=True)
    telefono = models.CharField(max_length=45, blank=True)
    cellulare = models.CharField(max_length=45, blank=True)
    fax = models.CharField(max_length=45, blank=True)
    blindato = models.BooleanField(help_text="cliente blindato", default=False)
    nota = models.TextField(verbose_name="nota del cliente", blank=True)
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        if self.denominazione:
            msg = "{}".format(self.denominazione)
            if self.cognome:
                msg += "di {} {}".format(self.cognome, self.nome)
            return msg
        if self.cognome:
            return "{} {}".format(self.cognome, self.nome)
        if self.tipo == "bus":
            return "P.I. {}".format(self.partiva_codfisc)
        else:
            return "C.F. {}".format(self.partiva_codfisc)
        
    class Meta:
        ordering = ["denominazione", "cognome"]
        verbose_name_plural = "Clienti"

class Gestore(models.Model):
    denominazione = models.CharField(max_length=45, primary_key=True,)
    
    def __unicode__(self):
        return "{}".format(self.denominazione)
    
    class Meta:
        verbose_name_plural = "Gestori"

class TipologiaTariffa(models.Model):
    gestore = models.ForeignKey(Gestore)
    denominazione = models.CharField(max_length=45,
                            help_text="tipologia della tariffa")

    def __unicode__(self):
        return "{}".format(self.denominazione)
    
    class Meta:
        verbose_name_plural = "Tipologie delle tariffe"
        unique_together = ("gestore", "denominazione")

class FasciaTariffa(models.Model):
    gestore = models.ForeignKey(Gestore)
    denominazione = models.CharField(max_length=45, 
                              verbose_name="fascia di consumo della tariffa")

    def __unicode__(self):
        return "{}".format(self.denominazione)  
    
    class Meta:
        verbose_name_plural = "Fasce di consumo delle tariffe"
        unique_together = ("gestore", "denominazione")

class ServizioTariffa(models.Model):
    gestore = models.ForeignKey(Gestore)
    denominazione = models.CharField(max_length=45,
                                help_text="servizio di portabilità",
                                verbose_name="servizio di portabilità")

    def __unicode__(self):
        return "{}".format(self.denominazione)
    
    class Meta:
        verbose_name_plural = "Servizi di portabilità"
        unique_together = ("gestore", "denominazione")      

class Tariffa(models.Model):
    # campi generici
    gestore = models.ForeignKey(Gestore, default="tim")
    profilo = models.CharField(max_length=45, 
                               help_text="denominazione della tariffa")
    attivo = models.BooleanField(help_text="tariffa ancora in uso", default=True)
    punteggio = models.DecimalField(max_digits=5, decimal_places=2, 
                                    help_text="punteggio interno all'azienda",
                                    verbose_name="punteggio aziendale")
    tipo = models.ForeignKey(TipologiaTariffa, blank=True, null=True, 
                             verbose_name="tipo", on_delete=SET_NULL)
    fascia = models.ForeignKey(FasciaTariffa, blank=True, null=True, 
                               verbose_name="fascia", on_delete=SET_NULL)
    servizio = models.ForeignKey(ServizioTariffa, blank=True, null=True, 
                                 verbose_name="servizio", on_delete=SET_NULL)
    sac = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                              help_text="provvigione 'una tantum' erogata per il "\
                              "contratto stipulato",
                              verbose_name="provvigione per contratto/S.A.C.")
#    code = models.CharField(max_length=32, editable=False) 
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True) 
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        queries = [Q(gestore=self.gestore),
                   Q(profilo=self.profilo),
                   Q(attivo=self.attivo)]
                
        if str(self.gestore) == "edison":
            if self.tipo is None:
                queries.append(Q(tipo__isnull=True))
            else:
                queries.append(Q(tipo=self.tipo))
            if self.fascia is None:
                queries.append(Q(fascia__isnull=True))
            else:
                queries.append(Q(fascia=self.fascia)) 
            if not self.pk:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
            else:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exclude(pk=self.pk).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
        elif str(self.gestore) == "tim":
            if self.tipo is None:
                queries.append(Q(tipo__isnull=True))
            else:
                queries.append(Q(tipo=self.tipo))
            if self.fascia is None:
                queries.append(Q(fascia__isnull=True))
            else:
                queries.append(Q(fascia=self.fascia))
            if self.servizio is None:
                queries.append(Q(servizio__isnull=True))
            else:
                queries.append(Q(servizio=self.servizio))    
            if not self.pk:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
            else:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exclude(pk=self.pk).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
        elif str(self.gestore) == "telecom":
            if self.tipo is None:
                queries.append(Q(tipo__isnull=True))
            else:
                queries.append(Q(tipo=self.tipo))
            if self.fascia is None:
                queries.append(Q(fascia__isnull=True))
            else:
                queries.append(Q(fascia=self.fascia))
            if self.servizio is None:
                queries.append(Q(servizio__isnull=True))
            else:
                queries.append(Q(servizio=self.servizio))            
            if not self.pk:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
            else:
                if Tariffa.objects.filter(reduce(operator.and_, queries)).exclude(pk=self.pk).exists():
                    raise ValidationError("La tariffa è già presente nel DATABASE")
        
        models.Model.clean(self)
    
    def __unicode__(self):
        msg = "{},{}".format(self.gestore, self.profilo)
        if self.tipo:
            msg += "," + str(self.tipo)
        if self.fascia:
            msg += "," + str(self.fascia)
        if self.servizio:
            msg += "," + str(self.servizio)                    
        return msg           
            
    class Meta:
        verbose_name_plural = "Tariffe"
        ordering = ["gestore", "profilo", "tipo", "servizio", "sac"]

class Referente(models.Model):
    cognome = models.CharField(max_length=45)
    nome = models.CharField(max_length=45)
    qualifica = models.CharField(max_length=45, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=45, blank=True)
    cellulare = models.CharField(max_length=45, blank=True)
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        msg = "{} {}".format(self.cognome, self.nome)
        if self.qualifica:
            msg += "- {}".format(self.qualifica)
        return msg
    
    class Meta:
        verbose_name_plural = "Referenti"
        ordering=["cognome", "nome"]

class Appuntamento(models.Model):
    telefonista = models.ForeignKey(Dipendente, 
                                    related_name="telefonista", 
                                    limit_choices_to={"ruolo": "tel",})
    cliente = models.ForeignKey(Cliente)
    data = models.DateTimeField(verbose_name="Data e Ora")
    referente = models.ForeignKey(Referente, related_name="referente", blank=True, 
                                  null=True, on_delete=SET_NULL)
    num_sim = models.CharField(max_length=45, 
                               blank=True,
                               verbose_name="Numero sim del contatto")
    gestore_mob = models.CharField(max_length=45, 
                                   blank=True, 
                                   verbose_name="Gestore mobile del contatto")
    gestore_fisso = models.CharField(max_length=45, 
                                     blank=True, 
                                     verbose_name="Gestore fisso del contatto")    
    nota = models.TextField(blank=True)
    agente = models.ForeignKey(Dipendente, 
                               related_name="agente", 
                               limit_choices_to={"ruolo": "agt",}, 
                               blank=True, null=True, on_delete=SET_NULL,
                               verbose_name="Agente assegnato")
    data_assegnazione = models.DateField(verbose_name="data dell'assegnazione",
                                         blank=True, null=True, editable=False)
    richiamare = models.BooleanField(help_text="da richiamare", default=False)
    data_richiamare = models.DateField(verbose_name="data in cui richiamare il cliente",
                                       blank=True, null=True)
    nota_esito = models.TextField(verbose_name="nota dell'esito",
                                  blank=True)
    data_contatto = models.DateField(auto_now_add=True, verbose_name="Data contatto")
    
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.agente and not self.data_assegnazione:
            self.data_assegnazione = datetime.datetime.now()
        elif not self.agente and self.data_assegnazione:
            self.data_assegnazione = None
        
        models.Model.clean(self)    
    
    def __unicode__(self):
        data = self.data.strftime("%d/%m/%Y alle %H:%M")
        cliente = self.cliente
        return "{} con {}".format(data, cliente)
    
    class Meta:
        verbose_name_plural = "Appuntamenti"
        ordering=["-data"]

class Contratto(models.Model):
    cliente = models.ForeignKey(Cliente, 
                                help_text="cliente che ha stipulato il contratto",)
    agente = models.ForeignKey(Dipendente, 
                               help_text="agente che ha stipulato il contratto",
                               limit_choices_to={"ruolo": "agt",})
    piano_tariffario = models.ManyToManyField(Tariffa, 
                                              through="PianoTariffario",
                                              verbose_name="Piano tariffario",
                                              limit_choices_to={"attivo": 1})
    data_stipula = models.DateField(verbose_name="Data di stipulazione")
    data_scadenza = models.DateField(verbose_name="Data di scadenza")
    appuntamento = models.ForeignKey(Appuntamento, blank=True, null=True, on_delete=SET_NULL,)
    vas_telefonista = models.DecimalField(max_digits=5, decimal_places=2,
                                          verbose_name="Bonus per telefonista",
                                          help_text="bonus per telefonista",
                                          default=0, blank=True)
    vas_agente = models.DecimalField(max_digits=5, decimal_places=2,
                                     verbose_name="Bonus per agente",
                                     help_text="bonus per agente",
                                     default=0, blank=True)    
    data_rescissione = models.DateField(blank=True, 
                                        verbose_name="Data di rescissione",
                                        null=True)
    pdf_contratto = models.FileField(upload_to="contratti/%Y/%m/", blank=True, null=True)
    completo = models.BooleanField(default=False, 
                                   help_text="contratto completato")
    data_completato = models.DateField(blank=True, 
                                           verbose_name="data completamento",
                                           editable=False, null=True)
    inviato = models.BooleanField(default=False, 
                                  help_text="contratto inviato")
    data_inviato = models.DateField(blank=True, 
                                    verbose_name="data di invio",
                                    editable=False, null=True)
    caricato = models.BooleanField(default=False, 
                                   help_text="contratto caricato")
    data_caricato = models.DateField(blank=True, 
                                     verbose_name="data del caricamento",
                                     editable=False, null=True)
    rifiutato = models.BooleanField(default=False, 
                                   help_text="contratto rifiutato")
    data_rifiutato = models.DateField(blank=True, 
                                      verbose_name="data del rifiuto",
                                      editable=False, null=True)
    attivato = models.BooleanField(default=False, 
                                   help_text="contratto attivato")
    data_attivato = models.DateField(blank=True, 
                                     verbose_name="data dell'attivazione",
                                     editable=False, null=True)
    nota = models.TextField(blank=True)
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)         
    
    def clean(self): 
        if not self.completo and self.data_completato:
            self.data_completato = None
        elif self.completo and not self.data_completato:
            self.data_completato = datetime.datetime.now()
        
        if not self.inviato and self.data_inviato:
            self.data_inviato = None
        elif self.inviato and not self.data_inviato:
            self.data_inviato = datetime.datetime.now()
        
        if not self.caricato and self.data_caricato:
            self.data_caricato = None
        elif self.caricato and not self.data_caricato:
            self.data_caricato = datetime.datetime.now()
        
        if not self.rifiutato and self.data_rifiutato:
            self.data_rifiutato = None
        elif self.rifiutato and not self.data_rifiutato:
            self.data_rifiutato = datetime.datetime.now()
        
        if not self.attivato and self.data_attivato:
            self.data_attivato = None
        elif self.attivato and not self.data_attivato:
            self.data_attivato = datetime.datetime.now()      
        
        models.Model.clean(self)   
    
    def __unicode__(self):
        return "{} - {}".format(self.cliente, self.data_stipula)
       
    class Meta:
        verbose_name_plural = "Contratti"
        ordering=["-data_stipula", "-data_scadenza"]
            
class PianoTariffario(models.Model):
    contratto = models.ForeignKey(Contratto)
    tariffa = models.ForeignKey(Tariffa,
                                help_text="gestore,profilo,tipo,fascia,servizio")
    num = models.PositiveIntegerField(verbose_name="quantità")
    opzione = models.BooleanField(blank=True, help_text="la tariffa è un opzione")
    
    def __unicode__(self):
        return "{}: {}".format(self.contratto, self.tariffa)
    
    class Meta:
        verbose_name_plural = "Piani Tariffari"

class Obiettivo(models.Model):
    denominazione = models.CharField(max_length=45,
                                     unique=True, 
                                     verbose_name="Etichetta dell'obiettivo",
                                     help_text="etichetta da assegnare all'obiettivo",)
    data_inizio = models.DateField(verbose_name="Data inizio obiettivo",
                                   null=True)
    data_fine = models.DateField(verbose_name="Data fine obiettivo",
                                 help_text="lasciare questo campo vuoto se l'obbiettivo è tutt'ora in vigore",
                                 null=True)
    parametri = models.TextField(blank=True, 
                                 default="",
                                 verbose_name="Parametri dell'obiettivo", 
                                 help_text='''
        Chiavi: <b>gestore</b>, <b>profilo</b>, <b>tipo</b>, <b>fascia</b>, <b>servizio</b><br/> 
        ognuna delle chiavi è opzionale, lasciando il campo vuoto l'obbiettivo sarà 
        relativo a tutti i contratti stipulati.
        Le chiavi <b>gestore</b>, <b>profilo</b>, <b>tipo</b>, <b>fascia</b>, <b>servizio</b> 
        si riferiscono alle tariffe. 
        <br/><b>ex:</b> se si volesse aggiungere un obiettivo per le tariffe di tipo 
        SIM e fascia LOW, basterà inserire: 
        <br/><b>tipo: sim, fascia: low</b><br/> 
        le chiavi devono essere separate dalla <i>virgola</i>, i <i>due punti</i> 
        servono per indicare il valore della chiave e il <i>punto e virgola</i> è 
        usato come termine; gli spazi extra e l'ordine  di inserimento delle chiavi 
        non sono influenti.<br/>
        <b>NB:</b> le chiavi possono essere ripetute; <b>ex:</b> si vuole aggiungere un obiettivo 
        per la vendita di tariffe TIM e TELECOM, allora bisognerà scrivere:
        <br/><b>gestore: tim, gestore: telecom</b><br/>
        ''',)
    punteggio = models.IntegerField(verbose_name="Punteggio", 
                                    help_text="meta da raggiungere rispetto ai parametri indicati")
    creazione = models.DateTimeField(auto_now_add=True)
    modifica = models.DateTimeField(auto_now=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        models.Model.clean(self)
        
        if not self.pk:
            # controlliamo che non venga assunto un obiettivo con la stessa denominazione
            # di uno attivo già presente nel database
            prev_all = Obiettivo.objects.filter(denominazione=self.denominazione)
            if prev_all.exists():
                for prev in prev_all:
                    if not prev.data_fine:
                        raise ValidationError("un obiettivo denominato <b>{}</b> "\
                                              "ancora attivo esiste già nel DATBASE"\
                                              .format(self.denominazione))
    
    def __unicode__(self):
        return "{}".format(self.denominazione)
    
    class Meta:
        verbose_name_plural = "Obiettivi"
