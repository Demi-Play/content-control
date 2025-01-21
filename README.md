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
git clone https://github.com/your_username/content-management-platform.git
cd content-management-platform
```

### 2. Создание виртуального окружения
```bash
Для Windows
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
```

Установка моделей

```bash
pip install textblob
```
