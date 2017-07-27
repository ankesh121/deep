from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings

# import datetime
import os


register = template.Library()


@register.simple_tag
def watchful_static_url(path):
    if getattr(settings, 'AWS_QUERYSTRING_AUTH', False):
        # TODO: Remove later, use AWS cache timer
        return static(path) + '&modified_date_time=' +\
                str(os.path.getmtime(os.path.join(
                    os.path.join(settings.BASE_DIR, 'static'), path)))
    return static(path) + '?modified_date_time=' +\
        str(os.path.getmtime(os.path.join(
                os.path.join(settings.BASE_DIR, 'static'), path)))
