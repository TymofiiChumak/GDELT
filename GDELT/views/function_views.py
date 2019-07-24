from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
import json
from ..functions.function_utils import FunctionUtil


@csrf_exempt
def make_plot_request(request, function):
    """
    :param request: POST request with parameter values dict in body at JSON format
    :param function: Name of requested function
    :return: JsonResponse
    Depends on "status field there will be two fields:
    "function" with function name and "job_uuid" with job id if "status" is "ok"
    else "error" with error description and "id" with wrong parameter id
    """
    param_dict = json.loads(request.body)
    try:
        fu = FunctionUtil()
        fu.check_params(function, param_dict=param_dict)
        job_uuid = fu.function_pool.add_task((function, param_dict))
        response_data = {"status": "ok",
                         "function": function,
                         "job_uuid": job_uuid}
        return JsonResponse(response_data)
    except AssertionError as e:
        response_data = {"status": "error",
                         "error": e.args[0],
                         "id": e.args[1]}
        return JsonResponse(response_data)


def loading_page(request, function, job_uuid):
    """
    :param request: GET request without content
    :param function: function name
    :param job_uuid: job id
    Last two parameters are used by page script (are taken from url)
    to build new request
    :return: html code of loading page
    """
    return render(request, 'loading.html', {})


@csrf_exempt
def wait_for_plot(request):
    """
    After receiving a request, tries to wait while job is completed synchronously
    :param request: POST request with JSON body with "job_uuid" parameter
    :return: JSON response with status field
    and optional "message" field with error description
    """
    params = json.loads(request.body)
    try:
        FunctionUtil().function_pool.wait_result(params['job_uuid'])
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error",
                             "message": str(e.args)})


def draw_plot(request, function, job_uuid):
    """
    Must be called only if POST request to wait_for_plot was successful
    :param request: GET request with empty body
    :param function: function name
    :param job_uuid: job id
    :return: page with plot embedded or JSON with error description
    """
    try:
        fu = FunctionUtil()
        title = fu.get_function_by_name(function).get_name()
        plot = mark_safe(fu.function_pool.get_result(job_uuid))
        context = {
            'title': title,
            'plot': plot
        }
        return render(request, 'plot.html', context)
    except Exception as e:
        return JsonResponse({"status": "error",
                             "message": str(e.args)})
