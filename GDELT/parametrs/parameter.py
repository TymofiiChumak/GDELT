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


class DateTimeParameter(Parameter):
    def __init__(self, date_string):
        # String must be in format MM/DD/YYYY
        month = date_string[:2]
        year = date_string[6:]
        day = date_string[3:5]
        sqldate = year + month + day
        Parameter.__init__(self, sqldate)

    @staticmethod
    def get_value_from_default(value):
        year = value[:4]
        month = value[4:6]
        day = value[6:]
        return month + '/' + day + '/' + year

    @staticmethod
    def check_params(date_string):
        assert len(date_string) == 10, "Wrong date length"
        assert date_string[2] == '/' and date_string[5] == '/', 'Wrong date format'
        try:
            month = int(date_string[:2])
            assert 1 <= month <= 12, 'Wrong month'
            year = int(date_string[6:])
            assert 1979 <= year <= 2019, 'Wrong year'
            day = int(date_string[3:5])
            assert 0 <= day <= monthrange(int(year), int(month))[1], 'Wrong day'
        except ValueError as e:
            raise AssertionError("Wrong number format")
        return True


class CameoCountryParameter(Parameter):
    def __init__(self, country_code):
        self.value = country_code



