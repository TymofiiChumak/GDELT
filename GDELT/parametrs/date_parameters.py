from .parameter import Parameter
from calendar import monthrange


class DateTimeParameter(Parameter):
    """
    Class for date parameter
    Date must be in MM/DD/YYYY
    Returns date in format YYYYMMYY (the same as SQLDATE column)
    """
    def __init__(self, date_string):
        # String must be in format MM/DD/YYYY
        month = date_string[:2]
        year = date_string[6:]
        day = date_string[3:5]
        sqldate = year + month + day
        Parameter.__init__(self, sqldate)

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en' 
               data-date-format="mm/dd/yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

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


class DateRangeParameter(DateTimeParameter):
    """
    Class for date range parameter
    Date must be in MM/DD/YYYY;MM/DD/YYYY
    Returns tuple of dates in format ("YYYYMMYY", "YYYYMMYY") (the same as SQLDATE column)
    """
    def __init__(self, value):
        # String must be in format MM/DD/YYYY
        sql_format = lambda date: date[6:] + date[:2] + date[3:5]
        data1, data2 = value.split(';')
        Parameter.__init__(self, (sql_format(data1), sql_format(data2)))

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en' 
               data-range="true"
               data-multiple-dates-separator=";"
               data-date-format="mm/dd/yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        date1, date2 = value
        format_date = lambda date: date[6:] + '/' + date[4:6] + '/' + date[:4]
        return format_date(date1) + ';' + format_date(date2)

    @staticmethod
    def check_params(value):
        def check_date_string(date_string):
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
        assert len(value) == 21, "Wrong date length"
        assert value[10] == ';' and value.count(';') == 1, 'Wrong date format'
        data1, data2 = value.split(';')
        return check_date_string(data1) and check_date_string(data2)


class MonthParameter(Parameter):
    """
    Class for month parameter
    Date must be in MM/YYYY
    Returns date in format YYYYMM (the same as MonthYear column)
    """
    def __init__(self, date_string):
        # String must be in format MM/YYYY
        month = date_string[:2]
        year = date_string[3:]
        month_year = year + month
        Parameter.__init__(self, month_year)

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en'
               data-min-view="months" 
               data-view="months"
               data-date-format="mm/yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        year = value[:4]
        month = value[4:]
        return month + '/' + year

    @staticmethod
    def check_params(date_string):
        assert len(date_string) == 7, "Wrong date length"
        assert date_string[2] == '/', 'Wrong date format'
        try:
            month = int(date_string[:2])
            assert 1 <= month <= 12, 'Wrong month'
            year = int(date_string[3:])
            assert 1979 <= year <= 2019, 'Wrong year'
        except ValueError as e:
            raise AssertionError("Wrong number format")
        return True


class MonthRangeParameter(Parameter):
    """
    Class for month range parameter
    Date must be in MM/YYYY;MM/YYYY
    Returns tuple of months in format ("YYYYMM", "YYYYMM") (the same as MonthYear column)
    """
    def __init__(self, value):
        # String must be in format MM/YYYY
        date1, date2 = value.split(';')
        Parameter.__init__(self, (date1[3:] + date1[:2], date2[3:] + date2[:2]))

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en'
               data-min-view="months" 
               data-range="true"
               data-multiple-dates-separator=";"
               data-view="months"
               data-date-format="mm/yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        year1 = value[0][:4]
        month1 = value[0][4:]
        year2 = value[1][:4]
        month2 = value[1][4:]
        return month1 + '/' + year1 + ';' + month2 + '/' + year2

    @staticmethod
    def check_params(value):
        def check_month(date_string):
            assert len(date_string) == 7, "Wrong date length"
            assert date_string[2] == '/', 'Wrong date format'
            try:
                month = int(date_string[:2])
                assert 1 <= month <= 12, 'Wrong month'
                year = int(date_string[3:])
                assert 1979 <= year <= 2019, 'Wrong year'
            except ValueError as e:
                raise AssertionError("Wrong number format")
        assert len(value) == 15, "Wrong date length"
        assert value[7] == ';' and value.count(';') == 1, 'Wrong date format'
        data1, data2 = value.split(';')
        return check_month(data1) and check_month(data2)


class YearParameter(Parameter):
    """
    Class for year parameter
    Date must be in YYYY
    Returns date in format YYYY (the same as Year column)
    """
    def __init__(self, year):
        # String must be in format YYYY
        Parameter.__init__(self, year)

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en'
               data-min-view="years" 
               data-view="years"
               data-date-format="yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        return value

    @staticmethod
    def check_params(date_string):
        assert len(date_string) == 4, "Wrong date length"
        try:
            year = int(date_string)
            assert 1979 <= year <= 2019, 'Wrong year'
        except ValueError as e:
            raise AssertionError("Wrong number format")
        return True


class YearRangeParameter(Parameter):
    """
    Class for year range parameter
    Date must be in YYYY;YYYY
    Returns tuple of months in format ("YYYYMM", "YYYYMM") (the same as MonthYear column)
    """
    def __init__(self, value):
        # String must be in format MM/YYYY
        date1, date2 = value.split(';')
        Parameter.__init__(self, (date1, date2))

    @staticmethod
    def get_field_code(params, default_value):
        param_id, label = params
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
        <input type="text" 
               class="form-control param datepicker-here" 
               data-language='en'
               data-min-view="years" 
               data-range="true"
               data-multiple-dates-separator=";"
               data-view="years"
               data-date-format="yyyy"
               id="{0}" 
               value={2}>
        </div>""".format(param_id, label, default_value)
        return test_form_field

    @staticmethod
    def get_value_from_default(value):
        year1 = value[0]
        year2 = value[1]
        return year1 + ';' + year2

    @staticmethod
    def check_params(value):
        def check_month(date_string):
            assert len(date_string) == 4, "Wrong date length"
            try:
                year = int(date_string)
                assert 1979 <= year <= 2019, 'Wrong year'
            except ValueError as e:
                raise AssertionError("Wrong number format")
        assert len(value) == 9, "Wrong date length"
        assert value[4] == ';' and value.count(';') == 1, 'Wrong date format'
        data1, data2 = value.split(';')
        return check_month(data1) and check_month(data2)
