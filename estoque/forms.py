
from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto
        fields = ['identificacao']

        widgets = {
            'identificacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PROD-001'
            })
        }


class OperacaoForm(forms.Form):

    produto = forms.ModelChoiceField(
        queryset=Produto.objects.all(),
        label="Produto",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Informe a quantidade'
        })
    )

    identificacao = forms.CharField(
        max_length=50,
        required=False,
        label="Identificação da operação",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opcional: gerada automaticamente'
        })
    )


class LiberacaoForm(forms.Form):

    identificacao = forms.CharField(
        max_length=50,
        label="Identificação da reserva ou bloqueio",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: RES-000001'
        })
    )
