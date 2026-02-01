from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class LearnItem(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  
    content_name = models.TextField(blank=True, null=True)
    object_image = models.ImageField(upload_to='learn_items/objects/', blank=True, null=True)
    audio = models.FileField(upload_to='learn_items/audio/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['category', 'order']),
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    