# -*- coding: utf-8 -*-

'''
Created on 07/dic/2011

@author: luigi
'''

from django.contrib import admin
import pymobile.administration.models as m

admin.site.register(m.Appuntamento) 
admin.site.register(m.ProvvigioneDipendente)
admin.site.register(m.Cliente)
admin.site.register(m.ConguaglioContratto)
admin.site.register(m.Contratto)
admin.site.register(m.Dipendente)
admin.site.register(m.FasciaTariffa)
admin.site.register(m.Gestore)
admin.site.register(m.PianoTariffario)
admin.site.register(m.Referente)
admin.site.register(m.RenditaContratto)
admin.site.register(m.ServizioTariffa)
admin.site.register(m.SicContratto)
admin.site.register(m.Tariffa)
#admin.site.register(m.TariffaEdison)
#admin.site.register(m.TariffaTim)
#admin.site.register(m.TariffaTelecom)
admin.site.register(m.TipologiaTariffa)
admin.site.register(m.Utente)
