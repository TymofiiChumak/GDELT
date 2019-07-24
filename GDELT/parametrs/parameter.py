class Parameter:
    """
    Base class for function parameters
    After creating value of parameter can be accessed by
    "value" object attribute
    """
    def __init__(self, value):
        """
        :param value: value of parameter
        """
        self.value = value

    @staticmethod
    def get_field_code(params, default_value):
        """
        :param params: Tuple of param_id and label
        :param default_value: Default value of parameter
        :return: html code for parameter field
        preferred form:
        <div class="form-group">
            <label for="{param_id}"> {Label} </label>
            <input id="{param_id}" value={default_value}>
        </div>
        """
        return ""

    @staticmethod
    def get_value_from_default(value):
        """
        :param value: value in format witch be used in function
        :return: value in format to display in field
        i.e. "20190101" -> "01/01/2019"
        """
        return value

    @staticmethod
    def check_params(value):
        """
        :param value: value of parameter
        :return: True if parameter meets condition
        :raise AssertionError with error description
        """
        return True



