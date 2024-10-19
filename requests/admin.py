from django.contrib import admin
from .models import *

# Inline для добавления медиафайлов прямо на странице заявки
class MediaFileInline(admin.TabularInline):
    model = MediaFile
    extra = 1  # Количество пустых полей для загрузки файлов
    fields = ['file', 'media_type']  # Какие поля показывать в инлайне
    verbose_name = "Медиа файл"
    verbose_name_plural = "Медиа файлы"

# Админка для модели Application (Заявка)
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('creator', 'category', 'status', 'created_at')  # Отображаемые поля в списке заявок
    list_filter = ('status', 'category', 'created_at')  # Фильтры по статусу, категории и дате создания
    search_fields = ('creator', 'description')  # Поиск по создателю и тексту заявки
    inlines = [MediaFileInline]  # Инлайн для медиафайлов
    readonly_fields = ('created_at',)  # Поле, которое нельзя редактировать
    fieldsets = (
        (None, {
            'fields': ('creator', 'category', 'description', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),  # Дополнительные поля можно свернуть
        }),
    )
    
# Админка для модели Category (Категория)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'resolution_days', 'responsible_person')
    search_fields = ('name',)  # Поиск по названию категории

# Админка для модели MediaFile (Медиа файл)
@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('application', 'media_type', 'file')  # Отображаемые поля в списке медиафайлов
    list_filter = ('media_type',)  # Фильтр по типу медиа (фото или видео)
    search_fields = ('application__creator',)  # Поиск по заявкам и их создателям

class MessageTemplateAdmin(admin.ModelAdmin):
    # Какие поля отображать в списке
    list_display = ('category', 'short_message')

    # Добавляем возможность фильтрации по категориям
    list_filter = ('category',)

    # Добавляем поиск по тексту сообщений
    search_fields = ('message',)

    # Функция для сокращенного отображения сообщения в списке
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Сообщение'

# Регистрируем модель с кастомной админкой
admin.site.register(MessageTemplate, MessageTemplateAdmin)
