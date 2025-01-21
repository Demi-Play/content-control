import re
import spacy
from textblob import TextBlob

class ContentModerator:
    def __init__(self):
        # Загрузка языковой модели
        self.nlp = spacy.load("ru_core_news_sm")
    
    def contains_profanity(self, text):
        """Расширенная проверка на наличие нецензурной лексики"""
        profanity_words = [
            # Основные матерные слова
            'хуй', 'хуе', 'хуё', 'пизд', 'ебан', 'ебл', 'ебу', 
            'бля', 'блят', 'сука', 'сучк', 'говн', 'гавн', 
            'мудак', 'мудил', 'петух', 'петух', 'шлюх', 
            
            # Производные и цензурные варианты
            'х*й', 'п*зд', 'е*ать', 'е*аный', 
            
            # Эвфемизмы и завуалированные формы
            'нафиг', 'нахрен', 'нахер', 'блин', 'бляха',
            
            # Оскорбительные слова
            'дебил', 'даун', 'идиот', 'тупой', 'придурок'
        ]
        
        # Преобразуем текст в нижний регистр
        text_lower = text.lower()
        
        # Проверяем каждое слово из списка
        for word in profanity_words:
            # Используем точное совпадение и частичное вхождение
            if word in text_lower:
                return True
        
        return False
    
    def contains_profanities(self, text):
        """Проверка с использованием регулярных выражений"""
        profanity_patterns = [
            # Точные совпадения
            r'\b(хуй|хуе|хуё|пизд|ебан|ебл|ебу)\w*\b',
            
            # Цензурные варианты
            r'\b(х\*й|п\*зд|е\*ать)\w*\b',
            
            # Эвфемизмы
            r'\b(нафиг|нахрен|нахер)\b',
            
            # Оскорбительные слова
            r'\b(дебил|даун|идиот|тупой|придурок)\b'
        ]
        
        # Преобразуем текст в нижний регистр
        text_lower = text.lower()
        
        # Проверяем каждый паттерн
        for pattern in profanity_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def analyze_sentiment(self, text):
        """Анализ тональности текста"""
        # Используем TextBlob для оценки тональности
        analysis = TextBlob(text)
        sentiment_score = analysis.sentiment.polarity
        
        if sentiment_score < -0.5:
            return 'negative'
        elif sentiment_score > 0.5:
            return 'positive'
        else:
            return 'neutral'
    
    def detect_dangerous_content(self, text):
        """Обнаружение потенциально опасного контента"""
        dangerous_patterns = [
            r'\b(убить|смерть|насилие|терроризм|убью|мертв|взрыв)\b',
            r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text.lower()):
                return True
        return False
    
    def moderate_comment(self, text):
        """
        Полная модерация комментария
        Возвращает True, если контент потенциально опасен
        """
        checks = [
            self.contains_profanity(text),
            self.contains_profanities(text),
            self.analyze_sentiment(text) == 'negative',
            self.detect_dangerous_content(text)
        ]
        
        return any(checks)
