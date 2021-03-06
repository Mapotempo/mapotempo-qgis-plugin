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

class V01Customer(object):
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
            'end_subscription': 'str',
            'max_vehicles': 'int',
            'take_over': 'str',
            'store_ids': 'list[int]',
            'job_geocoding_id': 'int',
            'job_optimizer_id': 'int',
            'name': 'str',
            'tomtom_user': 'str',
            'tomtom_password': 'str',
            'tomtom_account': 'str',
            'masternaut_user': 'str',
            'masternaut_password': 'str',
            'router_id': 'int',
            'speed_multiplicator': 'Number',
            'print_planning_annotating': 'int',
            'print_header': 'str',
            'alyacom_association': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'end_subscription': 'end_subscription',
            'max_vehicles': 'max_vehicles',
            'take_over': 'take_over',
            'store_ids': 'store_ids',
            'job_geocoding_id': 'job_geocoding_id',
            'job_optimizer_id': 'job_optimizer_id',
            'name': 'name',
            'tomtom_user': 'tomtom_user',
            'tomtom_password': 'tomtom_password',
            'tomtom_account': 'tomtom_account',
            'masternaut_user': 'masternaut_user',
            'masternaut_password': 'masternaut_password',
            'router_id': 'router_id',
            'speed_multiplicator': 'speed_multiplicator',
            'print_planning_annotating': 'print_planning_annotating',
            'print_header': 'print_header',
            'alyacom_association': 'alyacom_association'
        }
        
        
        self.id = None  # int
        
        
        self.end_subscription = None  # str
        
        
        self.max_vehicles = None  # int
        
        
        self.take_over = None  # str
        
        
        self.store_ids = None  # list[int]
        
        
        self.job_geocoding_id = None  # int
        
        
        self.job_optimizer_id = None  # int
        
        
        self.name = None  # str
        
        
        self.tomtom_user = None  # str
        
        
        self.tomtom_password = None  # str
        
        
        self.tomtom_account = None  # str
        
        
        self.masternaut_user = None  # str
        
        
        self.masternaut_password = None  # str
        
        
        self.router_id = None  # int
        
        
        self.speed_multiplicator = None  # Number
        
        
        self.print_planning_annotating = None  # int
        
        
        self.print_header = None  # str
        
        
        self.alyacom_association = None  # str
        

    def __repr__(self):
        properties = []
        for p in self.__dict__:
            if p != 'swaggerTypes' and p != 'attributeMap':
                properties.append('{prop}={val!r}'.format(prop=p, val=self.__dict__[p]))

        return '<{name} {props}>'.format(name=__name__, props=' '.join(properties))


