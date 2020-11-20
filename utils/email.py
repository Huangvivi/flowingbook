from flowingbook import mail
from flask_mail import Message
from flask import current_app, render_template
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(e)
            pass


def send_mail(to, subject, template, **kwargs):
    message = Message(subject=subject, sender=current_app.config['MAIL_USERNAME'],
                      recipients=[to])
    message.html = render_template(template, **kwargs)
    # send_mail(message)
    app = current_app._get_current_object()
    t = Thread(target=send_async_email, args=[app, message])
    t.start()

