from plotly.offline import plot
import plotly_express as px
import pandas as pd
import numpy as np
from sklearn.cluster import Birch, AgglomerativeClustering, KMeans, AffinityPropagation

from ..utils.utils import QueryExecutor, Utils
from ..parametrs.date_parameters import MonthRangeParameter
from ..parametrs.category_parameters import ActorTypeParameter, GenericCategoryParameter
from ..parametrs.base_parameters import IntParameter
from .function import Function


class DomesticPolicyClustering(Function):
    def __init__(self):
        self.query = """
            SELECT Actor1Geo_CountryCode AS ActorGeo,
                   Actor1Type1Code AS Type1,
                   Actor2Type1Code AS Type2,
                   SUM(AvgTone * NumMentions) / SUM(NumMentions) * count(*) AS AvgTone
            FROM `gdelt-bq.full.events`
            WHERE MonthYear >= {start}
            AND MonthYear < {end}
            AND Actor1Geo_CountryCode IS NOT NULL
            AND Actor1Geo_CountryCode = Actor2Geo_CountryCode 
            GROUP BY Actor1Geo_CountryCode, Actor1Type1Code, Actor2Type1Code
            ORDER BY Actor1Geo_CountryCode, Actor1Type1Code, Actor2Type1Code
            """

    def get_plot(self, parameters):
        qe = QueryExecutor()
        query = self.query.format(
            start=parameters['range'].value[0],
            end=parameters['range'].value[1],
        )
        df = qe.get_result_dataframe(query)

        countries_to_leave = Utils().get_valid_fips_countries(25000)
        df = df[(df['ActorGeo'].isin(countries_to_leave))]

        multi_index = pd.MultiIndex.from_product(
            [df['ActorGeo'].unique(), df['Type1'].unique(), df['Type2'].unique()],
            names=['ActorGeo', 'Type1', 'Type2'])
        df.index = pd.MultiIndex.from_arrays(
            [df['ActorGeo'], df['Type1'], df['Type2']],
            names=['ActorGeo', 'Type1', 'Type2'])
        df.drop(['ActorGeo', 'Type1', 'Type2'], axis=1, inplace=True)
        df = df.reindex(multi_index).reset_index()
        df.fillna(0., inplace=True)
        df.sort_values(['ActorGeo', 'Type1', 'Type2'], inplace=True)
        df.index = np.arange(df.shape[0])
        df = df[(df.Type1 != 0.0) & df.Type2 != 0.0]

        types_no = np.unique(df.groupby('ActorGeo')['AvgTone'].count())[0]
        data = df['AvgTone'].values.reshape((-1, types_no))
        labels = df['ActorGeo'].unique()
        norm_data = (data - np.mean(data, axis=1)[:, np.newaxis]) / np.std(data, axis=1)[:, np.newaxis]

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
        elif parameters['method'].value == 'affinity_prop':
            model = AffinityPropagation()

        clusters = model.fit_predict(norm_data)
        cluster_df = pd.DataFrame({'country_id': labels, 'cluster_id': clusters})

        cluster_df = cluster_df.join(Utils().get_fips_iso_mapping(),
                                     on=['country_id'],
                                     how='right',
                                     ).fillna(-1)
        cluster_df.rename({'ISO': 'country_iso'}, axis=1, inplace=True)
        cluster_df['country_name'] = cluster_df['country_id'].map(Utils().get_fips_country_id_to_name_mapping())
        print(Utils().get_fips_country_id_to_name_mapping()[:5])

        fig = px.choropleth(
            cluster_df,
            locations='country_iso',
            locationmode='ISO-3',
            color='cluster_id',
            hover_name='country_name',
            hover_data=['cluster_id'],
            labels={'country_name': 'Country Name',
                    'cluster_id': 'Cluster ID'},
            color_continuous_scale=px.colors.colorbrewer.Paired,
        )
        return plot(fig, include_plotlyjs=True, output_type='div')

    @staticmethod
    def get_parameters():
        clustering_method_mapping = pd.Series(['Agglomerative', 'Britch', 'KMeans', 'AffinityPropagation'],
                                              index=['agglomerative', 'britch', 'kmeans', 'affinity_prop'])
        ClusteringMethodParam = type("ClusteringMethodParam",
                                     (GenericCategoryParameter,),
                                     {"id_to_name_mapping":clustering_method_mapping})

        return [
            (MonthRangeParameter, ('range', 'Time range')),
            (ClusteringMethodParam, ('method', 'Clustering method')),
            (IntParameter, ('n_clusters', 'Clusters number'))
        ]

    @staticmethod
    def get_default_parameters():
        return {
            'range': ("201301", "201906"),
            'method': 'britch',
            'n_clusters': 20,
        }

    @staticmethod
    def get_name():
        return """Domestic policy clustering """

    @staticmethod
    def get_description():
        return "Clustering of countries by average tone multiplied bu event count \
        between each pair of countries"

    @staticmethod
    def check_params(params):
        if params['method'] == 'affinity_prop':
            assert int(params['n_clusters']) == 0, \
                ("for Affinity Propagation Number of clusters must be 0", 'n_clusters')
        else:
            assert 0 < int(params['n_clusters']) < 260, \
                ("Wrong number of clusters", 'n_clusters')

        return True


