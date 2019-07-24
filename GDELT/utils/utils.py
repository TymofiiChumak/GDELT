from calendar import month_name
import pandas as pd
from google.cloud import bigquery
import functools
import threading

resource_path = "GDELT/resources"
bigquery_credentials = "google_cloud_credentials.json"
mapbox_token = "mapbox_token"

cameo_country = "CAMEO.country.csv"
cameo_ethic = "CAMEO.ethnic.csv"
cameo_eventcodes = "CAMEO.eventcodes.csv"
cameo_knowngroup = "CAMEO.knowngroup.csv"
cameo_religion = "CAMEO.religion.csv"
cameo_type = "CAMEO.type.csv"
fips_country = "FIPS.country.csv"
fips_region = "FIPS.region.csv"
fips_iso = "fips-iso-country.csv"
actor1_geo_count_file = "actor1_geo_count.csv"
actor2_geo_count_file = "actor2_geo_count.csv"

lock = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


class Singleton(type):
    """
    implementation of singleton pattern
    should be applied as metaclass
    """
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class QueryExecutor(metaclass=Singleton):
    """
    class for execution of BigQuery queries
    """

    def __init__(self):
        self.client = bigquery.Client.from_service_account_json(
            resource_path + '/' + bigquery_credentials)

    def get_result_dataframe(self,
                             query,
                             index_col_name=None,
                             datetime_cols=None,
                             month_year_cols=None):
        """
        :param query: string query for execution
        :param index_col_name: list of string names of columns
        which will be a index for dataframe
        :param datetime_cols: list of string names of columns
        which will be parsed as pd.Timestamp.
        Time format is the same as SQLDATA column: YYYYMMDD
        :param month_year_cols: list of string names of columns
        which will be parsed as pd.Timestamp.
        Time format is the same as MonthYear column: YYYYMM.
        Will be parsed as first day of month
        :return:
        pandas DataFrame with result of query
        """
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


class Utils(metaclass=Singleton):
    """
    Base class for different util functionality
    """

    def get_cameo_country_id_to_name_mapping(self):
        """
        :return: pandas Series with country name as values
        and CAMEO country codes as index
        """
        if hasattr(self, "cameo_country_id_to_name_mapping"):
            return self.cameo_country_id_to_name_mapping
        else:
            cameo_country_df = pd.read_csv(resource_path + '/' + cameo_country, sep='\t')
            self.cameo_country_id_to_name_mapping = cameo_country_df.groupby('CODE')['LABEL'].first()
            del cameo_country_df
            return self.cameo_country_id_to_name_mapping

    def get_cameo_ethnic_id_to_name_mapping(self):
        """
        :return: pandas Series with ethnic name as values
        and CAMEO ethnic codes as indexes
        """
        if hasattr(self, "cameo_ethnic_id_to_name_mapping"):
            return self.cameo_ethnic_id_to_name_mapping
        else:
            cameo_ethic_df = pd.read_csv(resource_path + '/' + cameo_ethic, sep='\t')
            self.cameo_ethnic_id_to_name_mapping = cameo_ethic_df.groupby('CODE')['LABEL'].first()
            del(cameo_ethic_df)
            return self.cameo_ethnic_id_to_name_mapping

    def get_cameo_eventcodes_id_to_name_mapping(self):
        """
        :return: pandas Series with event name as values
        and CAMEO event codes as indexes
        """
        if hasattr(self, "cameo_eventcodes_id_to_name_mapping"):
            return self.cameo_eventcodes_id_to_name_mapping
        else:
            cameo_eventcodes_df = pd.read_csv(resource_path + '/' + cameo_eventcodes, sep='\t')
            self.cameo_eventcodes_id_to_name_mapping = cameo_eventcodes_df.groupby('CAMEOEVENTCODE')['EVENTDESCRIPTION'].first()
            del(cameo_eventcodes_df)
            return self.cameo_eventcodes_id_to_name_mapping

    def get_cameo_eventcodes_id_to_base_mapping(self):
        """
        :return: pandas Series with root event code as values
        and CAMEO event codes as indexes
        i.e. 021: Appeal for material cooperation -> 02: APPEAL
        """
        if hasattr(self, "cameo_eventcodes_id_to_name_mapping"):
            return self.cameo_eventcodes_id_to_base_mapping
        else:
            cameo_eventcodes_df = pd.read_csv(resource_path + '/' + cameo_eventcodes, sep='\t', dtype='str')
            cameo_eventcodes_df['CAMEOBASECODE'] = cameo_eventcodes_df['CAMEOEVENTCODE'].apply(lambda code: code[:2])
            self.cameo_eventcodes_id_to_base_mapping = cameo_eventcodes_df.groupby('CAMEOEVENTCODE')['CAMEOBASECODE'].first()
            del(cameo_eventcodes_df)
            return self.cameo_eventcodes_id_to_base_mapping

    def get_cameo_base_eventcodes_id_to_name_mapping(self):
        """
        :return: pandas Series with root event name as values
        and CAMEO event codes as indexes
        """
        if hasattr(self, "cameo_eventcodes_id_to_name_mapping"):
            return self.cameo_base_eventcodes_id_to_name_mapping
        else:
            cameo_eventcodes_df = pd.read_csv(resource_path + '/' + cameo_eventcodes, sep='\t', dtype='str')
            cameo_eventcodes_df = cameo_eventcodes_df[cameo_eventcodes_df['CAMEOEVENTCODE'].str.len() == 2]
            self.cameo_base_eventcodes_id_to_name_mapping = cameo_eventcodes_df.groupby('CAMEOEVENTCODE')['EVENTDESCRIPTION'].first()
            del(cameo_eventcodes_df)
            return self.cameo_base_eventcodes_id_to_name_mapping


    def get_cameo_knowngroups_id_to_name_mapping(self):
        """
        :return: pandas Series with known group name as values
        and CAMEO known group code as indexes
        """
        if hasattr(self, "cameo_knowngroups_id_to_name_mapping"):
            return self.cameo_knowngroups_id_to_name_mapping
        else:
            cameo_knowngroup_df = pd.read_csv(resource_path + '/' + cameo_knowngroup, sep='\t')
            self.cameo_knowngroups_id_to_name_mapping = cameo_knowngroup_df.groupby('CODE')['LABEL'].first()
            del(cameo_knowngroup_df)
            return self.cameo_knowngroups_id_to_name_mapping

    def get_cameo_religion_id_to_name_mapping(self):
        """
        :return: pandas Series with religion name as values
        and CAMEO religion code as indexes
        """
        if hasattr(self, "cameo_religion_id_to_name_mapping"):
            return self.cameo_religion_id_to_name_mapping
        else:
            cameo_religion_df = pd.read_csv(resource_path + '/' + cameo_religion, sep='\t')
            self.cameo_religion_id_to_name_mapping = cameo_religion_df.groupby('CODE')['LABEL'].first()
            del (cameo_religion_df)
            return self.cameo_religion_id_to_name_mapping

    def get_fips_country_id_to_name_mapping(self):
        """
        :return: pandas Series with country name as values
        and FIPS country code as indexes
        """
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
        """
        :return: pandas Series with region name as values
        and FIPS region code as indexes
        """
        if hasattr(self, "fips_region_id_to_name_mapping"):
            return self.fips_region_id_to_name_mapping
        else:
            fips_region_df = pd.read_csv(resource_path + '/' + fips_region, sep='\t')
            self.fips_region_id_to_name_mapping = fips_region_df.groupby('region_code')['region_name'].first()
            del (fips_region_df)
            return self.fips_region_id_to_name_mapping

    def get_fips_iso_mapping(self):
        """
        :return: pandas Series with FIPS country code as values
        and ISO alpha-3 country code as indexes
        """
        if hasattr(self, "fips_iso_mapping"):
            return self.fips_iso_mapping
        else:
            self.fips_iso_mapping = pd.read_csv(resource_path + '/' + fips_iso, index_col='FIPS')['ISO']
            return self.fips_iso_mapping

    def format_months_names(self, months):
        """
        :param months: List of strings of months in
        format YYYYMM (the same as MonthYear column)
        :return: List of months in human-readable format
        """
        def fotmat_month(month_year):
            month_year = str(int(month_year))
            year = month_year[:4]
            month = int(month_year[4:])
            return month_name[month] + ', ' + year
        return list(map(fotmat_month, months))


    def get_valid_fips_countries(self, threshold):
        """
        :param threshold:
        :return:
        FIPS country codes for countries that have
        more then threshold event counts for both
        Actor 1 and Actor 2 roles
        """
        actor1_geo_count = pd.read_csv(resource_path + '/' + actor1_geo_count_file).dropna()
        actor2_geo_count = pd.read_csv(resource_path + '/' + actor2_geo_count_file).dropna()
        a1_countries = set(actor1_geo_count[actor1_geo_count['Count'] >= threshold]['Actor1Geo_CountryCode'])
        a2_countries = set(actor2_geo_count[actor2_geo_count['Count'] >= threshold]['Actor2Geo_CountryCode'])
        return list(a1_countries.intersection(a2_countries))

    def get_mapbox_token(self):
        """
        :return: string token for mapbox library
        Watch README.md for instructions for getting token
        """
        if hasattr(self, "mapbox_token"):
            return self.mapbox_token
        else:
            with open(resource_path + '/' + mapbox_token, 'r') as source:
                self.mapbox_token = source.read()
                return self.mapbox_token
