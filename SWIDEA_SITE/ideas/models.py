from django.db import models


class DevTool(models.Model):
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.name


class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ideas/', blank=True, null=True)
    content = models.TextField()
    interest = models.PositiveIntegerField(default=0)
    devtool = models.ForeignKey(
        DevTool,
        on_delete=models.CASCADE,
        related_name='ideas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class IdeaStar(models.Model):
    idea = models.OneToOneField(
        Idea,
        on_delete=models.CASCADE,
        related_name='star'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.idea.title} 찜'