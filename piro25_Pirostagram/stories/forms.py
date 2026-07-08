from django import forms


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            MultipleImageInput(
                attrs={
                    "multiple": True,
                    "accept": "image/*",
                }
            ),
        )

        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_image_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [
                single_image_clean(image, initial)
                for image in data
            ]

        return [
            single_image_clean(data, initial)
        ]


class StoryCreateForm(forms.Form):
    images = MultipleImageField(
        label="스토리 이미지",
        help_text="최대 10장까지 선택할 수 있습니다.",
    )

    def clean_images(self):
        images = self.cleaned_data["images"]

        if len(images) > 10:
            raise forms.ValidationError(
                "스토리 이미지는 한 번에 최대 10장까지 업로드할 수 있습니다."
            )

        for image in images:
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    f"{image.name} 파일은 10MB를 초과합니다."
                )

        return images