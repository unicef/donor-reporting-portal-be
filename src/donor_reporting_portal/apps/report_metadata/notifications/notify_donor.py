from unicef_notification.utils import strip_text

name = "notify_donor"
defaults = {
    "description": "Notify Donor",
    "subject": "Updated reports available in DRP",
    "content": strip_text("""Dear user,

    Following reports have been updated in DPR:

    {% for report in reports %}
        {{ report.title }} {{ report.download_url }}
    {% endfor %}
    Regards.
    """),
    "html_content": """Dear user,<br/><br/>

    Following reports have been updated in DPR:
    <br/><br/>
    {% for report in reports %}
        <a href="{{ report.download_url }}>{{ report.title }}</a><br/>
    {% endfor %}
    <br/><br/>
    Regards.
    """,
}
