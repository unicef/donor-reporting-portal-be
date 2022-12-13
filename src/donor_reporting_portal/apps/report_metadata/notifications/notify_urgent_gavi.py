from unicef_notification.utils import strip_text

name = "notify_urgent_gavi"
defaults = {
    "description": "Urgent: Notify GAVI Donor",
    "subject": "Urgent: Updated GAVI reports available in UNICEF DRP",
    "content": strip_text("""Dear user,

    The following CTNs have been uploaded in the UNICEF Reporting Portal:

    {% for report in reports %}
        MOU # {{ report.m_o_u_number }}
        CTN # {{ report.number }}
        Report: {{ report.download_url }}
        Country: {{ report.country_name }}
        Gavi WBS: {{ report.g_a_v_i_w_b_s }}
        Funds Due date: {{ report.funds_due_date|slice:"0:10" }}
        Vaccine type: {{ report.vaccine_type }}

    {% endfor %}

    In case you do not wish to receive this email or change the frequency, please contact your local site administrator.
    Please do not reply to this mail.  For any questions on these reports, please contact your UNICEF focal point.

    Regards.
    """),
    "html_content": """Dear user,<br/><br/>

    The following CTNs have been uploaded in the UNICEF Reporting Portal:
    <br/><br/>
    <table>
    <tr>
        <th>#</th>
        <th>MOU #</th>
        <th>CTN #</th>
        <th>Country</th>
        <th>Gavi WBS</th>
        <th>Funds Due date</th>
        <th>Vaccine type</th>
    </tr>
    {% for report in reports %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <td>{{ report.m_o_u_number }}</td>
            <td><a href="{{ report.download_url }}">{{ report.number }}</a></td>
            <td>{{ report.country_name }}</td>
            <td>{{ report.g_a_v_i_w_b_s }}</td>
            <td>{{ report.funds_due_date|slice:"0:10" }}</td>
            <td>{{ report.vaccine_type }}</td>
        </tr>
    {% endfor %}
    </table>
    <br/><br/>

    <p>
    In case you do not wish to receive this email or change the frequency, please contact your local site administrator.
    </p>
    <p>
    Please do not reply to this mail.  For any questions on these reports, please contact your UNICEF focal point.</p>

    Regards.
    """,
}
