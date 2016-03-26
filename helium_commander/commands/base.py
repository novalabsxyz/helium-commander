import abc
import re

class abstractclassmethod(classmethod):
    __isabstractmethod__ = True
    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class BaseCommand:
    __metaclass__ = abc.ABCMeta

    @classmethod
    def command_name(cls):
        return re.sub('(.)([A-Z][a-z]+)', r'\1', cls.__name__).lower()

    @abstractclassmethod
    def add_sub_commands(cls, parser):
        return
