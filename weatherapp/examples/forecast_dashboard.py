from django.shortcuts import render
from django.http import HttpResponse

# Include the `fusioncharts.py` file that contains functions to embed the charts.
from ..fusioncharts import FusionCharts

from ..models import *


# The `chart` function is defined to load data from a Python Dictionary. This data will be converted to
# JSON and the chart will be rendered.

def chart(request, user_selected_city, user_selected_day):

    if request.method == 'POST':
        if request.POST.get('station_dropdown'):
            user_selected_city = request.POST.get('station_dropdown')
        if request.POST.get('day_dropdown'):
            user_selected_day = request.POST.get('day_dropdown')

    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    dataSource = {}
    dataSource['chart'] = {
        "caption": "Forecast Errors For " + user_selected_city +" Made " + user_selected_day +" days ago",
        "theme": "fusion",
        "yAxisMaxValue": "110",
        "yAxisMinValue": "70"
    }

    # Convert the data in the `actualData` array into a format that can be consumed by FusionCharts.
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Main Keys
    city_ids = []
    dataSource['dataset'] = []
    dataSource['linkeddata'] = []
    dataSource['dataset'] = []
    dataSource['categories'] = []

    # Nested Key, Values
    dataset1 = {}
    dataset1['data'] = []
    dataset1['seriesname'] = ['Actuals']

    dataset2 = {}
    dataset2['data'] = []
    dataset2['seriesname'] = ['PCWA Forecast']

    dataset3 = {}
    dataset3['data'] = []
    dataset3['seriesname'] = ['NWS Forecast']

    categories = {}
    categories['category'] = []

    for city in Forecasts.objects.raw("SELECT DISTINCT city_code, 1 as id FROM forecasts"):
        city_ids.append(city.city_code)

    # Iterate through the data in `Country` model and insert in to the `dataSource['data']` list.
    for key in Forecasts.objects.raw("SELECT 1 as id, a.high as actual, f.PCWA, f.NWS, f.GFS_bc, f.GFS, f.EURO, f.EURO_EPS, "
                                     "f.date_valid, f.city_code, ROUND(f.PCWA-a.high) as PCWA_error, "
                                     "ROUND(f.NWS-a.high) as NWS_error, ROUND(f.GFS-a.high) as GFS_error,"
                                     " ROUND(f.EURO-a.high) as EURO_error, ROUND(f.EURO_EPS-a.high) as EPS_error, "
                                     "ROUND(f.GFS_bc-a.high) as GFS_bc_error "
                                     "FROM forecasts as f "
                                     "JOIN actuals AS a ON f.date_valid=a.date_valid And f.city_code = a.station "
                                     "WHERE f.forecast_day = %s AND f.city_code = %s "
                                     "GROUP BY f.date_valid ORDER BY f.date_valid",
                                     [user_selected_day, user_selected_city]):


        data1 = {}
        data2 = {}
        data3 = {}

        category = {}
        category['label'] = key.date_valid.strftime("%m-%d")

        data1['value'] = key.actual
        data2['value'] = key.PCWA
        data3['value'] = key.NWS

        dataset1['data'].append(data1)
        dataset2['data'].append(data2)
        dataset3['data'].append(data3)

        categories['category'].append(category)


    dataSource['dataset'].append(dataset1)
    dataSource['dataset'].append(dataset2)
    dataSource['dataset'].append(dataset3)
    dataSource['categories'].append(categories)
    # Create an object for the Column 2D chart using the FusionCharts class constructor
    column2D = FusionCharts("column3D", "ex1", "400", "500", "chart-1", "json", dataSource)
    line2D = FusionCharts("msline", "ex2", "400", "500", "chart-2", "json", dataSource)
    return render(request, 'weatherapp/charts.html', {'output': column2D.render(), 'output_2': line2D.render(),
                                                       'chartTitle': 'Day ' + user_selected_day + ' Forecast Errors For ' + user_selected_city,
                                                       'city_ids': city_ids})
