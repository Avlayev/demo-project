import threading
from decouple import config

from twilio.rest import Client
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
import phonenumbers
import threading
from django.core.mail import EmailMessage


class EmailThread(threading.Thread):

    def init(self, email):
        self.email = email
        threading.Thread.init(self)

    def run(self):
        self.email.send()


def send_phone_notification(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Hello everyone! Your verification code is {code}\n",
        from_="+997854521",
        to=f"{phone}"
    )

class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data["to_email"]]
        )
        if data.get('content_type') == "html":
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code": code}
    )
    Email.send_email({
        "subject": "Registration",
        "to_email": email,
        "body": html_content,
        "content_type": "html"
    })


def phone_checker(p_number):
    if not (p_number and isinstance(p_number, str) and p_number.isdigit()):
        raise ValidationError("phone_number is not valid")


def phone_parser(p_number, c_code=None):
    try:
        phone_checker(p_number)
        p_number = '+' + p_number
        return phonenumbers.parse(p_number, c_code)
    except Exception as e:
        raise ValidationError("Phone number is not valid")