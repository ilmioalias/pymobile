# -*- coding: utf-8 -*-

'''
Created on 31/mar/2012

@author: luigi
'''
from pymobile.administration.views.account.admin import logout_user
import datetime
from django.contrib import messages
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

class timeOutSessionMiddleware(object):
    # FIXME: controllare come fa scadere la sessione anche su richieste ajax
    def process_request(self, request):
        if not request.user:
            return None
        if request.user.is_authenticated():
            if 'lastRequest' in request.session:            
                elapsed_time = datetime.datetime.now() - \
                              request.session['lastRequest']
                if elapsed_time.seconds > 1 * 60:
                    # sessione scade dopo 15 minuti di inattività
                    del request.session['lastRequest']
                    logger.debug("{}: sessione scaduta".format(request.user)) 
                    messages.add_message(request, messages.SUCCESS, 'Sessione scaduta')  
                    logout_user(request)

            request.session['lastRequest'] = datetime.datetime.now()
        else:
            if 'lastRequest' in request.session:
                del request.session['lastRequest'] 

        return None