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

    # 영양정보
    nutrition_facts_photo = models.ImageField('영양성분 이미지', blank=True, null=True, upload_to='posts/nutrition_facts/%Y%m%d')
    calorie = models.IntegerField('칼로리(Kcal)', blank=True, null=True, default=0)
    carbonhydrate = models.FloatField('탄수화물(g)', blank=True, null=True, default=0)
    protein = models.FloatField('단백질(g)', blank=True, null=True, default=0)
    fat = models.FloatField('지방(g)', blank=True, null=True, default=0)

    def save(self, *args, **kwargs):
        if self.pk:  # 수정일 때에만 갱신
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class NutritionOCRJob(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAIL = "FAIL"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAIL, "Fail"),
    ]

    image = models.ImageField(upload_to="nutrition_ocr/")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    result = models.JSONField(null=True, blank=True)  # {"kcal":..., "carb_g":..., ...}
    error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
