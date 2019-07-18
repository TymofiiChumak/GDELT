from ..utils.utils import QueryExecutor
from mapboxgl.utils import *
from mapboxgl.viz import HeatmapViz
from numpy import unique
import re
from ..parametrs.date_parameters import DateRangeParameter
from ..parametrs.category_parameters import FipsCountryParameter, QuadClassParameter, CameoEventcodeBaseParameter
from .function import Function
from ..utils.utils import Utils

import pandas as pd


class EventDensityByCountry(Function):
    def _build_qeury(self, params):
        query = """SELECT ActionGeo_Lat AS lat, ActionGeo_Long AS lon, COUNT(*) AS EventCount
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
        GROUP BY lat, lon
        ORDER BY lat, lon"""
        return query

    def get_plot(self, parameters):
        qe = QueryExecutor()
        df = qe.get_result_dataframe(self._build_qeury(parameters))

        min_lon, max_lon = df.lon.quantile([0.01, 0.99])
        min_lat, max_lat = df.lat.quantile([0.01, 0.99])
        center = ((min_lon + max_lon) / 2, (min_lat + max_lat) / 2)
        df = df[(df.lon >= min_lon) & (df.lon <= max_lon) & (df.lat >= min_lat) & (df.lat <= max_lat)]

        geojson = df_to_geojson(df,
                                properties=['EventCount'],
                                lat='lat',
                                lon='lon',
                                precision=3)

        heatmap_color_stops = create_color_stops([0.01, 0.25, 0.5, 0.75, 1], colors='RdPu')
        heatmap_radius_stops = [[0, 1], [14, 70]]

        color_breaks = unique([round(df['EventCount'].quantile(q=x * 0.1), 2) for x in range(2, 10)])
        color_stops = create_color_stops(color_breaks, colors='Spectral')

        heatmap_weight_stops = create_weight_stops(color_breaks)

        viz = HeatmapViz(geojson,
                         access_token=Utils().get_mapbox_token(),
                         weight_property='EventCount',
                         weight_stops=heatmap_weight_stops,
                         color_stops=heatmap_color_stops,
                         radius_stops=heatmap_radius_stops,
                         opacity=0.8,
                         center=center,
                         zoom=6,
                         below_layer='waterway-label')

        viz.height = "500px"

        return viz.as_iframe(viz.create_html())

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
        return """Event density by country"""

    @staticmethod
    def get_description():
        return """Event density by country"""

    @staticmethod
    def check_params(params):
        return True


