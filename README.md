# content-control
 Web Application for system controls of content

# Платформа управления социальными публикациями

## 📋 Описание проекта
Веб-приложение для создания, публикации и модерации контента с системой авторизации и безопасности.

## 🚀 Требования к окружению
- Python 3.10+
- pip
- virtualenv (опционально, но рекомендуется)

## 🔐 Безопасность
- Используется хеширование паролей
- Встроенная система модерации контента
- Защита от csrf-атак
- Проверка прав доступа

## 🐛 Возможные проблемы и решения
- Проблемы с зависимостями: `pip install --upgrade pip`
- Ошибки базы данных: `flask db migrate` и `flask db upgrade`

## 🆘 Поддержка
При возникновении проблем создайте Issue в репозитории или свяжитесь с разработчиком.

## 🔧 Установка и настройка

### 1. Клонирование репозитория
```bash
git clone https://github.com/Demi-Play/content-control.git
cd content-control
```

### 2. Создание виртуального окружения
Для Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Установка дополнительных зависимостей

Языковая модель spaCy

```bash
python -m spacy download ru_core_news_sm
python -m spacy download ru_core_news_md
```

Установка моделей

```bash
pip install textblob
```

### 5. Запуск приложения
Перейдите в каталог с файлом run.py и запустите его через терминал следующим образом: 
```bash
python run.py
```

