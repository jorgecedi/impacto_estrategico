from django import forms
from bootstrap_datepicker.widgets import DatePicker
from .models import Sitio

class CsvForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")
    start_date = forms.DateTimeField(label="Fecha de inicio",
                                     required=False,
    )
    end_date = forms.DateTimeField(label="Fecha final",
                                   required=False,
    )
    STATUS_CHOICES = (
        (0, "ALL"),
        (1, "UP"),
        (2, "DOWN"),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    url = forms.ModelChoiceField(queryset=Sitio.objects.all(),
                                 label="URL",
                                 to_field_name="url",
                                 required=False)

