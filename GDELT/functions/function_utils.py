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


class FunctionUtil:
    """
    Util class for handling functions
    """
    __metaclass__ = Singleton

    def __init__(self):
        """
        After creating new Function class it needs to be added into
        self.function_list as tuple pof function name and function instance
        """
        self.function_pool = FunctionPool(self.get_plot)
        self.function_dict = {
            'event_count': EventCount(),
            'country_connection_count': CountryConnectionCount(),
            'event_count_by_country': CountryRelations(),
            'event_density_by_country': EventDensityByCountry(),
            'event_density_timeline': EventDensityTimeline(),
            'event_correlation': EventCorrelation(),
            'event_base_type': EventBaseType(),
            'clustering': Clustering(),
            'domestic_policy_clustering': DomesticPolicyClustering(),
        }

    def get_function_by_name(self, function_name):
        """
        :param function_name: name of function into self.function_list
        :return: function instance by name
        """
        return self.function_dict[function_name]

    def get_parameters(self, function_name):
        """
        :return: list of tuples:
        (class of parameter type, (parameter name, parameter name to display)
        for specified function
        """
        return self.get_function_by_name(function_name).get_parameters()

    def get_functions_description(self):
        """
        :return: returns list of tuples:
        (function name, function name to be displayed, function description)
        from all functions from self.function_dict
        """
        return [(name, function.get_name(), function.get_description())
                for name, function in self.function_dict.items()]

    def get_plot(self, args):
        """
        :param args: tuple of (function name, parameters dictionary)
        :return: plot of function in html
        """
        function_name, param_dict = args
        function = self.get_function_by_name(function_name)
        function_params_dict = {names[0]: param for param, names in function.get_parameters()}
        params_dict = {param_name: function_params_dict[param_name](value)
                       for param_name, value in param_dict.items()}
        return function.get_plot(params_dict)

    def check_params(self, function_name, param_dict):
        """
        Checks all function parameters firstly apply
        "check_params" function on each parameter,
        and then call "check_params" function on function
        :param function_name: name of function
        :param param_dict: parameters dictionary
        :return: True if all parameters meet conditions
        :raise AssertionError with two args:
        first: error description
        second: wrong parameter name to be marked
        """
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


class FunctionPool:
    """
    Class for handling function execution
    Be aware that each job_id is only shared between thread of one process.
    Multiple workers aren't supported,
    as only process has access to its own function pool.
    TODO Move pool to separate server application (maybe new server with REST API)
    """
    __metaclass__ = Singleton

    def __init__(self, fun):
        """
        :param fun: function to run on each task
        """
        self.pool = Pool(4)
        self.fun = fun
        self.jobs = {}
        self.jobs_look = Lock()

    def add_task(self, args):
        """
        Adds new task to pool
        :param args: args witch will be passed to task
        :return: unique task id
        """
        res = self.pool.apply_async(self.fun, (args,))
        job_uuid = uuid.uuid4()
        with self.jobs_look:
            self.jobs[str(job_uuid)] = res
        return job_uuid

    def check_if_complete(self, job_uuid):
        """
        :param job_uuid: job id returned by add_task method
        :return: check if job is completed
        """
        with self.jobs_look:
            is_complete = self.jobs[job_uuid].ready()
        return is_complete

    def get_result(self, job_uuid):
        """
        Can only be called after wait_result function
        :param job_uuid: job id returned by add_task method
        :return: result of function execution
        """
        with self.jobs_look:
            value = self.jobs[job_uuid].get()
        return value

    def wait_result(self, job_uuid):
        """
        Wait for function complete
        :param job_uuid: job id returned by add_task method
        :return: nothing
        """
        with self.jobs_look:
            job = self.jobs[job_uuid]
        job.wait()
