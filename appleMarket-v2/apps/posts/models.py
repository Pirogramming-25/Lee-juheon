from django.db import models
from django.utils import timezone
from apps.users.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField('제목', max_length=20)
    content = models.CharField('내용', max_length=20)
    region = models.CharField('지역', max_length=20)
    user = models.ForeignKey(User, verbose_name='작성자', on_delete=models.CASCADE)
    price = models.IntegerField('가격', default=1000)
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', null=True, blank=True)
    photo = models.ImageField('이미지', blank=True, upload_to='posts/%Y%m%d')

    # 영양 성분 OCR 관련 필드
    nutrition_photo = models.ImageField('영양성분 이미지', blank=True, null=True, upload_to='nutrition/%Y%m%d')
    calorie = models.FloatField('칼로리(kcal)', blank=True, null=True)
    carbohydrate = models.FloatField('탄수화물(g)', blank=True, null=True)
    protein = models.FloatField('단백질(g)', blank=True, null=True)
    fat = models.FloatField('지방(g)', blank=True, null=True)

    # 상품 자동 해시태깅 관련 필드
    hashtags = models.CharField('상품 종류 해시태그', max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:  # 수정일 때에만 갱신
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)