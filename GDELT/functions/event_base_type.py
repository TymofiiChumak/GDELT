from plotly.offline import plot
import plotly_express as px
from ..utils.utils import QueryExecutor
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import CameoCountryParameter, ActorTypeParameter
from .function import Function


class EventCount(Function):
    def __init__(self):
        self.query = """
        SELECT MonthYear AS Date, EventRootCode AS EventCode, COUNT(*) AS EventCount
        FROM `gdelt-bq.full.events`
        WHERE MonthYear >= {start}
        AND MonthYear < {end}
        AND Actor{role}CountryCode = {country}
        GROUP BY MonthYear, EventRootCode
        ORDER BY MonthYear, EventRootCode
        """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(
            start=parameters['range'].value[0],
            end=parameters['range'].value[1],
            country=parameters['country'].value,
            role=parameters['actor_type'].value,
        )
        df = qe.get_result_dataframe(query)

        fig = px.line(df, x='Date', y='EventCount')
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (CameoCountryParameter, ('country', 'Country')),
            (ActorTypeParameter, ('actor_type', 'Country role')),
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201901"),
            'country': "POL",
            'actor_type': 1,
        }

    @staticmethod
    def get_name():
        return """Event types percentage"""

    @staticmethod
    def get_description():
        return """Number of events in database for each month for range of time"""

    @staticmethod
    def check_params(params):
        return True


