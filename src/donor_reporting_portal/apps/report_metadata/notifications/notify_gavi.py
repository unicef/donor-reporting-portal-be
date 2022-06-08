from unicef_notification.utils import strip_text

name = "notify_donor"
defaults = {
    "description": "Notify GAVI Donor",
    "subject": "Updated GAVI reports available in UNICEF DRP",
    "content": strip_text("""Dear user,

    The following reports have been updated in the Donor Reporting Portal (drp.unicef.org).

    {% for report in reports %}
        {{ report.title }} [{{ report.external_reference }}]
        {{ report.download_url }}
        Grant: {{ report.grant_number }}
        Type: {{ report.report_type }}
        End date: {{ report.report_end_date|slice:"0:10" }}

    {% endfor %}

    You are receiving this system generated notification because of user setting in UNICEF’s Donor Reporting Portal.
    In case you do not wish to receive this email or change the frequency, please contact your local site administrator.
    Please do not reply. For any questions on the reports, please contact your UNICEF colleague.

    Regards.
    """),
    "html_content": """Dear user,<br/><br/>

    The following reports have been updated in the Donor Reporting Portal (drp.unicef.org).
    <br/><br/>
    <table>
    <tr>
        <th>#</th>
        <th>Report</th>
        <th>Reference No</th>
        <th>Category</th>
        <th>Grant No</th>
        <th>Report Type</th>
        <th>Report Date</th>
    </tr>
    {% for report in reports %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <td><a href="{{ report.download_url }}">{{ report.title }}</a></td>
            <td>{{ report.external_reference }}</td>
            <td>{{ report.donor_report_category }}</td>
            <td>{{ report.grant_number }}</td>
            <td>{{ report.report_type }}</td>
            <td>{{ report.report_end_date|slice:"0:10" }}</td>
        </tr>
    {% endfor %}
    </table>
    <br/><br/>

    <p>
    You are receiving this system generated notification because of user setting in UNICEF’s Donor Reporting Portal.
    </p>
    <p>
    In case you do not wish to receive this email or change the frequency, please contact your local site administrator.
    </p>
    <p>
    Please do not reply. For any questions on the reports, please contact your UNICEF colleague.</p>

    Regards.
    """,
}
