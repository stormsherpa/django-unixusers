
import uuid

from django.template.loader import render_to_string

def send_email_validation(user):
    user.email_validation_code = str(uuid.uuid4())
    user.save()
    email_body = render_to_string('django_unixusers/email/validate.html', {'user': user})
    user.email_user("Validate your email", email_body)
