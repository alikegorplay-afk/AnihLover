class ParseError(Exception):
    """Базовое исключение для ошибок парсера"""
    
class RequiredAttributeNotFound(ParseError):
    """Исключение, когда атрибут не найден"""
