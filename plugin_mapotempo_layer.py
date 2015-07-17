# from PyQt4.QtCore import *
from PyQt4.QtCore import Qt, QVariant
# from qgis.core import *
from qgis.core import (
    QgsMapLayerRegistry, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsPoint, QgsProject, QgsSvgMarkerSymbolLayerV2,
    QgsSimpleMarkerSymbolLayerV2, QgsSimpleLineSymbolLayerV2,
    QgsSimpleFillSymbolLayerV2, QgsVectorJoinInfo, QgsSymbolV2,
    QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2)
import tempfile
import csv

import os.path
import ast

from polyline.codec import PolylineCodec
import geojson

import SwaggerMapo
from PyQt4.QtGui import QColor

class PluginMapotempoLayer:

    def __init__(self, dlg, dock, iface, translate):
        self.dlg = dlg
        self.dock = dock
        self.translate = translate
        self.iface = iface
        self.client = None
        self.handler = None

    def setClient(self, client):
        self.client = client

    def setHandler(self, instance):
        self.handler = instance

    def createLayer(self, model, name):
        """Create a Layer"""

        layer = QgsVectorLayer("Point?crs=epsg:4326", name, "memory")
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
            feature.setGeometry(
                QgsGeometry.fromPoint(QgsPoint(json[i]['lng'], json[i]['lat'])))
            feature.setAttributes(r)
            pr.addFeatures([feature])

        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.updateFields()

    def json2csv(self, json, model):
        """Convert json data in CSV file"""

        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        writer = csv.writer(tmp)
        types = model().swagger_types

        writer.writerow(types.keys())

        tmp.flush()
        for i in range(len(json)):
            r = []
            for field in types.keys():
                if field in json[i]:
                    try: #problem with encodage
                        r.append(json[i][field].encode("UTF-8"))
                    except AttributeError:
                        r.append(json[i][field])
                else:
                    r.append(None)
            try:
                writer.writerow(r)
            except UnicodeEncodeError as ue:
                print ue
            tmp.flush()
        return tmp

    def createLayerLine(self, model, name, json):
        """Create a Layer"""

        layer = QgsVectorLayer("LineString?crs=epsg:4326", name, "memory")
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
        attributes.append(QgsField('route_id', QVariant.Int))
        pr.addAttributes(attributes)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.updateFields()
        fields = layer.pendingFields()
        jsonstop = []

        route_id = []
        for row in json:
            if 'stops' in row and 'vehicle_id' in row:
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
            self.translate.tr("Zoning") + "_" + str(name)+ " " + str(idToDraw),
            "memory")
        pr = layer.dataProvider()
        types = SwaggerMapo.models.V01Zone().swagger_types
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

            polygon = list(geojson.utils.coords(a))
            polygonFinal = []
            for point in polygon:
                polygonFinal.append(QgsPoint(point[0], point[1]))
            form = QgsGeometry.fromPolygon([polygonFinal])
            feature.setGeometry(form)
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

    def loadCSVLayer(self, name, tmp):
        """load a CSV file"""

        uri = "file://"+ tmp.name +"?delimiter=%s" % (",")
        layer = QgsVectorLayer(uri, name, "delimitedtext")
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
            #transparency = layer.layerTransparency()
            layer.setLayerTransparency(60)
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
        if len(layers) > 0:
            layers.pop()
        for layer in layers: #a little bit long
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        self.dock.label_5.setText(self.translate.tr("Done"))

    def refresh(self):
        self.dock.comboBox.clear()
        self.clearLayer()
        self.handler.listPlannings()

    def joinZoneVehicle(self):
        layers = self.iface.legendInterface().layers()
        zoneLayers, vehiclesLayer = [], None
        for layer in layers:
            try:
                tmp = layer.name().split(' ', 1)
                if int(tmp[len(tmp) - 1]) in self.handler.id_zones_tab:
                    zoneLayers.append(layer)
            except ValueError:
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
                sym.setWidth(1)
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
                if not route_id:
                    color = '#bfbfbf'
                else:
                    color = feature.attribute(
                        self.translate.tr("Stops") +
                        '_' +
                        self.translate.tr('routes') +
                        '_' +
                        self.translate.tr('vehicles') +
                        '_color')
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
