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
    image = models.ImageField(
        upload_to="ideas/",
        blank=True, 
        null=True,
    )
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey(
        DevTool,
        on_delete=models.CASCADE,
        related_name="ideas"
    )

class IdeaStar(models.Model):
    idea = models.OneToOneField("Idea", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
