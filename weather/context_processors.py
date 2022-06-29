from django.conf import settings

# Pass environment variables to base.html (and all templates)
def environ_vars_processor(request):
    vars = {
        'google_api_key': settings.GOOGLE_API_KEY,
    }
    return vars
