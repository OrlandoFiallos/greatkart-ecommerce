from django.db import models
from django.utils.text import slugify 
from django.urls import reverse

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(max_length=255, blank=True)
    category_image = models.ImageField(upload_to='photos/categories',blank=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self) -> str:
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)
    
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])