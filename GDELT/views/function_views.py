from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
import json
from ..functions.function_utils import FunctionUtil


@csrf_exempt
def make_plot_request(request, function):
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
    return render(request, 'loading.html', {})

@csrf_exempt
def wait_for_plot(request):
    params = json.loads(request.body)
    try:
        FunctionUtil().function_pool.wait_result(params['job_uuid'])
        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error",
                             "message": str(e.args)})


def draw_plot(request, function, job_uuid):
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
        raise e
        return JsonResponse({"status": "error",
                             "message": str(e.args)})
