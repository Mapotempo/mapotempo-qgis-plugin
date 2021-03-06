#!/usr/bin/env python
# coding: utf-8

"""
StoresApi.py
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

NOTE: This class is auto generated by the swagger code generator program. Do not edit the class manually.
"""
from __future__ import absolute_import

import sys
import os

# python 2 and python 3 compatibility library
from six import iteritems

from .. import configuration
from ..api_client import ApiClient

class StoresApi(object):

    def __init__(self, api_client=None):
        if api_client:
            self.api_client = api_client
        else:
            if not configuration.api_client:
                configuration.api_client = ApiClient('http://beta.app.mapotempo.com/api')
            self.api_client = configuration.api_client


    def get_stores(self, **kwargs):
        """
        Fetch customer's stores.



        :return: list[V01Store]
        """

        all_params = []

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method get_stores" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores.{format}'.replace('{format}', 'json')
        method = 'GET'

        path_params = {}

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='list[V01Store]', auth_settings=auth_settings)

        return response

    def create_store(self, name, city, **kwargs):
        """
        Create store.


        :param str name:  (required)
        :param str street:
        :param str postalcode:
        :param str city:  (required)
        :param float lat:
        :param float lng:
        :param DateTime open:
        :param DateTime close:

        :return: V01Store
        """

        # verify the required parameter 'name' is set
        if name is None:
            raise ValueError("Missing the required parameter `name` when calling `create_store`")

        # verify the required parameter 'city' is set
        if city is None:
            raise ValueError("Missing the required parameter `city` when calling `create_store`")

        all_params = ['name', 'street', 'postalcode', 'city', 'lat', 'lng', 'open', 'close']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method create_store" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores.{format}'.replace('{format}', 'json')
        method = 'POST'

        path_params = {}

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        if 'name' in params:
            form_params['name'] = params['name']

        if 'street' in params:
            form_params['street'] = params['street']

        if 'postalcode' in params:
            form_params['postalcode'] = params['postalcode']

        if 'city' in params:
            form_params['city'] = params['city']

        if 'lat' in params:
            form_params['lat'] = params['lat']

        if 'lng' in params:
            form_params['lng'] = params['lng']

        if 'open' in params:
            form_params['open'] = params['open']

        if 'close' in params:
            form_params['close'] = params['close']

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='V01Store', auth_settings=auth_settings)

        return response

    def delete_stores(self, ids, **kwargs):
        """
        Delete multiple stores.


        :param list[Integer] ids:  (required)

        :return: str
        """

        # verify the required parameter 'ids' is set
        if ids is None:
            raise ValueError("Missing the required parameter `ids` when calling `delete_stores`")

        all_params = ['ids']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method delete_stores" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores.{format}'.replace('{format}', 'json')
        method = 'DELETE'

        path_params = {}

        query_params = {}

        if 'ids' in params:
            query_params['ids'] = params['ids']

        header_params = {}

        form_params = {}
        files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='str', auth_settings=auth_settings)

        return response

    def geocode_store(self, **kwargs):
        """
        Geocode store.


        :param str name:
        :param str street:
        :param str postalcode:
        :param str city:
        :param float lat:
        :param float lng:
        :param DateTime open:
        :param DateTime close:

        :return: V01Store
        """

        all_params = ['name', 'street', 'postalcode', 'city', 'lat', 'lng', 'open', 'close']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method geocode_store" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores/geocode.{format}'.replace('{format}', 'json')
        method = 'PATCH'

        path_params = {}

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        if 'name' in params:
            form_params['name'] = params['name']

        if 'street' in params:
            form_params['street'] = params['street']

        if 'postalcode' in params:
            form_params['postalcode'] = params['postalcode']

        if 'city' in params:
            form_params['city'] = params['city']

        if 'lat' in params:
            form_params['lat'] = params['lat']

        if 'lng' in params:
            form_params['lng'] = params['lng']

        if 'open' in params:
            form_params['open'] = params['open']

        if 'close' in params:
            form_params['close'] = params['close']

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='V01Store', auth_settings=auth_settings)

        return response

    def get_store(self, id, **kwargs):
        """
        Fetch store.


        :param int id:  (required)

        :return: V01Store
        """

        # verify the required parameter 'id' is set
        if id is None:
            raise ValueError("Missing the required parameter `id` when calling `get_store`")

        all_params = ['id']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method get_store" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores/{id}.{format}'.replace('{format}', 'json')
        method = 'GET'

        path_params = {}

        if 'id' in params:
            path_params['id'] = params['id']

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='V01Store', auth_settings=auth_settings)

        return response

    def update_store(self, id, **kwargs):
        """
        Update store.


        :param int id:  (required)
        :param str name:
        :param str street:
        :param str postalcode:
        :param str city:
        :param float lat:
        :param float lng:
        :param DateTime open:
        :param DateTime close:

        :return: V01Store
        """

        # verify the required parameter 'id' is set
        if id is None:
            raise ValueError("Missing the required parameter `id` when calling `update_store`")

        all_params = ['id', 'name', 'street', 'postalcode', 'city', 'lat', 'lng', 'open', 'close']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method update_store" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores/{id}.{format}'.replace('{format}', 'json')
        method = 'PUT'

        path_params = {}

        if 'id' in params:
            path_params['id'] = params['id']

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        if 'name' in params:
            form_params['name'] = params['name']

        if 'street' in params:
            form_params['street'] = params['street']

        if 'postalcode' in params:
            form_params['postalcode'] = params['postalcode']

        if 'city' in params:
            form_params['city'] = params['city']

        if 'lat' in params:
            form_params['lat'] = params['lat']

        if 'lng' in params:
            form_params['lng'] = params['lng']

        if 'open' in params:
            form_params['open'] = params['open']

        if 'close' in params:
            form_params['close'] = params['close']

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(['application/x-www-form-urlencoded'])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='V01Store', auth_settings=auth_settings)

        return response

    def delete_store(self, id, **kwargs):
        """
        Delete store.


        :param int id:  (required)

        :return: str
        """

        # verify the required parameter 'id' is set
        if id is None:
            raise ValueError("Missing the required parameter `id` when calling `delete_store`")

        all_params = ['id']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError("Got an unexpected keyword argument '%s' to method delete_store" % key)
            params[key] = val
        del params['kwargs']

        resource_path = '/0.1/stores/{id}.{format}'.replace('{format}', 'json')
        method = 'DELETE'

        path_params = {}

        if 'id' in params:
            path_params['id'] = params['id']

        query_params = {}

        header_params = {}

        form_params = {}
        files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept([])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, method, path_params, query_params, header_params,
                                            body=body_params, post_params=form_params, files=files,
                                            response='str', auth_settings=auth_settings)

        return response
