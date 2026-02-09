from django.db import models
from django.utils.text import slugify

from .services import (
    generate_color_image,
    get_category_translation,
    normalize_color,
    validate_object_fields,
)


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


LEARN_CATEGORY_ALL_SECTIONS = LearnCategory.choices


class CategoryConfig(models.Model):
    category = models.PositiveSmallIntegerField(
        choices=LEARN_CATEGORY_ALL_SECTIONS,
        unique=True,
    )
    name = models.CharField(max_length=255)
    name_ne = models.CharField(max_length=255, blank=True, null=True)
    name_hi = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, allow_unicode=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            if not self.name_ne or not self.name_hi:
                translated_ne, translated_hi = get_category_translation(self.name)
                if not self.name_ne and translated_ne:
                    self.name_ne = translated_ne
                if not self.name_hi and translated_hi:
                    self.name_hi = translated_hi
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class LearnItem(models.Model):
    category = models.ForeignKey(
        CategoryConfig,
        to_field='category',
        on_delete=models.CASCADE,
        related_name='items',
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
        category_name = self.category.name if self.category_id else None
        fallback = str(self.category_id) if self.category_id is not None else "Unknown"
        return f"{category_name or fallback} - {self.name}"

    def clean(self):
        super().clean()
        validate_object_fields(self.object_image, self.object_color)

    def save(self, *args, **kwargs):
        if self.name:
            self.slug = slugify(self.name, allow_unicode=True)
        self.full_clean()
        if self.object_color:
            normalized = normalize_color(self.object_color)
            self.object_color = normalized

            if not self.object_image:
                safe_name = slugify(self.name) or "item"
                filename = f"{safe_name}_{normalized[1:]}.png"
                self.object_image.save(
                    filename,
                    generate_color_image(normalized),
                    save=False,
                )

        super().save(*args, **kwargs)
    
    