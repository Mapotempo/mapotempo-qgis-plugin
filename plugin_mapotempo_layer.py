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
    QgsDataSourceURI)
import tempfile
import csv
import sqlite3
import string
import datetime
import time
import unicodedata
import os.path
import ast

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
                if field.name() in json[i]:
                    r.append(json[i][field.name()])
                else:
                    r.append(None)
            if 'lng' in json[i]:
                feature.setGeometry(
                    QgsGeometry.fromPoint(QgsPoint(json[i]['lng'], json[i]['lat'])))
            feature.setAttributes(r)
            pr.addFeatures([feature])

        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.updateFields()

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
            if 'stops' in row: #and 'vehicle_id' in row:
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
                    r.append(i[field.name()])
                else:
                    r.append(None)
            r[len(r) -1] = route_id[iteration] # moche
            iteration += 1
            feature.setAttributes(r)

            pointList = []
            if i['active'] and i['trace'] != 'None':
                pointList = PolylineCodec().decode(i['trace'])
            pointListFinal = []

            for point in pointList:
                pointListFinal.append(QgsPoint(point[1]/10, point[0]/10))
            line = QgsGeometry.fromPolyline(pointListFinal)
            feature.setGeometry(line)

            pr.addFeatures([feature])
            layer.updateExtents()
            layer.updateFields()

        QgsMapLayerRegistry.instance().addMapLayer(layer)
        self.addIcon(layer, 'line')

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
                feature.setGeometry(QgsGeometry.fromMultiPolygon([[[[QgsPoint(point[0],point[1]) for point in polygon ] for polygon in ring] for ring in a['coordinates']]][0]))

            pr.addFeatures([feature])
            layer.updateFields()
            layer.updateExtents()
            if not self.handler.id_zone == idToDraw:
                self.desactive(layer)
        self.addIcon(layer, 'zone')

    # def switchActive(self, layer):
    #     root = QgsProject.instance().layerTreeRoot()
    #     node = root.findLayer(layer.id())
    #     new_state = Qt.Checked
    #     if node.isVisible() == Qt.Unchecked else Qt.Unchecked
    #     node.setVisible(new_state)

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
                    layer.commitChanges()
                elif layer.name() == self.translate.tr("vehicles"):
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.commitChanges()
                elif layer.name() == self.translate.tr("destinations"):
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.commitChanges()
                elif layer.name() == self.translate.tr("Stops"):
                    ids = [f.id() for f in layer.getFeatures()]
                    layer.startEditing()
                    layer.dataProvider().deleteFeatures( ids )
                    layer.commitChanges()
        #self.dock.model.clear()
        self.dock.label_5.setText(self.translate.tr("Done"))

    def refresh(self):
        self.dock.comboBox.clear()
        self.dock.comboBox_2.clear()
        self.dock.model.clear()
        self.clearLayer()
        self.handler.listPlannings()

    def littleRefresh(self):
        self.littleClearLayer()
        #self.handler.HandleUpdate()

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
            info = QgsVectorJoinInfo()
            info.joinLayerId = vehiclesLayer.id()
            info.joinFieldName = "id"
            info.targetFieldName = "vehicle_id"
            info.memoryCache = True
            zoneLayer.addJoin(info)

            categories = []
            alreadyHere = []
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

        info = QgsVectorJoinInfo()
        info.joinLayerId = vehiclesLayer.id()
        info.joinFieldName = "id"
        info.targetFieldName = "vehicle_id"
        info.memoryCache = True
        routeLayer.addJoin(info)

        info = QgsVectorJoinInfo()
        info.joinLayerId = routeLayer.id()
        info.joinFieldName = "id"
        info.targetFieldName = "route_id"
        info.memoryCache = True
        stopLayer.addJoin(info)

        categories = []
        alreadyRouteId = []
        alreadyEnd = []
        for feature in stopLayer.getFeatures():
            route_id = feature.attribute('route_id')
            if not route_id in alreadyEnd:
                if feature.attribute(self.translate.tr("routes") +'_stop_trace') != 'None':
                    pointList = PolylineCodec().decode(feature.attribute(
                        self.translate.tr("routes") +'_stop_trace'))
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

    def joinDestinationVehicle(self): #use after joinStopVehicle
        layers = self.iface.legendInterface().layers()
        stopLayer, destinationLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                destinationLayer = layer
            elif layer.name() == self.translate.tr("Stops"):
                stopLayer = layer

        info = QgsVectorJoinInfo()
        info.joinLayerId = stopLayer.id()
        info.joinFieldName = "destination_id"
        info.targetFieldName = "id"
        info.memoryCache = True
        destinationLayer.addJoin(info)

        categories = []
        alreadyHere = []
        for feature in destinationLayer.getFeatures():
            route_id = feature.attribute(
                self.translate.tr("Stops") + '_route_id')
            if not route_id in alreadyHere:
                # if not route_id:
                #     color = '#bfbfbf'
                # else:
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
                        ' - ' + str(km) + 'Km ' + str(feature.attribute('id')))
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
            name = name + " " + str(stop_id)

            if feature.attribute(self.translate.tr("Stops") + '_active') == False:
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

        

        sorted_by_first = sorted(listFeature, key=lambda tup: tup[0])
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
