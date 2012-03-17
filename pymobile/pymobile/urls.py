from django.conf.urls.defaults import patterns, include, url
from django.views.generic.list_detail import object_detail
from pymobile.administration import models

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'pymobile.views.home', name='home'),
                       # url(r'^pymobile/', include('pymobile.foo.urls')),
                
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                
                        # Uncomment the next line to enable the admin:
                        url(r'^admin/', include(admin.site.urls)),)

urlpatterns += patterns('django.views.generic.simple',
                        url(r'^pymobile/$', 
                            "direct_to_template", 
                            {"template": "index.html"}, 
                            name="login"),)

#-------------------------------------------------------------------------------
# AMMINISTRAZIONE
# tariffa
INFO_TAR={"template_name": "tariffa/view.html", 
          "queryset": models.Tariffa.objects.all()}
# dipendente
INFO_DIP={"template_name": "dipendente/view.html", 
          "queryset": models.Dipendente.objects.all()}
# cliente
INFO_CLI={"template_name": "cliente/view.html", 
          "queryset": models.Cliente.objects.all()}
# appuntamento
INFO_APP={"template_name": "appuntamento/view.html", 
          "queryset": models.Appuntamento.objects.all()}
# contratto
INFO_CON={"template_name": "contratto/view.html", 
          "queryset": models.Contratto.objects.all()}

# dipendente
urlpatterns += patterns('pymobile.administration.views',
                        url(r'^pymobile/dipendente/$', 
                            "dipendente.admin.init", 
                            name="init_dipendente"),
                        url(r'^pymobile/dipendente/add/$', 
                            "dipendente.admin.add_object", 
                            name="add_dipendente"),
                        url(r'^pymobile/dipendente/mod/(?P<object_id>\d+)/$', 
                            "dipendente.admin.mod_object", 
                            name="mod_dipendente"),
                        url(r'^pymobile/dipendente/del/$', 
                            "dipendente.admin.del_object", 
                            name="del_dipendente"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/$', 
                            object_detail, 
                            INFO_DIP, 
                            name="view_dipendente"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/$', 
                            "dipendente.admin.init_provvigione", 
                            name="init_provvigione"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/add_retribuzione/$', 
                            "dipendente.admin.add_retribuzione", 
                            name="add_retribuzione"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/add_vartmp/$', 
                            "dipendente.admin.add_vartmp", 
                            name="add_vartmp"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/mod_retribuzione/(?P<provvigione_id>\d+)/$', 
                            "dipendente.admin.mod_retribuzione", 
                            name="mod_retribuzione"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/mod_vartmp/(?P<provvigione_id>\d+)/$', 
                            "dipendente.admin.mod_vartmp", 
                            name="mod_vartmp"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/del_retribuzione/$', 
                            "dipendente.admin.del_retribuzione", 
                            name="del_retribuzione"),
                        url(r'^pymobile/dipendente/(?P<object_id>\d+)/provvigione/del_vartmp/$', 
                            "dipendente.admin.del_vartmp", 
                            name="del_vartmp"),)

# tariffa
urlpatterns += patterns('pymobile.administration.views',
                        url(r'^pymobile/tariffa/$', 
                            "tariffa.admin.init", 
                            name="init_tariffa"),
                        url(r'^pymobile/tariffa/add/$', 
                            "tariffa.admin.add_object", 
                            name="add_tariffa"),
                        url(r'^pymobile/tariffa/mod/(?P<object_id>\d+)/$', 
                            "tariffa.admin.mod_object", 
                            name="mod_tariffa"),
                        url(r'^pymobile/tariffa/del/$', 
                            "tariffa.admin.del_object", 
                            name="del_tariffa"),
                        url(r'^pymobile/tariffa/add/popup:add-(?P<field_name>\w+)/$', 
                            "tariffa.admin.add_child_object", 
                            name="add_tariffa_fk"), 
                        url(r'^pymobile/tariffa/(?P<object_id>\d+)/$', 
                            object_detail, 
                            INFO_TAR, 
                            name="view_tariffa"),
                        url(r'^pymobile/tariffa/(?P<attribute>\btipologia\b|\bfascia\b|\bservizio\b)/$', 
                            "tariffa.admin.init_attribute", 
                            name="init_attribute"),
                        url(r'^pymobile/tariffa/(?P<attribute>\btipologia\b|\bfascia\b|\bservizio\b)/add/$', 
                            "tariffa.admin.add_attribute", 
                            name="add_attribute"),
                        url(r'^pymobile/tariffa/(?P<attribute>\btipologia\b|\bfascia\b|\bservizio\b)/mod/(?P<object_id>\d+)/$', 
                            "tariffa.admin.mod_attribute", 
                            name="mod_attribute"),
                        url(r'^pymobile/tariffa/(?P<attribute>\btipologia\b|\bfascia\b|\bservizio\b)/del/$', 
                            "tariffa.admin.del_attribute", 
                            name="del_attribute"),)

# cliente
urlpatterns += patterns('pymobile.administration.views',
                        url(r'^pymobile/cliente/$', 
                            "cliente.admin.init", 
                            name="init_cliente"),
                        url(r'^pymobile/cliente/add/$', 
                            "cliente.admin.add_object", 
                            name="add_cliente"),
                        url(r'^pymobile/cliente/mod/(?P<object_id>\d+)/$', 
                            "cliente.admin.mod_object", 
                            name="mod_cliente"),
                        url(r'^pymobile/cliente/del/$', 
                            "cliente.admin.del_object", 
                            name="del_cliente"),
                        url(r'^pymobile/cliente/(?P<object_id>\d+)/$', 
                            object_detail, 
                            INFO_CLI, 
                            name="view_cliente"),)

# appuntamento
urlpatterns += patterns('pymobile.administration.views',
                        url(r'^pymobile/appuntamento/$', 
                            "appuntamento.admin.init", 
                            name="init_appuntamento"),
                        url(r'^pymobile/appuntamento/add/$', 
                            "appuntamento.admin.add_object", 
                            name="add_appuntamento"),
                        url(r'^pymobile/appuntamento/mod/(?P<object_id>\d+)/$', 
                            "appuntamento.admin.mod_object", 
                            name="mod_appuntamento"),
                        url(r'^pymobile/appuntamento/del/$', 
                            "appuntamento.admin.del_object", 
                            name="del_appuntamento"),
                        url(r'^pymobile/appuntamento/add/popup:add-(?P<field_name>\w+)/$', 
                            "appuntamento.admin.add_child_object", 
                            name="add_fk"),
                        url(r'^pymobile/appuntamento/(?P<object_id>\d+)/$', 
                            object_detail, INFO_APP, 
                            name="view_appuntamento"),
                        url(r'^pymobile/appuntamento/(?P<object_id>\d+)/mail/$', 
                            "appuntamento.admin.send_mail_to_agente", 
                            name="send_mail_appuntamento"),
                        url(r'^pymobile/appuntamento/assign/$', 
                            "appuntamento.admin.assign_object", 
                            name="assign_appuntamento"),
                        url(r'^pymobile/appuntamento/(?P<object_id>\d+)/referente/(?P<referente_id>\d+)/$', 
                            "appuntamento.admin.view_referente", 
                            name="view_referente"), 
                        url(r'^pymobile/appuntamento/(?P<object_id>\d+)/referente/(?P<referente_id>\d+)/mod/$', 
                            "appuntamento.admin.mod_referente", 
                            name="mod_referente"), 
                        url(r'^pymobile/appuntamento/(?P<object_id>\d+)/referente/del/$', 
                            "appuntamento.admin.del_referente", 
                            name="del_referente"),)

# contratto
urlpatterns += patterns('pymobile.administration.views',
                        url(r'^pymobile/contratto/$', "contratto.admin.init", 
                            name="init_contratto"),
                        url(r'^pymobile/contratto/add/$', "contratto.admin.add_object", 
                            name="add_contratto"),
                        url(r'^pymobile/contratto/mod/(?P<object_id>\d+)/$', 
                            "contratto.admin.mod_object", 
                            name="mod_contratto"),
                        url(r'^pymobile/contratto/del/$', 
                            "contratto.admin.del_object", 
                            name="del_contratto"),
                        url(r'^pymobile/contratto/add/popup:add-(?P<field_name>\w+)/$', 
                            "contratto.admin.add_child_object", 
                            name="add_contratto_fk"),
                        url(r'^pymobile/contratto/(?P<object_id>\d+)/$', 
                            object_detail, INFO_CON, 
                            name="view_contratto"),)

#-------------------------------------------------------------------------------
# STATISTICHE
# contratto
INFO_OBI={"template_name": "statistiche/obiettivo_trimestrale_view.html", 
          "queryset": models.Obiettivo.objects.all()}

urlpatterns += patterns('django.views.generic.simple',
                        url(r'^pymobile/statistiche/$', 
                            "direct_to_template", 
                            {"template": "statistiche/statistiche.html"},
                            name="init_statistiche"),)

# canvas
urlpatterns += patterns('pymobile.administration.views.reports',
                        url(r'^pymobile/statistiche/classifiche/canvas/$', 
                            "rankings.canvas_tim_telecom", 
                            name="canvas_tim_telecom"),
                        url(r'^pymobile/statistiche/classifiche/canvas/$', 
                            "rankings.canvas_edison", 
                            name="canvas_edison"),)

# entrate uscite
urlpatterns += patterns('pymobile.administration.views.reports',
                        url(r'^pymobile/statistiche/finanze/inout/$', 
                            "business.inout", 
                            name="inout"),)

# Obiettivi
urlpatterns += patterns('pymobile.administration.views.reports',
                        url(r'^pymobile/statistiche/obiettivi/$', 
                            "goals.canvas_obiettivo_trimestrale", 
                            name="canvas_obiettivo_trimestrale"),
                        url(r'^pymobile/statistiche/obiettivi/admin/$', 
                            "goals.init_obiettivo_trimestrale", 
                            name="init_obiettivo_trimestrale"),
                        url(r'^pymobile/statistiche/obiettivi/admin/add/$', 
                            "goals.add_obiettivo_trimestrale", 
                            name="add_obiettivo_trimestrale"),
                        url(r'^pymobile/statistiche/obiettivi/admin/mod/(?P<object_id>\d+)/$', 
                            "goals.mod_obiettivo_trimestrale", 
                            name="mod_obiettivo_trimestrale"),
                        url(r'^pymobile/statistiche/obiettivi/admin/del/$', 
                            "goals.del_obiettivo_trimestrale", 
                            name="del_obiettivo_trimestrale"),
                        url(r'^pymobile/statistiche/obiettivi/admin/(?P<object_id>\d+)/$', 
                            object_detail, INFO_OBI, 
                            name="view_obiettivo_trimestrale"),)
                            