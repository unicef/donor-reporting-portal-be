from unicef_notification.utils import strip_text

name = "notify_donor"
defaults = {
    "description": "Notify Donor",
    "subject": "Updated reports available in DRP",
    "content": strip_text("""Dear user,

    The following reports have been updated in the Donor Reporting Portal (drp.unicef.org).

    {% for report in reports %}
        {{ report.title }} [{{ report.external_reference }}]
        {{ report.download_url }}
        Grant: {{ report.grant_number }}
        Type: {{ report.report_type }}
        End date: {{ report.report_end_date|slice:"0:10" }}
        
    {% endfor %}
    Regards.
    """),
    "html_content": """Dear user,<br/><br/>

    The following reports have been updated in the Donor Reporting Portal (drp.unicef.org).
    <br/><br/>
    <table>
    <tr>
        <th>Report</th>
        <th>Reference No</th>
        <th>Grant No</th>
        <th>Report Type</th>
        <th>Report Date</th>
    </tr>
    {% for report in reports %}
        <tr>
            <td><a href="{{ report.download_url }}">{{ report.title }}</a></td>
            <td>{{ report.external_reference }}</td>
            <td>{{ report.grant_number }}</td>
            <td>{{ report.report_type }}</td>
            <td>{{ report.report_end_date|slice:"0:10" }}</td>
        </tr>
    {% endfor %}
    </table>
    <br/><br/>
    Regards.
    """,
}
