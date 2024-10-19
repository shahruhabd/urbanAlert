import os
import django

# Установите путь к файлу настроек вашего проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urban_alert.settings')

# Инициализируем Django
django.setup()

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

import joblib

from requests.models import Application, MediaFile, Category

TOKEN = '7960660894:AAGoRHgen3grTxr5Gl5a1tuXBf4rSQyZI40'

# Загрузка обученной модели и векторизатора
model = joblib.load('message_classifier_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

category_model = joblib.load('category_classifier_model.pkl')
category_vectorizer = joblib.load('category_vectorizer.pkl')

# Список адресов
KNOWN_ADDRESSES = [
    'Абая',
    'Абылай хана',
    'Айвазовского',
    'Айтеке би',
    'Айтиева',
    'Алексеева',
    'Амангельды',
    'Аносова',
    'Аносова',
    'Аренского',
]

# Функция для проверки наличия адреса в сообщении
def contains_address(message_text):
    for address in KNOWN_ADDRESSES:
        if address.lower() in message_text.lower():
            return True
    return False

# Функция для определения категории по тексту
def predict_category(message_text):
    message_vec = category_vectorizer.transform([message_text])
    predicted_category = category_model.predict(message_vec)[0]
    return predicted_category

# Функция для классификации сообщения
def is_issue_related(message):
    message_vec = vectorizer.transform([message])
    prediction = model.predict(message_vec)
    return prediction[0] == 1

# Функция для обработки фото с текстом
def handle_photo_or_video(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = update.message.from_user
    message_text = update.message.caption  # Текст, прикрепленный к фото
    photos = update.message.photo  # Фотографии
    videos = update.message.video 
    
    # Проверка наличия текста
    if not message_text:
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, добавьте текст к вашему сообщению.")
        return

    # Проверка наличия адреса в тексте
    if not contains_address(message_text):
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, укажите адрес из известного района в вашем сообщении.")
        return

    # Проверка наличия фото
    if not photos:
        context.bot.send_message(chat_id=chat_id, text="Пожалуйста, приложите хотя бы одно фото.")
        return

    print(f"Сообщение с медиафайлом от {user.username}: {message_text}")

    # Предсказание категории
    predicted_category_name = predict_category(message_text)
    category = Category.objects.filter(name=predicted_category_name).first()
    
    if not category:
        context.bot.send_message(chat_id=chat_id, text="Категория для этого сообщения не найдена.")
        return

    # Проверяем, связано ли сообщение с заявкой
    if is_issue_related(message_text):
        context.bot.send_message(chat_id=chat_id, text="Отправлено в CRM.")

    # Создаем заявку
    application = Application.objects.create(
        category=category,
        creator=user.username,
        telegram_id=user.id,
        description=message_text,
        status=Application.DRAFT
    )

    # Создание директории, если она не существует
    photo_directory = "media/photos/"
    if not os.path.exists(photo_directory):
        os.makedirs(photo_directory)

    # Сохранение фотографий
    if photos:
        largest_photo = photos[-1]
        telegram_file = context.bot.get_file(largest_photo.file_id)  # Получаем объект файла через Telegram API
        file_path = f"{largest_photo.file_id}.jpg"   # Определяем путь для сохранения файла
        
        # Сохранение файла локально
        telegram_file.download(f"media/photos/{file_path}")  
        
        # Сохранение в базе данных
        MediaFile.objects.create(
            application=application,
            file=f"photos/{file_path}",
            media_type='photo'
        )

    # Создание директории для видео, если она не существует
    video_directory = "media/videos/"
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # Сохранение видео
    if videos:
        telegram_file = context.bot.get_file(videos.file_id)  # Получаем объект файла видео
        file_path = f"{videos.file_id}.mp4"

        # Сохранение файла локально
        telegram_file.download(f"media/videos/{file_path}")

        # Сохранение в базе данных
        MediaFile.objects.create(
            application=application,
            file=f"videos/{file_path}",
            media_type='video'
        )

    # Формирование ссылки на страницу отслеживания
    application_link = f"http://127.0.0.1:8000/application-status/{application.id}/?telegram_id={user.id}"

    # Отправка сообщения пользователю с ссылкой
    context.bot.send_message(
        chat_id=user.id,
        text=f"Заявка создана в категории '{predicted_category_name}'.\n"
             f"Отслеживайте статус по ссылке: {application_link}"
    )

# Функция для запуска бота
def main():
    # Создаем объект Updater и передаем токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчера для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик для фото с текстом
    dp.add_handler(MessageHandler(Filters.photo | Filters.video, handle_photo_or_video))

    # Запускаем бота
    updater.start_polling()

    # Бот будет работать до тех пор, пока его не остановят
    updater.idle()

if __name__ == '__main__':
    main()
