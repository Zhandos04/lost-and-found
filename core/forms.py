from django import forms
from .models import Item, Claim, Category

class DateInput(forms.DateInput):
    input_type = 'date'

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'date_lost_found', 'location', 'category', 'image', 'status', 'contact_info']
        widgets = {
            'date_lost_found': DateInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['description', 'proof', 'contact_info']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'proof': forms.Textarea(attrs={'rows': 4}),
        }

class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('all', 'Все'),
        ('lost', 'Утеряно'),
        ('found', 'Найдено'),
    )
    
    search_query = forms.CharField(label='Поиск', required=False, widget=forms.TextInput(attrs={'placeholder': 'Поиск...'}))
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.all(), required=False)
    status = forms.ChoiceField(label='Статус', choices=SEARCH_CHOICES, required=False)
    date_from = forms.DateField(label='Дата от', required=False, widget=DateInput())
    date_to = forms.DateField(label='Дата до', required=False, widget=DateInput())