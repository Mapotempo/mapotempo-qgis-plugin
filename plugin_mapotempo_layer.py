# from PyQt4.QtCore import *
from PyQt4.QtCore import Qt, QVariant
from qgis.gui import QgsMessageBar
# from qgis.core import *
from qgis.core import (
    QgsMapLayerRegistry, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsPoint, QgsProject, QgsSvgMarkerSymbolLayerV2,
    QgsSimpleMarkerSymbolLayerV2, QgsSimpleLineSymbolLayerV2,
    QgsSimpleFillSymbolLayerV2, QgsVectorJoinInfo, QgsSymbolV2,
    QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2,
    QgsPalLayerSettings, QgsRasterLayer, QgsVectorSimplifyMethod,
    QgsDataSourceURI, QgsVectorLayerCache)
import sqlite3
import string
import datetime
import time
import unicodedata
import os.path
import ast
import binascii
import json

from polyline.codec import PolylineCodec
from geojson.utils import coords

import SwaggerMapo
from PyQt4.QtGui import QColor

class PluginMapotempoLayer:

    def __init__(self, dlg, dock, iface, translate):
        self.layerTab = []
        self.dlg = dlg
        self.dock = dock
        self.translate = translate
        self.iface = iface
        self.client = None
        self.handler = None
        self.hashZone = {}
        self.removeZoneTab = []

    def setClient(self, client):
        self.client = client

    def setHandler(self, instance):
        self.handler = instance

    def createLayer(self, model, name):
        """Create a Layer"""

        layer = QgsVectorLayer("Point?crs=epsg:4326", name, "memory")
        mSimplifyMethod = QgsVectorSimplifyMethod()
        mSimplifyMethod.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
        layer.setSimplifyMethod(mSimplifyMethod)
        self.layerTab.append(layer)
        pr = layer.dataProvider()
        types = model().swagger_types
        keys = types.keys()
        attributes = []
        for i in keys:
            if types[i] == 'int':
                attributes.append(QgsField(i, QVariant.Int))
            elif types[i] == 'float':
                attributes.append(QgsField(i, QVariant.Double))
            else:
                attributes.append(QgsField(i, QVariant.String))
        pr.addAttributes(attributes)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.updateFields()
        return layer

    def addAttributesLayer(self, layer, json):
        pr = layer.dataProvider()
        fields = layer.pendingFields()
        for i in range(len(json)):
            r = []
            feature = QgsFeature()
            for field in fields:
                # print layer.fieldNameIndex(field.name())
                if field.name() in json[i]:
                    r.append(json[i][field.name()])
                else:
                    r.append(None)
            if 'lng' in json[i]:
                feature.setGeometry(
                    QgsGeometry.fromPoint(QgsPoint(json[i]['lng'], json[i]['lat'])))
            feature.setAttributes(r)
            pr.addFeatures([feature])
            layer.updateExtents()
            layer.updateFields()
        layer.commitChanges()
        layer.triggerRepaint()

    def fillField(self, json, layer):
        pr = layer.dataProvider()
        fields = layer.pendingFields()
        for i in range(len(json)):
            r = []
            feature = QgsFeature()
            for field in fields:
                if field.name() in json[i]:
                    r.append(unicode(json[i][field.name()]))
                else:
                    r.append(None)
            feature.setAttributes(r)
            pr.addFeatures([feature])
        layer.updateFields()
        layer.commitChanges()
        layer.triggerRepaint()

    def json2sqlite(self, json, model, name):
        f = self.resolve("sqlite/"+ name +".sqlite")
        f = unicodedata.normalize('NFKD', f).encode('ascii','ignore')
        tmp = open(f, "wb")
        db = sqlite3.connect(f)
        c = db.cursor()
        types = model().swagger_types
        query = 'create table `' + name + '` ' +str(tuple(types.keys()))
        c.execute(query)
        
        for i in range(len(json)):
            r = []
            for field in types.keys():
                if field in json[i]:
                    r.append(unicode(json[i][field]))
                else:
                    r.append(None)
            query = 'insert into `' + name + '` ' + 'values ' + string.replace(str(tuple([bytes('?') for i in range(len(r))])), "'", '')
            c = db.cursor()
            c.execute(query, tuple(r))
        db.commit()
        db.close()
        return f

    def createLayerLine(self, model, name, json):
        """Create a Layer"""
        layers = self.iface.legendInterface().layers()
        layer = None
        for l in layers: #a little bit long
            if l.name() == self.translate.tr("Stops"):
                layer = l
                break
        if not layer:
            layer = QgsVectorLayer("LineString?crs=epsg:4326", name, "memory")
            mSimplifyMethod = QgsVectorSimplifyMethod()
            mSimplifyMethod.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
            layer.setSimplifyMethod(mSimplifyMethod)
            self.layerTab.append(layer)
            pr = layer.dataProvider()
            types = model().swagger_types
            keys = types.keys()
            attributes = []
            for i in keys:
                if i == 'trace':
                    continue
                elif types[i] == 'int':
                    attributes.append(QgsField(i, QVariant.Int))
                elif types[i] == 'float':
                    attributes.append(QgsField(i, QVariant.Double))
                else:
                    attributes.append(QgsField(i, QVariant.String))
            attributes.append(QgsField('route_id', QVariant.Int))
            pr.addAttributes(attributes)
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            layer.updateFields()


        fields = layer.pendingFields()
        jsonstop = []

        route_id = []
        for row in json:
            if 'stops' in row:
                jsontmp = row['stops']
                for rowStop in jsontmp:
                    jsonstop.append(rowStop)
                    route_id.append(row['id'])
        pr = layer.dataProvider()

        iteration = 0
        for i in jsonstop:

            r = []
            feature = QgsFeature()
            for field in fields:
                if field.name() in i:
                    r.append(unicode(i[field.name()]))
                elif field.name() == 'route_id':
                    r.append(route_id[iteration])
                else:
                    r.append(None)
            iteration += 1

            pointList = []
            if i['active'] and i['trace'] != 'None':
                pointList = PolylineCodec().decode(i['trace'])
            pointListFinal = []

            for point in pointList:
                pointListFinal.append(QgsPoint(point[1]/10, point[0]/10))
            line = QgsGeometry.fromPolyline(pointListFinal)
            if len(pointListFinal) != 0: #to aviod save problem with pause and non active
                feature.setGeometry(line)
            feature.setAttributes(r)
            pr.addFeatures([feature])
            layer.updateExtents()
            layer.updateFields()
        layer.commitChanges()
        layer.triggerRepaint()
        self.addIcon(layer, 'line')

    def changeVehicleAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'name':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'color':
                    if self.is_bgcolor(changedAttributesValues[i][a].encode('utf8')):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'rest_stop':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'rest_start':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'close':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'open':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'rest_duration':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'capacity':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'consumption':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'emission':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'speed_multiplicator':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    elif not changedAttributesValues[i][a]:
                        kwargs[str(fields[a].name())] = None
                    else:
                        valid = False

            if valid and len(kwargs) > 0:
                cache = QgsVectorLayerCache(lyr, 10000)
                feat = QgsFeature()
                cache.featureAtId(i, feat)
                featId = int(feat['id'])
                 # have to see the API
                self.handler.update_vehicle(featId, refresh=False, **kwargs)
                cache.removeCachedFeature(feat.id())
                #mesage todo

    def changeZoningAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'name':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')

            if valid and len(kwargs) > 0:
                cache = QgsVectorLayerCache(lyr, 10000)
                feat = QgsFeature()
                cache.featureAtId(i, feat)
                featId = int(feat['id'])
                 # have to see the API
                self.handler.update_name_zone(featId, refresh=False, **kwargs)
                cache.removeCachedFeature(feat.id())
                #mesage todo

    def changeStopAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) != u'active':
                    continue
                elif changedAttributesValues[i][a] == u'True' or changedAttributesValues[i][a] == u'False':
                    cache = QgsVectorLayerCache(lyr, 10000)
                    feat = QgsFeature()
                    cache.featureAtId(i, feat)
                    featId = int(feat['id'])
                    routeId = int(feat['route_id'])
                    if changedAttributesValues[i][a] == u'True':
                        self.handler.update_stop(routeId, featId, 'CHECKED', refresh=False)
                    elif changedAttributesValues[i][a] == u'False':
                        self.handler.update_stop(routeId, featId, 'UNCHECKED', refresh=False)
                    cache.removeCachedFeature(feat.id())

    def changeRouteAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) != u'color':
                    continue
                elif self.is_bgcolor(changedAttributesValues[i][a]):
                    cache = QgsVectorLayerCache(lyr, 10000)
                    feat = QgsFeature()
                    cache.featureAtId(i, feat)
                    featId = int(feat['id'])
                    try:
                        vehicleId = int(feat['vehicle_id'])
                    except:
                        vehicleId = None
                    if vehicleId:
                        self.handler.update_color_route(featId, changedAttributesValues[i][a], refresh=False)
                    cache.removeCachedFeature(feat.id())

    def changePlanningAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'name':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'ref':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'date':
                    if self.is_date_correct(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
            if valid and len(kwargs) > 0:
                self.handler.update_planning(refresh=False, **kwargs)

    def is_date_correct(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return False
        else:
            return True

    def changeDestinationAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'name':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'comment':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'city':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'ref':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'details':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'street':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'postalcode':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'take_over':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'open':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'close':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'take_over_default':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'lat':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'lng':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'quantity':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    elif not changedAttributesValues[i][a]:
                        kwargs[str(fields[a].name())] = None
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'speed_multiplicator':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    elif not changedAttributesValues[i][a]:
                        kwargs[str(fields[a].name())] = None
                    else:
                        valid = False

            if valid and len(kwargs) > 0:
                cache = QgsVectorLayerCache(lyr, 10000)
                feat = QgsFeature()
                cache.featureAtId(i, feat)
                featId = int(feat['id'])
                 # have to see the API
                self.handler.update_destination(featId, refresh=False, **kwargs)
                cache.removeCachedFeature(feat.id())
                #mesage todo

    def changeStoreAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'city':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'name':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'postalcode':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'street':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'lat':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'lng':
                    if self.is_float(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False

            if valid and len(kwargs) > 0:
                cache = QgsVectorLayerCache(lyr, 10000)
                feat = QgsFeature()
                cache.featureAtId(i, feat)
                featId = int(feat['id'])
                 # have to see the API
                self.handler.update_store(featId, refresh=False, **kwargs)
                cache.removeCachedFeature(feat.id())
                #mesage todo

    def is_float(self, number):
        try:
            float(number)
        except:
            return False
        else:
            return True

    def changeTagAttributes(self, layerId, changedAttributesValues):
        lyr = QgsMapLayerRegistry.instance().mapLayer(layerId)
        fields = lyr.pendingFields()
        for i in changedAttributesValues:
            kwargs = {}
            valid = True
            for a in changedAttributesValues[i]:
                if unicode(fields[a].name()) == u'label':
                    kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                elif unicode(fields[a].name()) == u'icon':
                    if self.is_icon_valid(changedAttributesValues[i][a]):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
                elif unicode(fields[a].name()) == u'color':
                    if self.is_bgcolor(changedAttributesValues[i][a].encode('utf8')):
                        kwargs[str(fields[a].name())] = changedAttributesValues[i][a].encode('utf8')
                    else:
                        valid = False
            if valid and len(kwargs) > 0:
                cache = QgsVectorLayerCache(lyr, 10000)
                feat = QgsFeature()
                cache.featureAtId(i, feat)
                featId = int(feat['id'])
                 # have to see the API
                self.handler.update_tag(featId, refresh=False, **kwargs)
                cache.removeCachedFeature(feat.id())
                #mesage todo

    def is_icon_valid(self, icon):
        if unicode(icon) == u'diamon' | unicode(icon) == u'square' | unicode(icon) == u'square':
            return True
        else:
            return False

    def parse_bgcolor(self, bgcolor):
        if not bgcolor.startswith('#'):
            raise ValueError('A bgcolor must start with a "#"')
        return binascii.unhexlify(bgcolor[1:])

    def is_bgcolor(self, bgcolor):
        try:
            self.parse_bgcolor(bgcolor)
        except Exception as e:
            return False
        else:
            return True

    def drawZone(self, json, name, idToDraw):
        layer = QgsVectorLayer(
            "Polygon?crs=epsg:4326",
            self.translate.tr("Zoning") + " " + str(name),
            "memory")
        self.hashZone[layer.id()] = idToDraw
        mSimplifyMethod = QgsVectorSimplifyMethod()
        mSimplifyMethod.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
        layer.setSimplifyMethod(mSimplifyMethod)
        self.layerTab.append(layer)
        pr = layer.dataProvider()
        types = SwaggerMapo.models.V01Zone().swagger_types
        keys = types.keys()
        attributes = []
        for i in keys:
            if i == 'polygon':
                continue
            elif types[i] == 'int':
                attributes.append(QgsField(i, QVariant.Int))
            elif types[i] == 'float':
                attributes.append(QgsField(i, QVariant.Double))
            else:
                attributes.append(QgsField(i, QVariant.String))

        pr.addAttributes(attributes)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.updateFields()
        fields = layer.pendingFields()

        for i in json:
            try:
                r = []
                feature = QgsFeature()
                for field in fields:
                    if field.name() in i:
                        r.append(i[field.name()])
                    else:
                        r.append(None)

                feature.setAttributes(r)
                a = ast.literal_eval(i['polygon'])
                if a['geometry']['type'] == 'Polygon':
                    polygon = list(coords(a))
                    polygonFinal = []
                    for point in polygon:
                        polygonFinal.append(QgsPoint(point[0], point[1]))
                    form = QgsGeometry.fromPolygon([polygonFinal])
                    feature.setGeometry(form)

                elif a['geometry']['type'] == 'MultiPolygon':
                    feature.setGeometry(QgsGeometry.fromMultiPolygon([[[[QgsPoint(point[0],point[1]) for point in polygon ] for polygon in ring] for ring in a['geometry']['coordinates']]][0]))

                pr.addFeatures([feature])
                layer.updateFields()
                layer.updateExtents()
            except:
                print 'oops'
        if not self.handler.id_zone == idToDraw:
            self.desactive(layer)
        self.addIcon(layer, 'zone')
        # layer.committedGeometriesChanges.connect(self.changeZoneAttributes)
        # layer.committedFeaturesAdded.connect(self.changeZoneAttributes)
        layer.editingStarted.connect(self.reinitTabZoneRemove)
        layer.editingStopped.connect(self.changeZoneAttributes)
        layer.committedFeaturesRemoved.connect(self.removedAttributes)

    def reinitTabZoneRemove(self):
        self.removeZoneTab = []

    def removedAttributes(self, layer, deletedFeatureIds):
        lyr = self.iface.activeLayer()
        after_zone_tab = []
        for feature in lyr.getFeatures():
            after_zone_tab.append(feature.attribute('id'))
        for id_zone in self.handler.id_zones_tab[self.handler.id_zone]:
            if id_zone in after_zone_tab:
                continue
            else:
                self.removeZoneTab.append(id_zone)

    def changeZoneAttributes(self):
        lyr = self.iface.activeLayer()
        features = lyr.getFeatures()
        allGeo = []
        # features
        # bug = True
        for f in features:
            # qgis bug for feature added
            typePoly = 'Polygon'
            geo = f.geometry()
        # for geo in changedGeometries:
            polygon = geo.asPolygon()
            if len(polygon) == 2: # [] is two caracters
                polygon = geo.asMultiPolygon()
                typePoly = 'MultiPolygon'
            # cache = QgsVectorLayerCache(lyr, 10000)
            # feat = QgsFeature()
            # cache.featureAtId(geo, feat)
            try:
                vehicleId = int(f['vehicle_id'])
            except:
                vehicleId = None
            try:
                id_zone = int(f['id'])
            except:
                id_zone = None
            polygon = str(polygon)
            polygon = string.replace(polygon, '(', '[')
            polygon = string.replace(polygon, ')', ']')
            polygonFinal = {
            "type": "Feature",
            "properties": {},
            "geometry": {
              "type": typePoly,
              "coordinates": eval(polygon)
                }
                }
            zone = SwaggerMapo.models.V01Zone()
            zone.id = id_zone
            zone.vehicle_id = vehicleId
            zone.polygon = str(polygonFinal)
            allGeo.append(zone)
        self.handler.update_geo_zone(lyr, allGeo, self.removeZoneTab, refresh=False)

    def desactive(self, layer):
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(layer.id())
        new_state = Qt.Unchecked
        node.setVisible(new_state)

    def collapseTree(self, root):
        nodes = root.children()
        for child in nodes:
            child.setExpanded(False)

    def loadSQLiteLayer(self, name, tmp):
        """load a SQLite file"""
        layer = QgsVectorLayer(tmp + '|layername='+name, name, "ogr")
        self.layerTab.append(layer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def addIcon(self, layer, typeIcon):
        if typeIcon == 'store':
            properties = {
                'name': self.resolve('icons/shopping_estateagent2.svg'),
                'size': '10',
                'color': '255,0,0,255'}
            symbol_layer = QgsSvgMarkerSymbolLayerV2.create(properties)
        elif typeIcon == 'destination':
            properties = {'size': '3', 'color': '#bfbfbf'}
            symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)
        elif typeIcon == 'line':
            properties = {'width': '1', 'color': '#bfbfbf'}
            symbol_layer = QgsSimpleLineSymbolLayerV2.create(properties)
        elif typeIcon == 'zone':
            properties = {'color': '#bfbfbf'}
            symbol_layer = QgsSimpleFillSymbolLayerV2.create(properties)
        else:
            return
        layer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)
        layer.triggerRepaint()

    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)

    def clearLayer(self):
        self.dock.label_5.setText(self.translate.tr("Processing"))
        self.dock.label_5.repaint()
        layers = self.iface.legendInterface().layers()
        for layer in layers: #a little bit long
            if layer in self.layerTab:
                if layer.name() == self.translate.tr("planning"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr("tags"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr("routes"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr("store"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr("vehicles"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr("destinations"):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name() == self.translate.tr('zonings'):
                    layer.committedAttributeValuesChanges.disconnect()
                elif layer.name().split(' ')[0] == self.translate.tr("Zoning"):
                    # layer.committedGeometriesChanges.disconnect()
                    # layer.committedFeaturesAdded.disconnect()
                    layer.editingStopped.disconnect()
                    layer.editingStarted.disconnect()
                    layer.committedFeaturesRemoved.disconnect()
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        self.layerTab = []
        self.dock.label_5.setText(self.translate.tr("Done"))

    def littleClearLayer(self):
        self.dock.label_5.setText(self.translate.tr("Processing"))
        self.dock.label_5.repaint()
        layers = self.iface.legendInterface().layers()
        for layer in layers: #a little bit long
            if layer in self.layerTab:
                if layer.name() == self.translate.tr("routes"):
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.updateFields()
                    layer.commitChanges()
                elif layer.name() == self.translate.tr("vehicles"):
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.updateFields()
                    layer.commitChanges()
                elif layer.name() == self.translate.tr("Stops"):
                    layer.committedAttributeValuesChanges.disconnect()
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.updateFields()
                    layer.commitChanges()
        self.dock.label_5.setText(self.translate.tr("Done"))

    def refresh(self):
        self.dock.comboBox.clear()
        self.dock.comboBox_2.clear()
        self.dock.model.clear()
        self.clearLayer()
        self.handler.listPlannings()

    def littleRefresh(self):
        self.littleClearLayer()
        self.handler.getRoutes(self.handler.id_plan)
        self.handler.getStops(self.handler.id_plan)
        self.handler.getVehicles()
        self.paintStop()
        self.paintDestination()
        self.setLabel()
        self.vehiclesStop()
        self.iface.messageBar().pushMessage(
            self.translate.tr("Done"), duration=3, level=QgsMessageBar.INFO)

    def joinZoneVehicle(self):
        layers = self.iface.legendInterface().layers()
        zoneLayers, vehiclesLayer = [], None
        for layer in layers:
            if layer.id() in self.hashZone:
                tmp = self.hashZone[layer.id()]
                if tmp in self.handler.id_zones_tab:
                    zoneLayers.append(layer)
            if layer.name() == self.translate.tr("vehicles"):
                vehiclesLayer = layer

        for zoneLayer in zoneLayers:
            indexesBefore = zoneLayer.pendingAllAttributesList()
            info = QgsVectorJoinInfo()
            info.joinLayerId = vehiclesLayer.id()
            info.joinFieldName = "id"
            info.targetFieldName = "vehicle_id"
            info.memoryCache = True
            zoneLayer.addJoin(info)

            categories = []
            alreadyHere = []
            indexesAfter = zoneLayer.pendingAllAttributesList()
            for i in range(len(indexesBefore), len(indexesAfter)):
                zoneLayer.setEditorWidgetV2(i, 'Hidden')
            for feature in zoneLayer.getFeatures():
                vehicle_name = feature.attribute(
                    self.translate.tr("vehicles") + "_name")
                if not vehicle_name in alreadyHere:
                    if not vehicle_name:
                        color = '#bfbfbf'
                    else:
                        color = feature.attribute(
                            self.translate.tr("vehicles") + "_color")
                    alreadyHere.append(vehicle_name)
                    sym = QgsSymbolV2.defaultSymbol(zoneLayer.geometryType())
                    sym.setColor(QColor(color))
                    sym.setAlpha(0.5)
                    category = QgsRendererCategoryV2(
                        vehicle_name, sym, vehicle_name)
                    categories.append(category)
            field = self.translate.tr("vehicles") + "_name"
            renderer = QgsCategorizedSymbolRendererV2(field, categories)
            zoneLayer.setRendererV2(renderer)
            zoneLayer.triggerRepaint()
            self.iface.mapCanvas().refresh()

    def joinStopVehicle(self):
        layers = self.iface.legendInterface().layers()
        stopLayer, routeLayer, vehiclesLayer = None, None, None
        for layer in layers:
            if layer.name() == self.translate.tr("routes"):
                routeLayer = layer
            elif layer.name() == self.translate.tr("vehicles"):
                vehiclesLayer = layer
            elif layer.name() == self.translate.tr("Stops"):
                stopLayer = layer

        indexesBefore = stopLayer.pendingAllAttributesList()
        indexesBeforeRoute = routeLayer.pendingAllAttributesList()

        info = QgsVectorJoinInfo()
        info.joinLayerId = vehiclesLayer.id()
        info.joinFieldName = "id"
        info.targetFieldName = "vehicle_id"
        info.memoryCache = False
        routeLayer.addJoin(info)

        indexesAfterRoute = routeLayer.pendingAllAttributesList()
        for i in range(len(indexesBeforeRoute), len(indexesAfterRoute)):
            routeLayer.setEditorWidgetV2(i, 'Hidden')

        info = QgsVectorJoinInfo()
        info.joinLayerId = routeLayer.id()
        info.joinFieldName = "id"
        info.targetFieldName = "route_id"
        info.memoryCache = True
        stopLayer.addJoin(info)
        self.paintStop()

        indexesAfter = stopLayer.pendingAllAttributesList()
        for i in range(len(indexesBefore), len(indexesAfter)):
            stopLayer.setEditorWidgetV2(i, 'Hidden')

    def paintStop(self):
        layers = self.iface.legendInterface().layers()
        stopLayer, routeLayer, vehiclesLayer = None, None, None
        for layer in layers:
            if layer.name() == self.translate.tr("routes"):
                routeLayer = layer
            elif layer.name() == self.translate.tr("vehicles"):
                vehiclesLayer = layer
            elif layer.name() == self.translate.tr("Stops"):
                stopLayer = layer
        categories = []
        alreadyRouteId = []
        alreadyEnd = []
        for feature in stopLayer.getFeatures():
            route_id = feature.attribute('route_id')
            stopTrace = None
            if not route_id in alreadyEnd:
                for feat in routeLayer.getFeatures(): # problem with join have to do like this
                    if feat.attribute('id') == str(route_id):
                        stopTrace = feat.attribute('stop_trace')
                        break;
                if stopTrace != 'None':
                    pointList = PolylineCodec().decode(stopTrace)
                    pointListFinal = []
                    for point in pointList:
                        pointListFinal.append(QgsPoint(point[1]/10, point[0]/10))
                    line = QgsGeometry.fromPolyline(pointListFinal)
                    feature.setGeometry(line)
                    pr = stopLayer.dataProvider()
                    pr.addFeatures([feature])
                    stopLayer.updateExtents()
                    alreadyEnd.append(route_id)

                    alreadyRouteId.append(route_id)
                    color = feature.attribute(
                        self.translate.tr("routes") +
                        '_color')
                    if color == 'None':
                        color = feature.attribute(
                            self.translate.tr("routes") +
                            '_' +
                            self.translate.tr("vehicles") +
                            '_color')
                    route_name = feature.attribute(
                        self.translate.tr("routes") +
                        '_' +
                        self.translate.tr("vehicles") +
                        '_name')
                    sym = QgsSymbolV2.defaultSymbol(stopLayer.geometryType())
                    sym.setColor(QColor(color))
                    sym.setWidth(1.5)
                    sym.setAlpha(0.6)
                    category = QgsRendererCategoryV2(route_id, sym, route_name)
                    categories.append(category)
        field = "route_id"
        renderer = QgsCategorizedSymbolRendererV2(field, categories)
        stopLayer.setRendererV2(renderer)
        stopLayer.triggerRepaint()

        idStopTab = []#id stop trace to null
        for feature in stopLayer.getFeatures():
            stopId = feature.attribute('id')
            if not stopId in idStopTab:
                idStopTab.append(stopId)
            else:
                stopLayer.startEditing()
                feature['id'] = None
                stopLayer.updateFeature(feature)
                stopLayer.commitChanges()
        stopLayer.committedAttributeValuesChanges.connect(self.changeStopAttributes)

    def joinDestinationVehicle(self): #use after joinStopVehicle
        layers = self.iface.legendInterface().layers()
        stopLayer, destinationLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                destinationLayer = layer
            elif layer.name() == self.translate.tr("Stops"):
                stopLayer = layer

        indexesBefore = destinationLayer.pendingAllAttributesList()

        info = QgsVectorJoinInfo()
        info.joinLayerId = stopLayer.id()
        info.joinFieldName = "destination_id"
        info.targetFieldName = "id"
        info.memoryCache = False
        destinationLayer.addJoin(info)
        self.paintDestination()

        indexesAfter = destinationLayer.pendingAllAttributesList()
        for i in range(len(indexesBefore), len(indexesAfter)):
            destinationLayer.setEditorWidgetV2(i, 'Hidden')

    def paintDestination(self):
        layers = self.iface.legendInterface().layers()
        stopLayer, destinationLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                destinationLayer = layer
            elif layer.name() == self.translate.tr("Stops"):
                stopLayer = layer        
        categories = []
        alreadyHere = []
        for feature in destinationLayer.getFeatures():
            route_id = feature.attribute(
                self.translate.tr("Stops") + '_route_id')
            if not route_id in alreadyHere:
                color = feature.attribute(
                    self.translate.tr("Stops") +
                    '_' +
                    self.translate.tr('routes') +
                    '_color')
                if color == 'None':
                    color = feature.attribute(
                        self.translate.tr("Stops") +
                        '_' +
                        self.translate.tr('routes') +
                        '_' +
                        self.translate.tr('vehicles') +
                        '_color')
                if not color:
                    color = '#bfbfbf'

                alreadyHere.append(route_id)
                route_name = feature.attribute(
                    self.translate.tr("Stops") +
                    '_' +
                    self.translate.tr('routes') +
                    '_' +
                    self.translate.tr('vehicles') +
                    '_name')
                sym = QgsSymbolV2.defaultSymbol(destinationLayer.geometryType())

                sym.setColor(QColor(color))
                sym.setSize(3)
                category = QgsRendererCategoryV2(route_id, sym, route_name)
                categories.append(category)
        field = self.translate.tr("Stops") + '_route_id'
        renderer = QgsCategorizedSymbolRendererV2(field, categories)
        destinationLayer.setRendererV2(renderer)
        destinationLayer.triggerRepaint()

    def vehiclesStop(self):
        layers = self.iface.legendInterface().layers()
        destinationLayer, vehiclesLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                destinationLayer = layer
            elif layer.name() == self.translate.tr("vehicles"):
                vehiclesLayer = layer
            elif layer.name() == self.translate.tr("routes"):
                routesLayer = layer
        listVehicle = {}
        colorVehicle = {}

        for feature in vehiclesLayer.getFeatures():
            listVehicle[feature.attribute('name')] = []
            color = feature.attribute('color')
            colorVehicle[feature.attribute('name')] = color

        infoVehicle = {}
        idRouteNull = None
        for feature in routesLayer.getFeatures():
            color = feature.attribute('color')
            if color != 'None':
                colorVehicle[feature.attribute(self.translate.tr("vehicles") + '_' + 'name')] = color
            if feature.attribute('vehicle_id'):
                km = float(feature.attribute('distance'))
                if km:
                    km /= 1000
                timeBegin = feature.attribute('start')
                timeEnd = feature.attribute('end')
                timeTot = 0
                if timeBegin:
                    timeBegin = time.strptime(timeBegin, '%Y-%m-%dT%H:%M:%S')
                    timeEnd = time.strptime(timeEnd, '%Y-%m-%dT%H:%M:%S')
                    timeTot = (time.mktime(timeEnd) - time.mktime(timeBegin))
                infoVehicle[feature.attribute(
                    self.translate.tr('vehicles') + '_name')] = (
                        ' - ' +
                        str(time.strftime("%H:%M", time.gmtime(timeTot))) +
                        ' - ' + str(km) + 'Km ' + str(feature.attribute('stop_out_of_drive_time')) + ' ' +str(feature.attribute('id')))
            else:
                idRouteNull = self.translate.tr("Unplanned") + " " + str(feature.attribute('id'))
                listVehicle[idRouteNull] = []
        listFeature = []
        nonActiveTab = []

        routeIdTab = {}

        for feature in destinationLayer.getFeatures():
            index = feature.attribute(self.translate.tr("Stops") + '_index')
            name = feature.attribute('name')
            vehicle = unicode(feature.attribute(
                self.translate.tr("Stops") +
                '_' +
                self.translate.tr('routes') +
                '_' +
                self.translate.tr('vehicles') +
                '_name'))
            stop_id = feature.attribute(self.translate.tr("Stops") +
            '_id')
            out_of_time = unicode(feature.attribute(
                self.translate.tr("Stops") +
                '_' +
                self.translate.tr('out_of_drive_time')))
            name = name + " " + str(out_of_time) + " " + str(stop_id)

            if feature.attribute(self.translate.tr("Stops") + '_active') == unicode(False): #have to do this to save layer
                nonActiveTab.append(name)
            if vehicle == 'None':
                listVehicle[idRouteNull].append((name, []))
            else:
                date = feature.attribute(self.translate.tr("Stops") + '_time')
                if date:
                    date = time.strptime(date, '%Y-%m-%dT%H:%M:%S')
                    listFeature.append((
                        index,
                        str(time.strftime('%H:%M', date)) + " - " +name,
                        vehicle))
                else:
                    listFeature.append((index, name, vehicle))

        

        sorted_by_first = sorted(listFeature, key=lambda tup: int(tup[0]))
        for v in sorted_by_first:
            listVehicle[v[2]].append((v[1], []))
        self.dock.addVehicles(listVehicle, colorVehicle, infoVehicle, nonActiveTab)

    def setLabel(self):
        layers = self.iface.legendInterface().layers()
        destinationLayer, vehiclesLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                destinationLayer = layer
            elif layer.name() == self.translate.tr('store'):
                storeLayer = layer

        label, label_1 = QgsPalLayerSettings(), QgsPalLayerSettings()
        label.readFromLayer(destinationLayer)
        label.placement = QgsPalLayerSettings.OverPoint
        label.setDataDefinedProperty(
            QgsPalLayerSettings.Size, True, True, '8', '')
        label.setDataDefinedProperty(
            QgsPalLayerSettings.Bold, True, True, '8', '')
        label.setDataDefinedProperty(
            QgsPalLayerSettings.ScaleVisibility, True, True, '1', '')
        label.setDataDefinedProperty(
            QgsPalLayerSettings.MinScale, True, True, '1', '')
        label.setDataDefinedProperty(
            QgsPalLayerSettings.MaxScale, True, True, '2000000', '')
        label_1.readFromLayer(storeLayer)
        label.enabled = True
        label_1.enabled = True
        label.fieldName = self.translate.tr("Stops") +'_index'
        label_1.fieldName = 'name'
        label.writeToLayer(destinationLayer)
        label_1.writeToLayer(storeLayer)
        destinationLayer.triggerRepaint()
        storeLayer.triggerRepaint()

    def hideFields(self):
        for layer in self.layerTab:
            fields = layer.pendingFields()
            for field in fields:
                if layer.name() == self.translate.tr("vehicles"):
                    if field.name() == 'close' or field.name() == 'open' or field.name() == 'rest_start' or field.name() == 'rest_stop' or field.name() == 'rest_duration':
                        fieldName = layer.fieldNameIndex(field.name())
                        layer.setEditorWidgetV2(fieldName, 'DateTime')
                        layer.setEditorWidgetV2Config(fieldName, {'display_format': 'yyyy-MM-dd HH:mm:ss', 'allow_null': True, 'field_format': 'yyyy-MM-ddTHH:mm:ss', 'calendar_popup': False})
                if layer.name() == self.translate.tr("destinations"):
                    if field.name() == 'close' or field.name() == 'open' or field.name() == 'take_over' or field.name() == 'take_over_default':
                        fieldName = layer.fieldNameIndex(field.name())
                        layer.setEditorWidgetV2(fieldName, 'DateTime')
                        layer.setEditorWidgetV2Config(fieldName, {'display_format': 'yyyy-MM-dd HH:mm:ss', 'allow_null': True, 'field_format': 'yyyy-MM-ddTHH:mm:ss', 'calendar_popup': False})
                if layer.name() == self.translate.tr("planning"):
                    if field.name() == 'route_ids':
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                    elif  field.name() == 'tag_ids':
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                    elif field.name() == 'out_of_date':
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                    elif field.name() == 'date':
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'DateTime')
                if layer.name() == self.translate.tr("routes") and field.name() != 'color':
                    layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                if layer.name() == self.translate.tr("zonings") and field.name() == 'zones':
                    layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                if layer.name() == self.translate.tr("Stops") and field.name() != 'active':
                    layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                if field.name().split('_').pop() == 'id' or field.name() == 'stop_trace' or field.name() == 'stops':
                    if not (field.name() == 'vehicle_id' and layer.name().split(' ')[0] == self.translate.tr("Zoning")):
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'Hidden')
                if layer.name().split(' ')[0] == self.translate.tr("Zoning"):
                    if field.name() == 'vehicle_id':
                        fieldName = layer.fieldNameIndex(field.name())
                        layer.setEditorWidgetV2(layer.fieldNameIndex(field.name()), 'ValueMap')
                        dictVehicleValueMap = {}
                        for layer2 in self.layerTab:
                            if layer2.name() == self.translate.tr("routes"):
                                for feature in layer2.getFeatures():
                                    dictVehicleValueMap[feature.attribute(self.translate.tr("vehicles") + '_name')] = feature.attribute('vehicle_id')
                            
                        layer.setEditorWidgetV2Config(layer.fieldNameIndex(field.name()), dictVehicleValueMap)
