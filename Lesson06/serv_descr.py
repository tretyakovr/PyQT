class ServerDescr():
    def __init__(self, name, type_name, default=None):
        self.name = '_' + name
        self.type = type_name
        self.default = default if default else type_name()

    def __get__(self, instance, owner):
        return getattr(instance, self.name, self.default)

    def __set__(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError(f'Значение должно быть типа {self.type}')

        if self.name == '_port' and not value >= 0:
            raise ValueError('Номер порта должен быть неотрицательным числом!')

        setattr(instance, self.name, value)

    def __delete__(self, instance):
        raise AttributeError('Невозможно удалить атрибут')
