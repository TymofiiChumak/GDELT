from django.shortcuts import render

from django.utils.safestring import mark_safe
from ..functions.function_utils import FunctionUtil

fu = FunctionUtil()


def make_card(name, label, description):
    """
    :param name: name of function
    :param label: name of function to display
    :param description: description of function
    :return: html code of card to embed into page
    """
    card = """
    <div class="card" style="height: 250px">
        <h5 class="card-header">
            {0}
        </h5>
        <div class="overflow-auto" style="height: 100%">
            <div class="card-body">
                <p class="card-text">
                    {1}
                </p>
            </div>
        </div>
        <div class="card-footer">
            <a href="/set_parameters/{2}" class="btn btn-info" role="button">GO</a>
        </div>
    </div>""".format(label, description, name)
    return card


def make_row(descs):
    """
    :param descs: descriptions of 4 functions
    :return: html code of row with four cards to embed into page
    """
    descs += [None] * (4 - len(descs))
    row = """<div class="row">"""
    for desc in descs:
        row += """<div class="col-md-3">"""
        if desc:
            name, label, description = desc
            row += make_card(name, label, description)
        row += """</div>"""
    row += """</div>"""
    return row


def make_rows(descs):
    """
    :param descs: descriptions of all functions
    list os tuples (function name, function name to display, function description)
    :return: html code to embed into page
    """
    rows = ""
    rows_no = int(len(descs) / 4) + (len(descs) % 4  > 0)
    for i in range(rows_no):
        rows += make_row(descs[i * 4: (i + 1) * 4])


def main_index(request):
    """
    :param request: GET request with empty body
    :return: html code for main page with cards inserted
    """
    card_rows = mark_safe(make_row(fu.get_functions_description()))
    context = {
        'cards': card_rows
    }
    return render(request, 'main.html', context)
