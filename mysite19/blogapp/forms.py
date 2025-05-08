
from django.forms import (CharField, ModelForm, Select, TextInput,
                          ValidationError)

from .models import Article, Author, Category


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ("name", "bio",)

class ArticleForm(ModelForm):
    new_category = CharField(
        max_length=40,
        required=True,
        widget=TextInput(attrs={'placeholder': 'Впишите категорию'}),
    )

    new_tags = CharField(
        max_length=20,
        required=False,
        widget=TextInput(attrs={'placeholder': 'Впишите тэги через запятую'}),
        help_text="Если тэг существует, он будет использован."
    )

    class Meta:
        model = Article
        fields = ('title', 'content', 'author',)
        widgets = {
            "author": Select(),
        }

    def clean_new_category(self):
        name = self.cleaned_data['new_category'].strip()
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("Категория с таким названием уже существует.")
        return name