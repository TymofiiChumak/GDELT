import plotly.plotly
import plotly_express as px
from ..utils.utils import QueryExecutor
from ..parametrs.date_parameter import DateTimeParameter
from .function import Function
import time


class EventCount(Function):
    def __init__(self):
        self.query = """
        SELECT MonthYear AS Date, COUNT(*) AS EventCount
        FROM `gdelt-bq.full.events`
        WHERE SQLDATE >= {}
        AND SQLDATE < {}
        GROUP BY MonthYear
        ORDER BY MonthYear
        """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(parameters['start'].value, parameters['end'].value)
        df = qe.get_result_dataframe(query, month_year_cols=['Date'])
        fig = px.line(df, x='Date', y='EventCount')
        return plotly.offline.plot(fig, include_plotlyjs=True, output_type='div')
        # time.sleep(200)
        # return "<h1>Loaded</h1>"

    @staticmethod
    def get_parameters():
        return [
            (DateTimeParameter, ('start', 'Start Time')),
            (DateTimeParameter, ('end', 'End Time'))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'start': "20130101",
            'end': "20190101",
        }

    @staticmethod
    def get_name():
        return """Event Count"""

    @staticmethod
    def get_description():
        return """Description of function"""

    @staticmethod
    def check_params(params):
        return True


