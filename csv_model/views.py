# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unicodecsv
from django.http import HttpResponse
from django.views.generic import View


class CSVGeneratorView(View):
    model = None
    file_name = None
    queryset = None
    empty_qs_message = 'No data for now'
    encoding = 'utf-8'

    def __init__(self, *args, **kwargs):
        if not self.model and not 'model' in kwargs:
            raise NotImplementedError(
                "You must assign a model instance "
                "to your {class_name} model "
                "attribute.".format(
                    class_name=self.__class__.__name__
                )
            )

        if not self.file_name:
            self.file_name = self.__class__.__name__

        super(CSVGeneratorView, self).__init__(*args, **kwargs)

    def _get_csv_headers(self, qs):
        # Because of the python nature the keys of the ValuQuerySet
        # do not follow any specific order, we want to make sure
        # the headers are correctly ordered, so we get the order
        # of the keys of the first item inside our queryset to
        # know how they'll be ordered for our model.
        return qs[0].keys()

    def _get_queryset(self):
        if not self.queryset:
            return self.model.objects.all()

        return self.queryset

    def get(self, request, *args, **kwargs):
        queryset = self._get_queryset().values()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % \
                                          self.file_name

        writer = unicodecsv.writer(response, encoding=self.encoding)

        if queryset:
            writer.writerow(self._get_csv_headers(queryset))
            writer.writerows([obj.values() for obj in queryset])
        else:
            writer.writerow([self.empty_qs_message])

        return response
