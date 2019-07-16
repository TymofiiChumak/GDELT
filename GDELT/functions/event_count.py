import plotly.plotly
import plotly_express as px
from ..utils.utils import QueryExecutor
from ..parametrs.date_parameters import DateRangeParameter
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
        start, end = parameters['range'].value
        query = self.query.format(start, end)
        df = qe.get_result_dataframe(query, month_year_cols=['Date'])
        fig = px.line(df, x='Date', y='EventCount')
        return plotly.offline.plot(fig, include_plotlyjs=True, output_type='div')
        # time.sleep(5)
        # return "<h1>Loaded</h1>"

    @staticmethod
    def get_parameters():
        return [
            (DateRangeParameter, ('range', 'Time range')),
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("20130101", "20190101"),
        }

    @staticmethod
    def get_name():
        return """Event Count"""

    @staticmethod
    def get_description():
        return """Number of events in database for each month for range of time"""

    @staticmethod
    def check_params(params):
        return True


