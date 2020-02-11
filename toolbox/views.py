__author__ = 'jblowe'

from django.shortcuts import render

from cspace_django_site.main import cspace_django_site
from toolbox.cswaMain import main
from toolbox.cswaUtils import downloadCsv
from toolbox.cswaHelpers import *
from common import cspace

webappconfig = cspace.getConfig(os.path.join(settings.BASE_DIR, 'config'), 'toolbox')

config = cspace_django_site.getConfig()
hostname = cspace.getConfigOptionWithSection(config,
                                             cspace.CONFIGSECTION_AUTHN_CONNECT,
                                             cspace.CSPACE_HOSTNAME_PROPERTY)

TITLE = 'Tools Available'


def direct(request):
    context = configure_common_tools({}, request, 'landing', webappconfig)
    context['hostname'] = webappconfig.get('connect', 'hostname')
    context['html'], context['elapsedtime'] = main(request, 'landing', {}, webappconfig)
    context['extra_nav'] = {'href': './', 'id': 'switchtool', 'name': 'Switch Tool'}
    return render(request, 'toolbox.html', context)


def toolbox(request, action):

    # here we explicitly (re-)initialize context, both global and per-tool
    context = configure_common_tools({}, request, action, webappconfig)

    if webappconfig == False:
        return render(request, 'toolbox.html', {'html': '<h1>toolbox.cfg not found</h1>'})

    # NB we convert the request dict into a 'real' dict
    form = {'tool': action}
    for r in request.POST.keys():
        form[r] = request.POST[r]

    context['html'], context['elapsedtime'] = main(request, action, form, webappconfig)

    if (action == 'packinglist' or action == 'governmentholdings'):
        if 'action' in form and form['action'] == 'Download as CSV':
            response = downloadCsv(form, webappconfig)
            if type(response) == type(' '):
                context['html'] += response
            else:
                return response

    context['extra_nav'] = {'href': './', 'id': 'switchtool', 'name': 'Switch Tool'}
    return render(request, 'toolbox.html', context)


