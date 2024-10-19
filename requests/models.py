from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_file_type(value):
    # Ограничение типов файлов для видео
    if not value.name.endswith(('.mp4', '.mov', '.avi')):
        raise ValidationError('Неподдерживаемый формат видео. Допустимые форматы: .mp4, .mov, .avi')

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    resolution_days = models.IntegerField(verbose_name="Количество рабочих дней на решение", default=5)
    responsible_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ответственный")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Application(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Категория")
    creator = models.CharField(max_length=100, verbose_name="Создатель")
    telegram_id = models.CharField(max_length=50, verbose_name="Telegram ID", null=True, blank=True)  
    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name="Дата создания")
    
    # Поле для текста заявки
    description = models.TextField(verbose_name="Текст заявки", null=True, blank=True)

    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'

    STATUS_CHOICES = [
        (DRAFT, 'Черновик'),
        (APPROVED, 'Одобрена'),
        (DECLINED, 'Отказано')
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.creator} в категории {self.category}"

    @property
    def is_approved(self):
        return self.status == self.APPROVED

    @property
    def is_declined(self):
        return self.status == self.DECLINED

class MediaFile(models.Model):
    APPLICATION_MEDIA_TYPE_CHOICES = [
        ('photo', 'Фото'),
        ('video', 'Видео'),
    ]

    application = models.ForeignKey(Application, related_name='media_files', on_delete=models.CASCADE, verbose_name="Заявка")
    file = models.FileField(upload_to='', verbose_name="Файл")
    media_type = models.CharField(max_length=10, choices=APPLICATION_MEDIA_TYPE_CHOICES, verbose_name="Тип медиа")
    
    class Meta:
        verbose_name = "Медиа файл"
        verbose_name_plural = "Медиа файлы"

    def __str__(self):
        return f"{self.media_type} для заявки {self.application.id}"

    def clean(self):
        # Валидация на тип файла в зависимости от media_type
        if self.media_type == 'photo' and not self.file.name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError('Неправильный формат изображения. Допустимые форматы: .jpg, .jpeg, .png')
        elif self.media_type == 'video' and not self.file.name.endswith(('.mp4', '.mov', '.avi')):
            raise ValidationError('Неправильный формат видео. Допустимые форматы: .mp4, .mov, .avi')


class MessageTemplate(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='templates')
    message = models.TextField()

    def __str__(self):
        return f"{self.category.name}: {self.message[:50]}"
    
    class Meta:
        verbose_name = "База для обучения"
        verbose_name_plural = "База для обучения"