import re
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from PIL import Image


class LearnCategory(models.IntegerChoices):
    SECTION_1 = 1, "Your first alphabets"
    SECTION_2 = 2, "Let's learn Nepali"
    SECTION_3 = 3, "Math is fun with us"
    SECTION_4 = 4, "Nepali months"
    SECTION_5 = 5, "English Months"
    SECTION_6 = 6, "7 days"
    SECTION_7 = 7, "4 seasons"
    SECTION_8 = 8, "Colors"
    SECTION_9 = 9, "Animals"
    SECTION_10 = 10, "Human Body"
    SECTION_11 = 11, "Birds"
    SECTION_12 = 12, "Punctuation Marks"
    SECTION_13 = 13, "World meaning"
    SECTION_14 = 14, "Shapes"


class CategoryConfig(models.Model):
    category = models.PositiveSmallIntegerField(
        choices=LearnCategory.choices,
        primary_key=True,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, allow_unicode=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class LearnItem(models.Model):
    category = models.PositiveSmallIntegerField(
        choices=LearnCategory.choices,
        db_column='category_id',
    )
    name = models.CharField(max_length=100)  
    slug = models.SlugField(max_length=120, blank=True, allow_unicode=True)
    content_name = models.TextField(blank=True, null=True)
    object_image = models.ImageField(upload_to='learn_items/objects/', blank=True, null=True)
    object_color = models.CharField(max_length=7, blank=True, null=True)
    audio = models.FileField(upload_to='learn_items/audio/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['category', 'order']),
        ]

    def __str__(self):
        category_name = (
            CategoryConfig.objects.filter(category=self.category)
            .values_list('name', flat=True)
            .first()
        )
        fallback = None
        try:
            fallback = LearnCategory(self.category).label
        except ValueError:
            fallback = str(self.category)

        return f"{category_name or fallback} - {self.name}"

    def _normalize_color(self, value: str) -> str:
        value = value.strip()
        color_re = re.compile(r"^#?[0-9a-fA-F]{3}$|^#?[0-9a-fA-F]{6}$")
        if not color_re.match(value):
            raise ValidationError({"object_color": "Invalid color code."})

        if not value.startswith('#'):
            value = f"#{value}"

        if len(value) == 4:
            value = f"#{value[1]}{value[1]}{value[2]}{value[2]}{value[3]}{value[3]}"

        return value.lower()

    def _generate_color_image(self, hex_color: str) -> ContentFile:
        image = Image.new("RGB", (512, 512), hex_color)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())

    def clean(self):
        super().clean()
        if self.object_image and self.object_color:
            raise ValidationError(
                {
                    "object_image": "Provide either object image or object color, not both.",
                    "object_color": "Provide either object image or object color, not both.",
                }
            )

    def save(self, *args, **kwargs):
        if self.name:
            self.slug = slugify(self.name, allow_unicode=True)
        self.full_clean()
        if self.object_color:
            normalized = self._normalize_color(self.object_color)
            self.object_color = normalized

            if not self.object_image:
                safe_name = slugify(self.name) or "item"
                filename = f"{safe_name}_{normalized[1:]}.png"
                self.object_image.save(
                    filename,
                    self._generate_color_image(normalized),
                    save=False,
                )

        super().save(*args, **kwargs)
    
    