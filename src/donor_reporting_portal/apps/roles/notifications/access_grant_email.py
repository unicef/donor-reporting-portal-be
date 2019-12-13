from unicef_notification.utils import strip_text

name = "access_grant_email"
defaults = {
    "description": "Access to UNICEF Donor Reporting Portal",
    "subject": "Access to UNICEF Donor Reporting Portal",
    "content": strip_text("""Dear {{ instance.first_name }},

    You have been granted access to UNICEF Donor Reporting Portal.

    Please registry at {{home_link}} and feel free to login in the system,
    username is your e-mail address provided at the time of account registration.

    Thank you.
    """),
    "html_content": """Dear {{ instance.first_name }},<br/><br/>

    You have been granted access to UNICEF Donor Reporting Portal.<br/><br/>

    Please registry <a href="{{ home_link }}">here</a><br/><br/> and feel free to login in the system,<br/>
    username is your e-mail address provided at the time of account registration.<br/><br/>

    Thank you.
    """,
}
