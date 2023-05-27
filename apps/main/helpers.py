from django.core.mail import send_mail
from django.contrib.auth import get_user_model


User = get_user_model()


def send_spam(new_product):
    users_email = [x.email for x in User.objects.all()]
    message = f"""
У нас появился новый продукт

{new_product.title}

{new_product.description}
"""
    send_mail(
        subject="Новинка",
        message=message,
        from_email="a@gmail.com",
        recipient_list=users_email
    )