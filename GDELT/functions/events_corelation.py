from plotly.offline import plot
import plotly_express as px
from ..utils.utils import QueryExecutor, Utils
from ..parametrs.date_parameters import MonthParameter
from .function import Function


class EventCorrelation(Function):
    def __init__(self):
        self.query = """
        WITH 
          comb_unique AS 
          (SELECT u1.Actor1Geo_CountryCode AS Actor1, u2.Actor2Geo_CountryCode AS Actor2, u3.SQLDATE AS Date
            FROM 
                (SELECT DISTINCT Actor1Geo_CountryCode
                 FROM `gdelt-bq.full.events`
                 WHERE MonthYear = {month}
                 AND NOT Actor1Geo_CountryCode IS NULL
                 ORDER BY Actor1Geo_CountryCode) AS u1
            CROSS JOIN
                (SELECT DISTINCT Actor2Geo_CountryCode
                 FROM `gdelt-bq.full.events`
                 WHERE MonthYear = {month}
                 AND NOT Actor2CountryCode IS NULL
                 ORDER BY Actor2Geo_CountryCode) AS u2
            CROSS JOIN
                (SELECT DISTINCT SQLDATE
                 FROM `gdelt-bq.full.events`
                 WHERE MonthYear = {month}
                 ORDER BY SQLDATE) AS u3),
            filled_table AS 
            (SELECT comb_unique.Actor1 AS Actor1, 
                    comb_unique.Actor2 AS Actor2, 
                    comb_unique.Date AS Date,
                    IFNULL(t1.AvgCount, 0.0) AS AvgCount
            FROM comb_unique
            LEFT JOIN
              (SELECT Actor1Geo_CountryCode, Actor2Geo_CountryCode, SQLDATE as Date, count(*) as AvgCount
              FROM `gdelt-bq.full.events`
              WHERE MonthYear = {month}
              AND NOT Actor1Geo_CountryCode IS NULL
              AND NOT Actor2Geo_CountryCode IS NULL
              GROUP BY Actor1Geo_CountryCode, Actor2Geo_CountryCode, SQLDATE
              ORDER BY Actor1Geo_CountryCode, Actor2Geo_CountryCode, SQLDATE) AS t1
            ON comb_unique.Actor1 = t1.Actor1Geo_CountryCode
            AND comb_unique.Actor2 = t1.Actor2Geo_CountryCode
            AND comb_unique.Date = t1.Date)
        SELECT t1.Actor1 AS Actor1, 
               t2.Actor1 AS Actor2,
               CORR(t1.AvgCount, t2.AvgCount) AS AvgCountCorr
        FROM filled_table as t1
        CROSS JOIN filled_table as t2
        WHERE t1.Actor2 = t2.Actor2
        AND t1.Date = t2.Date
        AND t1.Actor1 < t2.Actor1
        GROUP BY t1.Actor1, t2.Actor1
        HAVING NOT IS_NAN(AvgCountCorr)
        ORDER BY AvgCountCorr DESC
        LIMIT 10
        """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(month=parameters['month'].value)
        df = qe.get_result_dataframe(query)
        df = df.iloc[::-1]
        df['Actor1'] = df['Actor1'].map(Utils().get_fips_country_id_to_name_mapping())
        df['Actor2'] = df['Actor2'].map(Utils().get_fips_country_id_to_name_mapping())
        df['Country name'] = df['Actor1'] + ' & ' + df['Actor2']
        df['Correlation coefficient'] = df['AvgCountCorr']
        fig = px.bar(
            data_frame=df,
            x='Correlation coefficient',
            y='Country name',
            text='Country name',
            orientation='h',
            title="Correlation between number of events of each day to each country for {}".format(
                Utils().format_months_names([parameters['month'].value])[0]
            ),
        )
        fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                          marker_line_width=1.5, opacity=0.6)
        fig.update_yaxes(title='', showticklabels=False)
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        return [
            (MonthParameter, ('month', 'Month')),
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'month': "201905",
        }

    @staticmethod
    def get_name():
        return """Event Correlation"""

    @staticmethod
    def get_description():
        return """Correlation between number of events of each day to each country for month"""

    @staticmethod
    def check_params(params):
        return True


