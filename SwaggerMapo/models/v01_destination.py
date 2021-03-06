#!/usr/bin/env python
# coding: utf-8

"""
Copyright 2015 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

class V01Destination(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """

    def __init__(self):
        """
        Swagger model

        :param dict swaggerTypes: The key is attribute name and the value is attribute type.
        :param dict attributeMap: The key is attribute name and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'int',
            'name': 'str',
            'street': 'str',
            'postalcode': 'str',
            'city': 'str',
            'lat': 'float',
            'lng': 'float',
            'quantity': 'int',
            'open': 'datetime',
            'close': 'datetime',
            'detail': 'str',
            'comment': 'str',
            'ref': 'str',
            'take_over': 'datetime',
            'take_over_default': 'str',
            'tag_ids': 'list[int]',
            'geocoding_accuracy': 'float'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'street': 'street',
            'postalcode': 'postalcode',
            'city': 'city',
            'lat': 'lat',
            'lng': 'lng',
            'quantity': 'quantity',
            'open': 'open',
            'close': 'close',
            'detail': 'detail',
            'comment': 'comment',
            'ref': 'ref',
            'take_over': 'take_over',
            'take_over_default': 'take_over_default',
            'tag_ids': 'tag_ids',
            'geocoding_accuracy': 'geocoding_accuracy'
        }


        self.id = None  # int


        self.name = None  # str


        self.street = None  # str


        self.postalcode = None  # str


        self.city = None  # str


        self.lat = None  # float


        self.lng = None  # float


        self.quantity = None  # int


        self.open = None  # DateTime


        self.close = None  # DateTime


        self.detail = None  # str


        self.comment = None  # str


        self.ref = None  # str


        self.take_over = None  # DateTime


        self.take_over_default = None  # str


        self.tag_ids = None  # list[int]


        self.geocoding_accuracy = None  # float


    def __repr__(self):
        properties = []
        for p in self.__dict__:
            if p != 'swaggerTypes' and p != 'attributeMap':
                properties.append('{prop}={val!r}'.format(prop=p, val=self.__dict__[p]))

        return '<{name} {props}>'.format(name=__name__, props=' '.join(properties))
