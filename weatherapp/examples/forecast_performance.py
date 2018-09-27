from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime


# Include the `fusioncharts.py` file that contains functions to embed the charts.
from ..fusioncharts import FusionCharts

from ..models import *
from ..forms import *


# The `chart` function is defined to load data from a Python Dictionary. This data will be converted to
# JSON and the chart will be rendered.

def chart(request, user_selected_city, user_selected_day, model, user_selected_date):

    forecast_type = 'daily_comparison'

    if request.method == 'POST':
        if request.POST.get('station_dropdown'):
            user_selected_city = request.POST.get('station_dropdown')
        if request.POST.get('day_dropdown'):
            user_selected_day = request.POST.get('day_dropdown')
        if request.POST.get('forecaster_dropdown'):
            model = request.POST.get('forecaster_dropdown')
        if request.POST.get('start_date'):
            user_selected_date = request.POST.get('start_date') + " 00:00:00"
        if request.POST.get('clicked_date'):
            clicked_date = datetime.strptime(request.POST.get('clicked_date') + "-" + str(datetime.now().year), '%m-%d-%Y')
            user_selected_date = clicked_date.strftime("%Y-%m-%d") + " 00:00:00"
            forecast_type = 'single_day'



    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    dataSource = {}

    dataSource['chart'] = {
        "caption": "Forecast Errors For " + user_selected_city +" Made " + user_selected_day +" days ago from " + model,
        "theme": "fusion",
        "yAxisMaxValue": "110",
        "yAxisMinValue": "70",
        "showLegend": "1",
        "interactiveLegend": "1"
    }

    # Convert the data in the `actualData` array into a format that can be consumed by FusionCharts.
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Main Keys
    city_ids = []
    models = ['PCWA', 'GFS', 'EURO', 'EURO_EPS', 'GFS_bc', 'NWS', 'actual']
    dataSource['dataset'] = []
    dataSource['linkeddata'] = []
    dataSource['dataset'] = []
    dataSource['categories'] = []


    for model in models:
        categories = {}
        categories['category'] = []
        dataset = {}
        dataset['data'] = []
        dataset['seriesname'] = model
        database = database_pull(dataset, categories, user_selected_day, user_selected_city, model, forecast_type, user_selected_date)
        dataSource['dataset'].append(database[0])
    dataSource['categories'].append(database[1])

    city_ids = list(Forecasts.objects.values_list('city_code', flat=True).distinct())
    #for city in Forecasts.objects.raw("SELECT DISTINCT city_code, 1 as id FROM forecasts"):
    #    city_ids.append(city.city_code)


    # Create an object for the Column 2D chart using the FusionCharts class constructor
    #column2D = FusionCharts("column3D", "ex1", "400", "500", "chart-1", "json", dataSource)
    line2D = FusionCharts("msline", "myChart", "800", "600", "chart-1", "json", dataSource)
    line2D.addEvent("dataplotClick","onDataplotClick")

    # If the request to render is coming from a POST request where a line was clicked, send the
    # appropirate data back in a JSON response (This will prevent the entire page from re-rendering).

    if request.POST.get('clicked_date'):
        return JsonResponse(dataSource)
    return render(request, 'weatherapp/performance.html', {'form': DateRangeForm(), 'output': line2D.render(),
                                                       'chartTitle': 'Day ' + user_selected_day + ' Forecast Errors For ' + user_selected_city,
                                                       'city_ids': city_ids,
                                                        'models': models,
                                                        })

def json_builder(data):
    return

def database_pull(dataset, categories, user_selected_day, user_selected_city, model, forecast_type, user_selected_date):
    if forecast_type == 'daily_comparison':
        for key in Forecasts.objects.raw(
                "SELECT 1 as id, a.high as actual, f.PCWA, f.NWS, f.GFS_bc, f.GFS, f.EURO, f.EURO_EPS, "
                "f.date_valid, f.city_code, ROUND(f.PCWA-a.high) as PCWA_error, "
                "ROUND(f.NWS-a.high) as NWS_error, ROUND(f.GFS-a.high) as GFS_error,"
                "ROUND(f.EURO-a.high) as EURO_error, ROUND(f.EURO_EPS-a.high) as EPS_error, "
                "ROUND(f.GFS_bc-a.high) as GFS_bc_error "
                "FROM forecasts as f "
                "JOIN actuals AS a ON f.date_valid=a.date_valid And f.city_code = a.station "
                "WHERE f.forecast_day = %s AND f.city_code = %s "
                "GROUP BY f.date_valid ORDER BY f.date_valid",
                [user_selected_day, user_selected_city]):

            data = {}
            category = {}
            category['label'] = key.date_valid.strftime("%m-%d")
            data['value'] = getattr(key, model)

            dataset['data'].append(data)
            categories['category'].append(category)
    if forecast_type == 'single_day':
        for key in Forecasts.objects.raw(
                "SELECT 1 as id, a.high as actual, f.PCWA, f.NWS, f.GFS_bc, f.GFS, f.EURO, f.EURO_EPS, "
                "f.date_valid, f.date_created, f.forecast_day, f.city_code "
                "FROM forecasts as f "
                "JOIN actuals AS a ON f.date_valid=a.date_valid And f.city_code = a.station "
                "WHERE f.date_valid = %s  AND f.city_code = %s",
                [user_selected_date, user_selected_city]):
            data = {}
            category = {}
            category['label'] = key.date_valid.strftime("%m-%d")
            data['value'] = getattr(key, model)

            dataset['data'].append(data)
            categories['category'].append(category)

    return (dataset, categories)