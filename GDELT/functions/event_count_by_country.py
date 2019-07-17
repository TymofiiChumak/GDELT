from plotly.offline import plot
import plotly_express as px
import pandas as pd
import numpy as np
from itertools import product
from ..utils.utils import QueryExecutor, Utils
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import GenericCategoryParameter, FipsCountryParameter
from .function import Function


class EventCountByCountry(Function):
    def __init__(self):
        self.query = """
            SELECT MonthYear AS MonthYear, Actor{4}Geo_CountryCode AS Country, COUNT(*) AS EventCount
            FROM `gdelt-bq.full.events`
            WHERE MonthYear >= {0}
            AND MonthYear < {1}
            AND Actor{3}Geo_CountryCode = "{2}"
            AND Actor{4}Geo_CountryCode IS NOT NULL
            GROUP BY MonthYear, Actor{4}Geo_CountryCode
            ORDER BY MonthYear, Actor{4}Geo_CountryCode
            """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(
            parameters['range'].value[0],
            parameters['range'].value[1],
            parameters['country_id'].value,
            parameters['actor_type'].value,
            3 - parameters['actor_type'].value
        )
        df = qe.get_result_dataframe(query)
        df['country_iso'] = df['Country'].map(Utils().get_fips_iso_mapping())
        df.dropna(inplace=True)
        df['Log of event count'] = np.log10(df['EventCount'])
        df['Date'] = df['MonthYear'].apply(
            lambda date: str(int(date / 100)) + "-" + str(int(date % 100)))
        columns = ['country_iso', 'Date']
        filler = pd.DataFrame(list(product(df['country_iso'].unique(), df['Date'].unique())),
                              columns=columns)

        filled = df.join(filler.groupby(columns).count(), on=columns, how='right')[columns + ['Log of event count']]
        filled['Log of event count'].fillna(0.0, inplace=True)

        fig = px.choropleth(
            filled,
            locations='country_iso',
            locationmode='ISO-3',
            color='Log of event count',
            animation_frame='Date',
            color_continuous_scale=px.colors.sequential.Aggrnyl,
            title="Count of events for each months between {} as Actor {} and other countries".format(
                Utils().get_fips_country_id_to_name_mapping()[parameters['country_id'].value],
                parameters['actor_type'].value
            )
        )
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        actor_to_id_mapping = pd.Series(['Actor 1', 'Actor 2'], index=[1, 2])
        ActorTypeParameter = type("ActorTypeParameter",
                                  (GenericCategoryParameter,),
                                  {"id_to_name_mapping": actor_to_id_mapping})
        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (FipsCountryParameter, ('country_id', 'Country')),
            (ActorTypeParameter, ('actor_type', 'Country role')),
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201906"),
            'country_id': 'US',
            'actor_type': 1,
        }

    @staticmethod
    def get_name():
        return """Event Count By Country"""

    @staticmethod
    def get_description():
        return """Number of events in database for each year for each country"""

    @staticmethod
    def check_params(params):
        return True


