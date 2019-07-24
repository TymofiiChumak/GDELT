from .parameter import Parameter


class IntParameter(Parameter):
    """
    Base parameter class for int value
    """
    def __init__(self, value):
        Parameter.__init__(self, int(value))

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
            <input type="text" class="form-control param int_field" id="{0}" value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        return str(value)

    @staticmethod
    def check_params(params):
        try:
            int(params)
        except ValueError as e:
            raise AssertionError("Wrong number format")
        return True


class FloatParameter(Parameter):
    """
    Base parameter class for float value
    """
    def __init__(self, value):
        Parameter.__init__(self, float(value))

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
            <input type="text" class="form-control param float_field" id="{0}" value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        return str(value)

    @staticmethod
    def check_params(params):
        try:
            float(params)
        except ValueError as e:
            raise AssertionError("Wrong number format")
        return True
