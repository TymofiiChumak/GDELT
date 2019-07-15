from django.shortcuts import render
from django.utils.safestring import mark_safe

from ..functions.function_utils import FunctionUtil


def get_fields(function):
    default_values = FunctionUtil().get_function_by_name(function).get_default_parameters()
    fields_html = ""
    for param_class, params in FunctionUtil().get_parameters()[function]:
        default_value = param_class.get_value_from_default(default_values[params[0]])
        fields_html += param_class.get_field_code(params, default_value)
    return mark_safe(fields_html)


def parameters_index(request, function):
    fields = get_fields(function)
    context = {
        'fields': fields,
        'function': function
    }
    return render(request, 'form.html', context)
