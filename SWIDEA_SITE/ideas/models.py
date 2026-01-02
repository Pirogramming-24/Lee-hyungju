from django.db import models

# Create your models here.
class DevTool(models.Model):
    name = models.CharField(max_length=32)
    kind = models.CharField(max_length=64)
    content = models.TextField()

    def __str__(self):
        return self.name

class Idea(models.Model):
    title = models.CharField(max_length=32)
    # TODO ImageField 더 설정하기
    image = models.ImageField(blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField()
    devTool = models.ForeignKey(
        DevTool,
        on_delete=models.CASCADE,
        related_name="ideas"
    )

