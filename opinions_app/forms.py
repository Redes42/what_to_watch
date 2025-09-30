from wtforms_alchemy import ModelForm

from opinions_app.models import Opinion


class OpinionForm(ModelForm):
    class Meta:
        model = Opinion

