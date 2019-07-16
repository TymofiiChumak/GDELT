from ..utils.utils import Singleton


class Parameter:
    def __init__(self, value):
        self.value = value

    @staticmethod
    def get_field_code(params, default_value):
        return ""

    @staticmethod
    def get_value_from_default(value):
        return value

    @staticmethod
    def check_params(params):
        return True


class ParameterUtil(metaclass=Singleton):
    @staticmethod
    def get_datalist(elements, name):
        datalist = """<datalist id="{}">""".format(name)
        for element in elements:
            datalist += "<option>" + str(element) + "</option>"
        datalist += "</datalist>"
        return datalist


