# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages

import pymobile.administration.utils as u
import pymobile.administration.forms as forms
import json
import os
from pymobile.settings import PROJECT_ROOT_PATH
import logging

# Get an instance of a logger
logger = logging.getLogger("file")

TMP_INIT="opzioni/admin.html"
TMP_FORM="opzioni/modelform.html"

DEFAULT_OPTS=["email_titolare", "provvigione_bonus_agente", "provvigione_bonus_telefonista",]
JSON_FILE_PATH=PROJECT_ROOT_PATH + "/administration/opzioni_default.json"

def get_default_options():
    if not os.path.isfile(JSON_FILE_PATH):
        json_data = {}
        for k in DEFAULT_OPTS:
            json_data[k] = ""
        opts = json.dumps(json_data, indent=4,)
        json_file = open(JSON_FILE_PATH, "w+")
        json_file.write(opts)
        json_file.close()

    json_file = open(JSON_FILE_PATH, "r")
    json_data = json_file.read()
    json_file.close()

    opts = json.loads(json_data)
    return opts

def get_default_options_list():
    opts = get_default_options()
    return [(k, opts[k]) for k in DEFAULT_OPTS]

def set_default_options(opts):
    json_file = open(JSON_FILE_PATH, "w+")
    json_file.write(opts)
    json_file.close()   

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def init(request):
    template = TMP_INIT
    
    opts = get_default_options_list()
    
    data = {"opts": opts,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda user: not u.is_telefonista(user),)
def mod_object(request):
    template = TMP_FORM

    opts = get_default_options()
    
    if request.method == "POST":
        post_query = request.POST.copy()
        form = forms.OpzioneForm(post_query)
        
        if form.is_valid():
            opts = json.dumps(form.cleaned_data, indent=4,)
            set_default_options(opts)
            
            logger.debug("{}: modificate le opzioni iniziali"
                         .format(request.user))
            messages.add_message(request, messages.SUCCESS, 'Opzioni iniziali modificate')
            return HttpResponseRedirect(reverse("init_opzione"))
    else:
        form = forms.OpzioneForm(initial=opts)    
        
    data = {"modelform": form,}                
    return render_to_response(template, 
                              data,
                              context_instance=RequestContext(request))
