import numpy as np
import pandas as pd
from google.cloud import bigquery
from threading import Lock

resource_path = "GDELT/resources"
bigquery_credentials = "GDELT2-c60e8f0ed67d.json"
cameo_country = "CAMEO.country.csv"
cameo_ethic = "CAMEO.ethnic.csv"
cameo_eventcodes = "CAMEO.eventcodes.csv"
cameo_knowngroup = "CAMEO.knowngroup.csv"
cameo_religion = "CAMEO.religion.csv"
cameo_type = "CAMEO.type.csv"
fips_country = "FIPS.country.csv"
fips_region = "FIPS.region.csv"


class Singleton(type):
    _instances = {}
    lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class QueryExecutor(metaclass=Singleton):

    def __init__(self):
        self.client = bigquery.Client.from_service_account_json(
            resource_path + '/' + bigquery_credentials)

    def get_result_dataframe(self,
                             query,
                             index_col_name=None,
                             datetime_cols=None,
                             month_year_cols=None):
        query_job = self.client.query(query)
        rows = []
        for row in query_job:
            rows.append(pd.Series(dict(row.items())))
        df = pd.DataFrame(rows)
        del(rows)
        if datetime_cols is not None:
            for datetime_col in datetime_cols:
                df[datetime_col] = pd.to_datetime(df[datetime_col],
                                                  format='%Y%m%d',
                                                  errors='ignore')
        if month_year_cols is not None:
            for month_year_col in month_year_cols:
                df[month_year_col] = df[month_year_col].apply(
                    lambda date: pd.Timestamp(
                        year=int(date / 100),
                        month=int(date % 100),
                        day=1))
        if index_col_name is not None:
            df.index = df[index_col_name]
            df.drop([index_col_name], inplace=True, axis=1)
        return (df)


class Utils:
    __metaclass__ = Singleton

    def get_cameo_country_id_to_name_mapping(self):
        if hasattr(self, "cameo_country_id_to_name_mapping"):
            return self.cameo_country_id_to_name_mapping
        else:
            cameo_country_df = pd.read_csv(resource_path + '/' + cameo_country, sep='\t')
            self.cameo_country_id_to_name_mapping = cameo_country_df.groupby('CODE')['LABEL'].first()
            del cameo_country_df
            return self.cameo_country_id_to_name_mapping

    def get_cameo_ethnic_id_to_name_mapping(self):
        if hasattr(self, "cameo_ethnic_id_to_name_mapping"):
            return self.cameo_ethnic_id_to_name_mapping
        else:
            cameo_ethic_df = pd.read_csv(resource_path + '/' + cameo_ethic, sep='\t')
            self.cameo_ethnic_id_to_name_mapping = cameo_ethic_df.groupby('CODE')['LABEL'].first()
            del(cameo_ethic_df)
            return self.cameo_ethnic_id_to_name_mapping

    def get_cameo_eventcodes_id_to_name_mapping(self):
        if hasattr(self, "cameo_eventcodes_id_to_name_mapping"):
            return self.cameo_eventcodes_id_to_name_mapping
        else:
            cameo_eventcodes_df = pd.read_csv(resource_path + '/' + cameo_eventcodes, sep='\t')
            self.cameo_eventcodes_id_to_name_mapping = cameo_eventcodes_df.groupby('CAMEOEVENTCODE')['EVENTDESCRIPTION'].first()
            del(cameo_eventcodes_df)
            return self.cameo_eventcodes_id_to_name_mapping

    def get_cameo_eventcodes_id_to_base_mapping(self):
        if hasattr(self, "cameo_eventcodes_id_to_name_mapping"):
            return self.cameo_eventcodes_id_to_base_mapping
        else:
            cameo_eventcodes_df = pd.read_csv(resource_path + '/' + cameo_eventcodes, sep='\t')
            cameo_eventcodes_df['CAMEOBASECODE'] = cameo_eventcodes_df['CAMEOEVENTCODE'].apply(lambda code: code[:2])
            self.cameo_eventcodes_id_to_base_mapping = cameo_eventcodes_df.groupby('CAMEOEVENTCODE')['CAMEOBASECODE'].first()
            del(cameo_eventcodes_df)
            return self.cameo_eventcodes_id_to_base_mapping


    def get_cameo_knowngroups_id_to_name_mapping(self):
        if hasattr(self, "cameo_knowngroups_id_to_name_mapping"):
            return self.cameo_knowngroups_id_to_name_mapping
        else:
            cameo_knowngroup_df = pd.read_csv(resource_path + '/' + cameo_knowngroup, sep='\t')
            self.cameo_knowngroups_id_to_name_mapping = cameo_knowngroup_df.groupby('CODE')['LABEL'].first()
            del(cameo_knowngroup_df)
            return self.cameo_knowngroups_id_to_name_mapping

    def get_cameo_religion_id_to_name_mapping(self):
        if hasattr(self, "cameo_religion_id_to_name_mapping"):
            return self.cameo_religion_id_to_name_mapping
        else:
            cameo_religion_df = pd.read_csv(resource_path + '/' + cameo_religion, sep='\t')
            self.cameo_religion_id_to_name_mapping = cameo_religion_df.groupby('CODE')['LABEL'].first()
            del (cameo_religion_df)
            return self.cameo_religion_id_to_name_mapping

    def get_fips_country_id_to_name_mapping(self):
        if hasattr(self, "fips_country_id_to_name_mapping"):
            return self.fips_country_id_to_name_mapping
        else:
            fips_country_df = pd.read_csv(resource_path + '/' + fips_country,
                                          sep='\t',
                                          names=["CODE", "LABEL"])
            self.fips_country_id_to_name_mapping = fips_country_df.groupby('CODE')['LABEL'].first()
            del (fips_country_df)
            return self.fips_country_id_to_name_mapping

    def get_fips_region_id_to_name_mapping(self):
        if hasattr(self, "fips_region_id_to_name_mapping"):
            return self.fips_region_id_to_name_mapping
        else:
            fips_region_df = pd.read_csv(resource_path + '/' + fips_region, sep='\t')
            self.fips_region_id_to_name_mapping = fips_region_df.groupby('region_code')['region_name'].first()
            del (fips_region_df)
            return self.fips_region_id_to_name_mapping