from django.conf import settings # import the settings file

def ua_tracking_id(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'UA_TRACKING_ID': settings.UA_TRACKING_ID}
