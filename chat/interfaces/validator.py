class _MetaCollectValidatorMethod(type):
    def __new__(cls, cname, bases, attrs):
        """Упаковывает в атрибут класса validators методы валидации"""
        _cls = type.__new__(cls, cname, bases, attrs)
        _cls.validators = [getattr(_cls, method) for method in _cls.__dict__ if method.startswith("is_")]
        return _cls


class BaseValidatorField(metaclass=_MetaCollectValidatorMethod):
    validators = None

    @classmethod
    def validate(cls, value):
        for validator in cls.validators:
            validator(value)
