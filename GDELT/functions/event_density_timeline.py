from ..utils.utils import QueryExecutor
import folium
import folium.plugins as plugins
from numpy import log
from ..parametrs.date_parameters import DateRangeParameter
from ..parametrs.category_parameters import FipsCountryParameter, QuadClassParameter, CameoEventcodeBaseParameter
from .function import Function
from ..utils.utils import Utils

import pandas as pd


class EventDensityTimeline(Function):
    def _build_qeury(self, params):
        query = """SELECT MonthYear, ActionGeo_Lat AS lat, ActionGeo_Long AS lon, COUNT(*) AS EventCount
        FROM `gdelt-bq.full.events`
        WHERE SQLDATE >= {0}
        AND SQLDATE < {1}
        AND ActionGeo_CountryCode = "{2}" """.format(
            params['range'].value[0],
            params['range'].value[1],
            params['loc_country'].value)
        multiple_params = ['a1_country', 'a2_country', 'quad_class', 'event_code']
        column_names = ['Actor1Geo_CountryCode', 'Actor2Geo_CountryCode', 'QuadClass', 'EventRootCode']
        for param_name, column_name in zip(multiple_params, column_names):
            if 'All' in params[param_name].value:
                continue
            query += "\nAND {} IN UNNEST({})".format(
                column_name, params[param_name].value
            )
        query += """
        GROUP BY MonthYear, lat, lon
        ORDER BY MonthYear, lat, lon"""
        return query

    def get_plot(self, parameters):
        qe = QueryExecutor()
        df = qe.get_result_dataframe(self._build_qeury(parameters))

        min_lon, max_lon = df.lon.quantile([0.01, 0.99])
        delta_lon = max_lon - min_lon
        min_lat, max_lat = df.lat.quantile([0.01, 0.99])
        delta_lat = max_lat - min_lat
        center = ((min_lat + max_lat) / 2, (min_lon + max_lon) / 2)
        df = df[(df.lon >= min_lon) & (df.lon <= max_lon) & (df.lat >= min_lat) & (df.lat <= max_lat)]

        df['EventCount'] = log(df['EventCount'])
        df['EventCount'] = df['EventCount'] / df['EventCount'].max()
        timeline = []
        months = list(sorted(df['MonthYear'].unique()))
        for month in months:
            month_counts = df[df['MonthYear'] == month][['lat', 'lon', 'EventCount']].values
            timeline.append(list(map(list, month_counts)))

        m = folium.Map(center,
                       tiles='stamentoner',
                       control_scale=True,
                       height="75%"
                       )

        m.fit_bounds([
            [min_lat - 0.1 * delta_lat, max_lat + 0.1 * delta_lat],
            [min_lon - 0.1 * delta_lon, max_lon + 0.1 * delta_lon],
        ])
        months = Utils().format_months_names(months)
        hm = plugins.HeatMapWithTime(
            data=timeline,
            index=months,
            name="heatmap",
            radius=0.3,
            scale_radius=True,
            overlay=True,
        )
        hm.add_to(m)
        m.render()
        return m._repr_html_().replace('"', "'")

    @staticmethod
    def get_parameters():
        return [
            (DateRangeParameter, ('range', 'Time range')),
            (FipsCountryParameter, ('loc_country', 'Country of events location')),
            (FipsCountryParameter.allow_all().allow_multiple(),
             ('a1_country', 'Actor 1')),
            (FipsCountryParameter.allow_all().allow_multiple(),
             ('a2_country', 'Actor 2')),
            (QuadClassParameter.allow_all().allow_multiple(),
             ('quad_class', "Quad class")),
            (CameoEventcodeBaseParameter.allow_all().allow_multiple(),
             ('event_code', "Event Base code"))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("20130101", "20190101"),
            'loc_country': 'PL',
            'a1_country': ['US'],
            'a2_country': ['US'],
            'quad_class': ['All'],
            'event_code': ['All'],
        }

    @staticmethod
    def get_name():
        return """Event density timeline"""

    @staticmethod
    def get_description():
        return """Event density heatmap by country for each month"""

    @staticmethod
    def check_params(params):
        return True


