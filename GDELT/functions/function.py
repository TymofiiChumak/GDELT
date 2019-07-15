
class Function:
    """
    default class to be inherited by new implementation
    needs to be added to "function_list" attribute
    in init method at function util class
    TODO add auto search of classes which implements this class
    """

    def get_plot(self, parameters):
        """
        :param parameters:
        dictionary where keys are parameter names,
        values are values for parameter
        :return:
        html code for plot
        """
        raise Exception("Method isn't defined")

    @staticmethod
    def get_parameters():
        """
        :return:
        list of tuples:
        (class of parameter type, (parameter name, parameter name to display)
        """
        return []

    @staticmethod
    def get_default_parameters():
        """
        :return:
        dictionary where keys are parameter name,
        values are default value for parameter
        """
        return {}

    @staticmethod
    def get_name():
        """
        :return:
        string name of method
        """
        return "Generic method name"

    @staticmethod
    def get_description():
        """
        :return:
        string description of method to display
        """
        return """Description of function"""

    @staticmethod
    def check_params(params):
        """
        checks parameters specified in get_params function
        returns true if all ok
        if something wrong raise AssertionError with two args:
        1) Error description
        2) Parameter name
        :arg:
        list of tuples (parameter name, parameter value
        :return:
        True if all parameters are ok
        """
        return True



