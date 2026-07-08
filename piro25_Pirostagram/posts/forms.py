from django import forms

from .models import Comment, Post


class PostCreateForm(forms.ModelForm):
    image = forms.ImageField(
        label="게시글 이미지",
        required=True,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-file-input",
            }
        ),
    )

    class Meta:
        model = Post
        fields = [
            "content",
        ]

        labels = {
            "content": "내용",
        }

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "text-input",
                    "placeholder": "문구를 입력하세요.",
                    "rows": 5,
                }
            ),
        }


class PostUpdateForm(forms.ModelForm):
    image = forms.ImageField(
        label="새 이미지",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-file-input",
            }
        ),
    )

    class Meta:
        model = Post
        fields = [
            "content",
        ]

        labels = {
            "content": "내용",
        }

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "text-input",
                    "placeholder": "문구를 입력하세요.",
                    "rows": 5,
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = [
            "content",
        ]

        labels = {
            "content": "",
        }

        widgets = {
            "content": forms.TextInput(
                attrs={
                    "placeholder": "댓글 달기...",
                    "autocomplete": "off",
                }
            ),
        }