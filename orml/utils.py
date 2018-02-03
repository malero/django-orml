try:
    from django.db.models.loading import get_model as django_get_model
except ImportError:
    from django.apps import apps
    django_get_model = apps.get_model


def get_model(app_label, model_label=None):
    if model_label is None:
        app_label, model_label = app_label.split('.')[-2:]

    return django_get_model(app_label, model_label)
