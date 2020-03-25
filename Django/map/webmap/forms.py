from django import forms

travel_options = [
    ('driving', 'Driving'),
    ('walking', 'Walking'),
    ('train', 'Train'),
    ('bus','Bus')
]

cost_options = [
    ('9999', 'Least Transfer'),
    ('0', 'Shortest Route')
]

class HomeForm(forms.Form):
    travel = forms.CharField(label='', widget=forms.Select(choices=travel_options, attrs={'onchange':"showOptions()"}))
    start = forms.CharField(label= '', widget= forms.TextInput(attrs={'id':'start','class':'travelsearch','placeholder':'Choose starting point...','onchange':"checkStartMap()"}))
    end = forms.CharField(label='', widget = forms.TextInput(attrs={'id':'end','class':'travelsearch','placeholder':'Choose destination...','onchange':"checkEndMap()"}))
    cost_per_transfer = forms.CharField(label='Options', widget=forms.Select(choices=cost_options, attrs={'onchange':"showOptions()"}))
    