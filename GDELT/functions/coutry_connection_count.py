import plotly.plotly
import plotly.graph_objs as go
import numpy as np
from ..utils.utils import QueryExecutor
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import FipsCountryParameter
from .function import Function
from ..utils.utils import Utils


class CountryConnectionCount(Function):
    def __init__(self):
        self.query = """
        SELECT t1.ActorCountry AS ActorCountry, t1.CountryCount AS CountryCountAsActor1, t2.CountryCount AS CountryCountAsActor2
        FROM
          (SELECT Actor2Geo_CountryCode AS ActorCountry, count(*) AS CountryCount
          FROM `gdelt-bq.full.events`
          WHERE MonthYear >= {0}
          AND MonthYear < {1}
          AND Actor1Geo_CountryCode="{2}"
          GROUP BY Actor2Geo_CountryCode) AS t1
        JOIN
          (SELECT Actor1Geo_CountryCode AS ActorCountry, count(*) AS CountryCount
          FROM `gdelt-bq.full.events`
          WHERE MonthYear >= {0} 
          AND MonthYear < {1}
          AND Actor2Geo_CountryCode="{2}"
          GROUP BY Actor1Geo_CountryCode) as t2
        ON t1.ActorCountry = t2.ActorCountry"""

    def get_plot(self, parameters):
        qe = QueryExecutor()
        start, end = parameters['range'].value
        country_code = parameters['country_code'].value
        query = self.query.format(start, end, country_code)
        df = qe.get_result_dataframe(query)
        df.index = df['ActorCountry'].map(Utils().get_fips_country_id_to_name_mapping())

        def get_data_for_plot(data, count_col):
            threshold = data[count_col].sum() * 0.015
            cat_df = data.copy()
            cat_df.loc['OTHER'] = cat_df.loc[cat_df[count_col] < threshold].sum()
            cat_df = cat_df.loc[cat_df[count_col] >= threshold]
            cat_df.drop('ActorCountry', axis=1, inplace=True)
            cat_df.rename({np.NaN: 'NONE'}, axis=0, inplace=True)
            return cat_df

        data_a1 = get_data_for_plot(df, 'CountryCountAsActor1')
        data_a2 = get_data_for_plot(df, 'CountryCountAsActor2')

        trace1 = go.Pie(labels=data_a1.index,
                        values=data_a1['CountryCountAsActor1'],
                        domain=dict(x=[0, 0.5]))
        trace2 = go.Pie(labels=data_a2.index,
                        values=data_a2['CountryCountAsActor2'],
                        domain=dict(x=[0.5, 1]))
        ann1 = dict(font=dict(size=20),
                    showarrow=False,
                    text='Actor1',
                    x=0.23,
                    y=1.15)
        ann2 = dict(font=dict(size=20),
                    showarrow=False,
                    text='Actor2',
                    x=0.78,
                    y=1.15)

        data = [trace1, trace2]
        layout = go.Layout(title='Count of events between {} and other countries'.format(
            Utils().get_fips_country_id_to_name_mapping()[country_code]),
            annotations=[ann1, ann2])

        fig = go.Figure(data=data,
                        layout=layout)

        return plotly.offline.plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (FipsCountryParameter, ('country_code', 'Country'))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201906"),
            'country_code': 'US',
        }

    @staticmethod
    def get_name():
        return """Country connection Count"""

    @staticmethod
    def get_description():
        return """Description"""

    @staticmethod
    def check_params(params):
        return True


