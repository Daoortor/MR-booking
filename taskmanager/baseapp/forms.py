from django import forms


class SlotForm(forms.Form):
    room = forms.ChoiceField(choices=[tuple([i, 'MR' + str(i)]) for i in range(1, 8)])
    slot = forms.ChoiceField(choices=[(1, '16:40-17:20'), (2, '17:30-18:10'), (3, '18:20-19:00'), (4, '19:20-20:00'),
                                      (5, '20:10-20:50')])


class AuthForm(forms.Form):
    username = forms.CharField(max_length=32, help_text='Логин', widget=forms.TextInput(attrs={
        'style': 'width: 250px; margin-left: 152px; margin-top: 13px; height: 23px;', 'placeholder': 'Логин'}))
    password = forms.CharField(max_length=32, help_text='Пароль', widget=forms.TextInput(attrs={
        'type': 'password', 'style': 'width: 250px; margin-left: 152px; margin-top: 5px; height: 23px;',
        'placeholder': 'Пароль'}))


class RegForm(forms.Form):
    username = forms.CharField(max_length=32, help_text='Логин', widget=forms.TextInput(attrs={
        'style': 'width: 250px; margin-left: 152px; margin-top: 13px; height: 23px;', 'placeholder': 'Логин'}))
    password = forms.CharField(max_length=32, help_text='Пароль', widget=forms.TextInput(attrs={
        'type': 'password', 'style': 'width: 250px; margin-left: 152px; margin-top: 5px; height: 23px;',
        'placeholder': 'Пароль'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'style': 'width: 250px; margin-left: 152px; margin-top: 5px; height: 23px;', 'placeholder': 'Email'}))


class CodeForm(forms.Form):
    code = forms.IntegerField(max_value=999999, widget=forms.TextInput(attrs={
        'style': 'align: center; height: 27px;', 'placeholder': 'Код подтверждения'}))
