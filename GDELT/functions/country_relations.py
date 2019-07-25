from plotly.offline import plot
import plotly_express as px
import pandas as pd
import numpy as np
from itertools import product
from ..utils.utils import QueryExecutor, Utils
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import FipsCountryParameter, ActorTypeParameter, TargetTypeParameter
from .function import Function


class CountryRelations(Function):
    def __init__(self):
        self.query = """
            SELECT MonthYear AS MonthYear, Actor{role_2}Geo_CountryCode AS Country, {target_type}AS Target
            FROM `gdelt-bq.full.events`
            WHERE MonthYear >= {start}
            AND MonthYear < {end}
            AND Actor{role_1}Geo_CountryCode = "{country}"
            AND Actor{role_2}Geo_CountryCode IS NOT NULL
            GROUP BY MonthYear, Actor{role_2}Geo_CountryCode
            ORDER BY MonthYear, Actor{role_2}Geo_CountryCode
            """

    def get_plot(self, parameters):
        target_dict = {
            1: "COUNT(*)",
            2: "AVG(AvgTone)",
            3: "Sum(NumMentions)",
            4: "AVG(GoldsteinScale)"
        }
        qe = QueryExecutor()
        query = self.query.format(
            start=parameters['range'].value[0],
            end=parameters['range'].value[1],
            country=parameters['country_id'].value,
            role_1=parameters['actor_type'].value,
            role_2=(3 - parameters['actor_type'].value),
            target_type=target_dict[parameters['target_type'].value],
        )
        df = qe.get_result_dataframe(query)
        df['country_iso'] = df['Country'].map(Utils().get_fips_iso_mapping())
        df.dropna(inplace=True)

        target_name_dict = {
            1: 'Event Count',
            2: 'Average Tone',
            3: 'Sum of Mentions',
            4: 'Average Goldstein scale'
        }
        target_col_name = target_name_dict[parameters['target_type'].value]
        if parameters['target_type'].value in [1, 3]:
            target_col_name = "Log " + target_col_name
            df[target_col_name] = np.log10(df['Target'])
        else:
            df[target_col_name] = df['Target']

        df['Date'] = df['MonthYear'].apply(
            lambda date: str(int(date / 100)) + "-" + str(int(date % 100)))
        columns = ['country_iso', 'Date']
        filler = pd.DataFrame(list(product(df['country_iso'].unique(), df['Date'].unique())),
                              columns=columns)

        filled = df.join(filler.groupby(columns).count(), on=columns, how='right')[columns + [target_col_name]]
        filled[target_col_name].fillna(0.0, inplace=True)

        color_bounds = filled[target_col_name].min(), filled[target_col_name].max()

        fig = px.choropleth(
            filled,
            locations='country_iso',
            locationmode='ISO-3',
            color=target_col_name,
            animation_frame='Date',
            range_color=color_bounds,
            color_continuous_scale=px.colors.sequential.Aggrnyl,
            title="{} for each months between {} as Actor {} and other countries".format(
                target_name_dict[parameters['target_type'].value],
                Utils().get_fips_country_id_to_name_mapping()[parameters['country_id'].value],
                parameters['actor_type'].value
            )
        )
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (FipsCountryParameter, ('country_id', 'Country')),
            (ActorTypeParameter, ('actor_type', 'Country role')),
            (TargetTypeParameter, ('target_type', 'Measure type'))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201906"),
            'country_id': 'US',
            'actor_type': 1,
            'target_type': 1
        }

    @staticmethod
    def get_name():
        return """Country relations"""

    @staticmethod
    def get_description():
        return "Characteristic of events (Event count, Average tone, Sum mentions, Average Goldstain scale value) \
        between one country and others for each month"

    @staticmethod
    def check_params(params):
        return True


