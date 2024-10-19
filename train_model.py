from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

# Расширенный набор данных
messages = [
    # Сообщения, связанные с заявками
    "Не вывозят мусор второй день",  # 1
    "На улице яма, опасно",  # 1
    "Освещение не работает уже неделю",  # 1
    "Двор не убран, повсюду мусор",  # 1
    "Падение деревьев во дворе, аварийное состояние",  # 1
    "Проблемы с водой, прорыв труб",  # 1
    "Не убраны улицы после сильного ветра",  # 1
    "На улице отключили электричество",  # 1
    "Необходимо ремонтировать дорожное покрытие",  # 1

    # Сообщения, не связанные с заявками
    "Здравствуйте, как у вас дела?",  # 0
    "Когда состоится встреча?",  # 0
    "Как проехать на Сейфуллина?",  # 0
    "Спасибо за вашу помощь!",  # 0
    "Привет!",  # 0
    "Где находится ближайший магазин?",  # 0
    "Когда будет концерт?",  # 0
    "До свидания!"  # 0
]

# Метки (1 - сообщение связано с заявкой, 0 - не связано)
labels = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

# Если уже есть обученная модель, загружаем её
if os.path.exists('message_classifier_model.pkl') and os.path.exists('vectorizer.pkl'):
    model = joblib.load('message_classifier_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    print("Модель загружена из файлов.")

    # Преобразуем сообщения в числовой вид с помощью загруженного векторизатора
    X_new = vectorizer.transform(messages)
    
    # Дообучаем модель на новых данных
    model.fit(X_new, labels)
else:
    # Преобразование текста в векторное представление
    vectorizer = TfidfVectorizer()

    # Преобразуем сообщения в числовой вид
    X = vectorizer.fit_transform(messages)
    y = labels

    # Разделение данных на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Обучение модели логистической регрессии
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Прогнозирование на тестовых данных
    y_pred = model.predict(X_test)

    # Оценка точности
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Точность модели: {accuracy * 100:.2f}%")

# Сохранение дообученной модели и векторизатора
joblib.dump(model, 'message_classifier_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Модель и векторизатор сохранены.")
