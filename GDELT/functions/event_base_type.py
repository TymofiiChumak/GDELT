from plotly.offline import plot
import plotly.graph_objs as go
from ..utils.utils import QueryExecutor
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import CameoCountryParameter, ActorTypeParameter
from .function import Function
from ..utils.utils import Utils

import pandas as pd


class EventBaseType(Function):
    def __init__(self):
        self.query = """
        SELECT MonthYear AS Date, EventRootCode AS EventCode, COUNT(*) AS EventCount
        FROM `gdelt-bq.full.events`
        WHERE MonthYear >= {start}
        AND MonthYear < {end}
        AND Actor{role}CountryCode = "{country}"
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
        df['EventCount'] = df['EventCount'].astype('int32')
        df['Date'] = df['Date'].astype('int32')
        event_count_sum = df.groupby("Date")['EventCount'].sum()
        sum_mask = df['Date'].map(event_count_sum)
        df['Part'] = df['EventCount'].divide(sum_mask)

        fig = go.Figure()
        df['Date'] = df['Date'].apply(
            lambda date: str(int(date / 100)) + "-" + str(int(date % 100)))
        dates = list(sorted(df['Date'].unique()))
        for event_type in df['EventCode'].unique():
            values = df[df['EventCode'] == event_type]['Part']

            fig.add_trace(go.Scatter(
                x=dates,
                y=values * 100,
                hoverinfo='x+y',
                mode='lines',
                line=dict(width=1.),
                stackgroup='one',
                name=Utils().get_cameo_base_eventcodes_id_to_name_mapping().loc[event_type]
            ))

        fig.layout.update(
            showlegend=True,
            yaxis=dict(
                type='linear',
                range=[1, 100],
                ticksuffix='%'))
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


