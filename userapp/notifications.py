from userapp.models import UserNotification


def notify_user(user_sno, kind, title, body='', link=''):
    if user_sno is None:
        return None
    return UserNotification.objects.create(
        user_sno=user_sno,
        kind=kind,
        title=title,
        body=body,
        link=link,
    )
