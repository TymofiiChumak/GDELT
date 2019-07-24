from .parameter import Parameter


class TextParameter(Parameter):
    """
    Base parameter class for text/string value
    """
    def __init__(self, value):
        Parameter.__init__(self, value)

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
            <input type="text" class="form-control param" id="{0}" value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        return value

    @staticmethod
    def check_params(params):
        return True
