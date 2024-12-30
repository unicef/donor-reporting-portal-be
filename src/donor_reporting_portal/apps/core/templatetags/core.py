from django import template

from donor_reporting_portal import NAME, VERSION

register = template.Library()


@register.simple_tag
def version():
    return f"{NAME}: v{VERSION}"
