from django.apps import apps
from django.contrib import admin

post_models = apps.get_app_config('core').get_models()

for model in post_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass