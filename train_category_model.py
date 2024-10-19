import os
import django

# Установите переменную окружения для настроек вашего проекта Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urban_alert.settings')

# Инициализируйте Django
django.setup()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from collections import Counter
import joblib

from requests.models import *

categories = []
messages = []

for category in Category.objects.all():
    templates = category.templates.all()
    for template in templates:
        categories.append(category.name)
        messages.append(template.message)

# Преобразование текста в числовое представление
vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.9)

# Преобразуем сообщения в числовой вид
X = vectorizer.fit_transform(messages)

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, categories, test_size=0.2, random_state=42)

# Вывод размера выборок
print(f"Размер тренировочной выборки: {len(X_train.toarray())}")
print(f"Размер тестовой выборки: {len(X_test.toarray())}")

# Проверка баланса классов
print("Баланс классов в тренировочной выборке:", Counter(y_train))
print("Баланс классов в тестовой выборке:", Counter(y_test))

# Обучение модели
model = LogisticRegression()
model.fit(X_train, y_train)

# Прогнозирование на тестовых данных
y_pred = model.predict(X_test)

# Оценка точности
accuracy = accuracy_score(y_test, y_pred)
print(f"Точность модели: {accuracy * 100:.2f}%")

# Сохранение модели и векторизатора
joblib.dump(model, 'category_classifier_model.pkl')
joblib.dump(vectorizer, 'category_vectorizer.pkl')
print("Модель и векторизатор сохранены.")


## how to solve is text 