# -*- coding: utf-8 -*-

'''
Created on 31/mar/2012

@author: luigi
'''
from django.http import HttpResponse
from pymobile.administration.views.account.admin import logout_user, logout_user_ajax
import datetime
from django.contrib import messages
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

class timeOutSessionMiddleware(object):
    # FIXME: controllare come fa scadere la sessione anche su richieste ajax
    def process_request(self, request):
        if request.user and request.user.is_authenticated():
            now = datetime.datetime.now()
            if (request.session.has_key("last_activity") and
                (now - request.session["last_activity"]).seconds > 900):
                if request.is_ajax():
                    # sessione scade dopo 15 minuti di inattività
                    logger.debug("{}: sessione scaduta".format(request.user)) 
                    messages.add_message(request, messages.ERROR, 'Sessione scaduta')
                    return logout_user_ajax(request)
                else:
                    # sessione scade dopo 15 minuti di inattività
                    logger.debug("{}: sessione scaduta".format(request.user)) 
                    messages.add_message(request, messages.ERROR, 'Sessione scaduta')  
                    return logout_user(request)
            else:
                request.session["last_activity"] = now
                            
        return None
    