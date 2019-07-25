from plotly.offline import plot
import plotly_express as px
import pandas as pd
import numpy as np
from sklearn.cluster import Birch, AgglomerativeClustering, KMeans

from ..utils.utils import QueryExecutor, Utils
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import ActorTypeParameter, GenericCategoryParameter
from ..parametrs.base_parameters import IntParameter
from .function import Function


class Clustering(Function):
    def __init__(self):
        self.query = """
            SELECT e.Actor1Geo_CountryCode AS Actor1Geo,
                   e.Actor2Geo_CountryCode AS Actor2Geo,
                   SUM((0.5 * e.AvgTone + e.GoldsteinScale) * e.NumMentions) / SUM(e.NumMentions) * COUNT(*) 
                   / SQRT(AVG(a1.Actor1Count) * AVG(a2.Actor2Count)) * 1000 AS AvgTone
            FROM `gdelt-bq.full.events` AS e
            LEFT JOIN
              (SELECT Actor1Geo_CountryCode AS Actor1, COUNT(*) Actor1Count
               FROM `gdelt-bq.full.events`
               WHERE MonthYear >= {start}
               AND MonthYear < {end}
               GROUP BY Actor1Geo_CountryCode) AS a1
            ON e.Actor1Geo_CountryCode = a1.Actor1
            LEFT JOIN
              (SELECT Actor2Geo_CountryCode AS Actor2, COUNT(*) Actor2Count
               FROM `gdelt-bq.full.events`
               WHERE MonthYear >= {start}
               AND MonthYear < {end}
               GROUP BY Actor2Geo_CountryCode) AS a2
            ON e.Actor2Geo_CountryCode = a2.Actor2
            WHERE e.MonthYear >= {start}
            AND e.MonthYear < {end}
            AND e.Actor1Geo_CountryCode IS NOT NULL
            AND e.Actor2Geo_CountryCode IS NOT NULL
            GROUP BY e.Actor1Geo_CountryCode, e.Actor2Geo_CountryCode
            ORDER BY e.Actor1Geo_CountryCode, e.Actor2Geo_CountryCode
            """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(
            start=parameters['range'].value[0],
            end=parameters['range'].value[1],
        )
        df = qe.get_result_dataframe(query)

        countries_to_leave = Utils().get_valid_fips_countries(25000)
        df = df[(df['Actor1Geo'].isin(countries_to_leave)) & (df['Actor2Geo'].isin(countries_to_leave))]
        df.sort_values(['Actor1Geo', 'Actor2Geo'], inplace=True)

        index = pd.MultiIndex.from_product((countries_to_leave, countries_to_leave),
                                           names=['Actor1Geo', 'Actor2Geo'])
        df.index = pd.MultiIndex.from_arrays((df['Actor1Geo'], df['Actor2Geo']),
                                             names=['Actor1Geo', 'Actor2Geo'])
        df.drop(['Actor1Geo', 'Actor2Geo'], axis=1, inplace=True)
        df = df.reindex(index, fill_value=0.0).reset_index()
        df.sort_values(['Actor1Geo', 'Actor2Geo'], inplace=True)

        dist_matrix = df['AvgTone'].values.reshape((-1, df.groupby('Actor1Geo')['Actor2Geo'].count().unique()[0]))

        down_limit, up_limit = np.percentile(dist_matrix, (1, 99))
        dist_matrix = np.clip(dist_matrix, down_limit, up_limit)

        labels_idx = pd.Series(df['Actor1Geo'].unique(), name='country_id')

        n_clusters = parameters['n_clusters'].value

        if parameters['method'].value == 'agglomerative':
            model = AgglomerativeClustering(
                n_clusters=n_clusters,
                affinity='precomputed',
                linkage='complete',
                compute_full_tree=True,
            )
        elif parameters['method'].value == 'britch':
            model = Birch(
                branching_factor=5,
                n_clusters=n_clusters
            )
        elif parameters['method'].value == 'kmeans':
            model = KMeans(
                n_clusters=n_clusters
            )

        if parameters['actor_type'].value == 1:
            clusters = model.fit_predict(dist_matrix)
        else:
            clusters = model.fit_predict(dist_matrix.T)

        cluster_df = pd.concat([pd.Series(clusters, name='cluster_id'), labels_idx], axis=1)
        cluster_df = cluster_df.join(Utils().get_fips_iso_mapping(),
                                     on=['country_id'],
                                     how='right',
                                     ).fillna(-1)
        cluster_df['country_name'] = cluster_df['country_id'].map(Utils().get_fips_country_id_to_name_mapping())
        cluster_df.rename({'ISO': 'country_iso'}, axis=1, inplace=True)
        # Uncomment to write result to csv
        # cluster_df.groupby('cluster_id')['country_name'].apply(lambda countries: '; '.join(countries)).to_csv('clustering_result.csv')

        fig = px.choropleth(
            cluster_df,
            locations='country_iso',
            locationmode='ISO-3',
            color='cluster_id',
            hover_name='country_name',
            hover_data=['cluster_id'],
            labels={'country_name': 'Country Name',
                    'cluster_id': 'Cluster ID'},
            color_continuous_scale=px.colors.qualitative.Alphabet,
        )
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        clustering_method_mapping = pd.Series(['Agglomerative', 'Britch', 'KMeans'],
                                              index=['agglomerative', 'britch', 'kmeans'])
        ClusteringMethodParam = type("ClusteringMethodParam",
                                     (GenericCategoryParameter,),
                                     {"id_to_name_mapping":clustering_method_mapping})

        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (ActorTypeParameter, ('actor_type', 'Country role')),
            (ClusteringMethodParam, ('method', 'Clustering method')),
            (IntParameter, ('n_clusters', 'Clusters number'))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201906"),
            'actor_type': 2,
            'method': 'britch',
            'n_clusters': 20,
        }

    @staticmethod
    def get_name():
        return """Countries clustering """

    @staticmethod
    def get_description():
        return "Clustering of countries by average tone multiplied bu event count \
        between each pair of countries"

    @staticmethod
    def check_params(params):
        assert 0 < int(params['n_clusters']) < 260, \
            ("Wrong number of clusters", 'n_clusters')
        return True


