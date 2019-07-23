from multiprocessing.dummy import Pool
from threading import Lock
import uuid
from ..utils.utils import Singleton
from .event_count import EventCount
from .coutry_connection_count import CountryConnectionCount
from .country_relations import CountryRelations
from .event_density_by_country import EventDensityByCountry
from .event_density_timeline import EventDensityTimeline
from .events_corelation import EventCorrelation
from .event_base_type import EventBaseType
from .domestic_policy_clustering import DomesticPolicyClustering
from .clustering import Clustering

class FunctionUtil(metaclass=Singleton):

    def __init__(self):
        self.function_pool = FunctionPool(self.get_plot)
        self.function_list = [
            ('event_count', EventCount()),
            ('country_connection_count', CountryConnectionCount()),
            ('event_count_by_country', CountryRelations()),
            ('event_density_by_country', EventDensityByCountry()),
            ('event_density_timeline', EventDensityTimeline()),
            ('event_correlation', EventCorrelation()),
            ('event_base_type', EventBaseType()),
            ('clustering', Clustering()),
            ('domestic_policy_clustering', DomesticPolicyClustering())
        ]

    def get_function_by_name(self, function_name):
        return dict(self.function_list)[function_name]

    def get_parameters(self):
        return {name: function.get_parameters() for name, function in self.function_list}

    def get_function_description(self):
        return [(name, function.get_name(), function.get_description()) for name, function in self.function_list]

    def get_plot(self, args):
        function_name, param_dict = args
        function = self.get_function_by_name(function_name)
        function_params_dict = {names[0]: param for param, names in function.get_parameters()}
        params_dict = {param_name: function_params_dict[param_name](value)
                       for param_name, value in param_dict.items()}
        return function.get_plot(params_dict)

    def check_params(self, function_name, param_dict):
        function = self.get_function_by_name(function_name)
        function_params_dict = {names[0]: param for param, names in function.get_parameters()}

        def check_param_value(param_name, value):
            try:
                return function_params_dict[param_name].check_params(value)
            except AssertionError as e:
                e.args += (param_name,)
                raise e
        for param_name, value in param_dict.items():
            check_param_value(param_name, value)

        function.check_params(param_dict)


class FunctionPool(metaclass=Singleton):

    def __init__(self, fun):
        self.pool = Pool(4)
        self.fun = fun
        self.jobs = {}
        self.jobs_look = Lock()

    def add_task(self, args):
        res = self.pool.apply_async(self.fun, (args,))
        job_uuid = uuid.uuid4()
        with self.jobs_look:
            self.jobs[str(job_uuid)] = res
        return job_uuid

    def check_if_complete(self, job_uuid):
        with self.jobs_look:
            is_complete = self.jobs[job_uuid].ready()
        return is_complete

    def get_result(self, job_uuid):
        with self.jobs_look:
            value = self.jobs[job_uuid].get()
        return value

    def wait_result(self, job_uuid):
        with self.jobs_look:
            job = self.jobs[job_uuid]
        job.wait()
