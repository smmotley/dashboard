from __future__ import unicode_literals
from django.db import models
from bootstrap_datepicker.widgets import DatePicker
from django import forms
import json


# # Create your models here.
# class SalesRecord(models.Model):
#     Region = models.CharField(max_length=100)
#     Country = models.CharField(max_length=50)
#     City = models.CharField(max_length=50)
#     TotalSales = models.IntegerField()
#
#     def __unicode__(self):
#         return u'%s %s %s %s' % (self.Region, self.Country, self.City, self.TotalSales)


class Forecasts(models.Model):
    city_code = models.TextField()
    date_valid = models.DateTimeField()
    forecast_day = models.TextField()
    PCWA = models.TextField()

    def __unicode__(self):
        return u'%s %s %s %s' % (self.city_code, self.date_valid, self.forecast_day, self.PCWA)

    class Meta:
        # Django automatically derives the table name from the database class name and the
        # app that contains it (e.g. "weatherapp" "Forecasts" in this case). The database table will have the name
        # of the app + the name of the Class with an underscore between them (e.g. weatherapp_Forecast in this case).
        # To override the database table name, use the db_table parameter in class Meta (as shown below).
        db_table = 'forecasts'

class DateRange(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    # start_time = models.TimeField()
    # end_time = models.TimeField()
    def __unicode__(self):
        return u'%s %s %s %s' % (self.name, self.start_date, self.end_date)
