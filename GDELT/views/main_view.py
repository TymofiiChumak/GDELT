from django.shortcuts import render

from django.utils.safestring import mark_safe
from ..functions.function_utils import FunctionUtil

fu = FunctionUtil()


def make_card(name, label, description):
    card = """
    <div class="card" style="height: 250px">
        <h5 class="card-header">
            {0}
        </h5>
        <div class="card-body">
            <p class="card-text">
                {1}
            </p>
        </div>
        <div class="card-footer">
            <a href="/set_parameters/{2}" class="btn btn-info" role="button">GO</a>
        </div>
    </div>""".format(label, description, name)
    return card


def make_row(descs):
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
    rows = ""
    rows_no = int(len(descs) / 4) + (len(descs) % 4  > 0)
    for i in range(rows_no):
        rows += make_row(descs[i * 4: (i + 1) * 4])


def main_index(request):

    card_rows = mark_safe(make_row(fu.get_function_description()))
    context = {
        'cards': card_rows
    }
    return render(request, 'main.html', context)
