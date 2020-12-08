from django import template
from django.utils.safestring import mark_safe

from donor_reporting_portal import NAME, VERSION

register = template.Library()


@register.simple_tag
def version():
    return mark_safe('{}: v{}'.format(NAME, VERSION))
