from django.conf.urls import url
from django.contrib import admin
from weatherapp.views import index
from weatherapp.examples import forecast_dashboard, forecast_performance
from . import views  # import "." means import from the current package.
from datetime import datetime

urlpatterns = [
    url('^$', views.index),
    url(r'^admin/', admin.site.urls),
    url(r'^charts/', forecast_dashboard.chart, {'user_selected_city':'KSAC', 'user_selected_day':'4'}, name='chart'),
    url(r'^performance/', forecast_performance.chart, {'user_selected_city':'KSAC',
                                                       'user_selected_day':'4',
                                                       'model':'PCWA',
                                                       'user_selected_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, name='chart'),
]