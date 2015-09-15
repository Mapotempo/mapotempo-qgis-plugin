from PyQt4.QtCore import QSettings, Qt
from PyQt4 import QtGui, QtCore
from qgis.core import QgsProject, QgsMessageLog
from urllib3.exceptions import MaxRetryError, LocationValueError
from qgis.gui import QgsMessageBar

import json
import SwaggerMapo
import string
import requests
from SwaggerMapo import configuration
from SwaggerMapo.apis import TagsApi
from SwaggerMapo.apis import DestinationsApi
from SwaggerMapo.apis import PlanningsApi
from SwaggerMapo.apis import StoresApi
from SwaggerMapo.apis import VehiclesApi
from SwaggerMapo.apis import ZoningsApi
from SwaggerMapo.rest import ApiException

class PluginMapotempoHandle:
    def __init__(self, layer, dlg, dlg_2, dock, translate):
        self.translate = translate
        self.s = QSettings()
        self.keyConnection = None
        self.hostConnection = None
        self.dlg = dlg
        self.dlg_2 = dlg_2
        self.dock = dock

        self.layer_inst = layer
        self.client = None
        self.id_plan = None
        self.id_zone = None
        self.id_zones_tab = {}

    def handleButtonTags(self):
        """action after Tags clic"""
        self.handleButtonGeneric(
            TagsApi(self.client).get_tags(),
            SwaggerMapo.models.V01Tag,
            self.translate.tr("tags"))
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('tags'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeTagAttributes)

    def handleButtonDest(self):
        self.handleButtonGeoGeneric(
            DestinationsApi(self.client).get_destinations(),
            SwaggerMapo.models.V01Destination,
            self.translate.tr("destinations"),
            'destination')
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('destinations'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeDestinationAttributes)

    def handleButtonStores(self):
        self.handleButtonGeoGeneric(
            StoresApi(self.client).get_stores(),
            SwaggerMapo.models.V01Store,
            self.translate.tr("store"),
            'store')
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('store'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeStoreAttributes)

    def handleButtonGeneric(self, get, model, name):
        """generic action after clic"""
        try:
            data = get
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        else:
            layers = self.layer_inst.iface.legendInterface().layers()
            layer = None
            for l in layers: #a little bit long
                if l.name() == name:
                    layer = l
                    break
            jsondata = self.client.sanitize_for_serialization(data)
            if not layer:
                sqlite = self.layer_inst.json2sqlite(jsondata, model, name)
                self.layer_inst.loadSQLiteLayer(name, sqlite)
            else:
                self.layer_inst.fillField(jsondata, layer)

    def handleButtonGeoGeneric(self, get, model, name, typeIcon):
        """generic action after clic"""

        try:
            data = get
            layers = self.layer_inst.iface.legendInterface().layers()
            layer = None
            for l in layers: #a little bit long
                if l.name() == name:
                    layer = l
                    break
            if not layer:
                layer = self.layer_inst.createLayer(model, name)
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        else:
            jsondata = self.client.sanitize_for_serialization(data)
            if len(jsondata) > 0:
                self.layer_inst.addAttributesLayer(layer, jsondata)
                self.layer_inst.addIcon(layer, typeIcon)

    def handleButtonConnect(self):
        """action after Connection clic"""
        if not self.keyConnection:
            self.dock.label_5.setText(self.translate.tr("No connection"))
            return
        configuration.host = self.hostConnection + "/api/"
        configuration.api_key['api_key'] = self.keyConnection
        self.client = SwaggerMapo.api_client.ApiClient(
            self.hostConnection + "/api/")
        self.layer_inst.setClient(self.client)
        try:
            self.layer_inst.refresh()
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        except ApiException as ae:
            print ae
        except TypeError as te:
            print te

    def handleButtonSave(self):
        self.keyConnection = self.dlg.lineEdit.text()
        self.hostConnection = self.dlg.lineEdit_2.text()
        self.dlg.close()

    def HandleParam(self):
        if self.keyConnection:
            self.dlg.lineEdit.setText(self.s.value("PluginMapotempo/key"))
            self.dlg.lineEdit_2.setText(self.s.value("PluginMapotempo/host"))
        else:
            self.dlg.lineEdit_2.setText('https://app.mapotempo.com')
        self.dlg.show()

    def HandleSelect(self):

        index = self.dock.comboBox.currentIndex()
        tmp = self.dock.comboBox.itemData(index)
        try:
            self.id_plan = int(tmp)
        except:
            return
        else:
            if len(self.layer_inst.layerTab) > 0:
                for layer in self.layer_inst.layerTab:
                    if layer.name() == self.translate.tr("planning"):
                        for feature in layer.getFeatures():
                            if int(feature.attribute('id')) == self.id_plan:
                                return
            self.layer_inst.iface.messageBar().pushMessage(
                self.translate.tr("Processing"), duration=1, level=QgsMessageBar.INFO)
            self.dock.label_5.setText(self.translate.tr("Processing"))
            self.layer_inst.clearLayer()
            self.dock.comboBox_2.clear()
            self.dock.label_5.repaint()
            if self.client:
                self.dock.model.clear()
                self.handleButtonTags()
                self.handleButtonStores()
                self.handleButtonDest()

                self.getPlanningsId(self.id_plan)
                self.getZonings()
                self.getZoneId(self.id_plan)
                self.getStops(self.id_plan)
                self.getVehicles()
                self.getZone()
                self.layer_inst.joinZoneVehicle()
                self.layer_inst.joinStopVehicle()
                self.layer_inst.joinDestinationVehicle()
                self.layer_inst.hideFields()
                root = QgsProject.instance().layerTreeRoot()
                self.layer_inst.collapseTree(root)
                self.layer_inst.vehiclesStop()
                self.layer_inst.setLabel()
                self.layer_inst.iface.messageBar().pushMessage(
                    self.translate.tr("Done"), duration=3, level=QgsMessageBar.INFO)
                self.dock.label_5.setText(self.translate.tr("Done"))
            else:
                self.dock.label_5.setText(
                    self.translate.tr("Connection problem"))
                self.layer_inst.iface.messageBar().pushMessage(
                    self.translate.tr("Connection problem"),
                    level=QgsMessageBar.WARNING)

    def HandleUpdate(self):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        self.layer_inst.iface.messageBar().pushMessage(
            self.translate.tr("Processing"), duration=1, level=QgsMessageBar.INFO)
        self.layer_inst.littleRefresh()
        self.layer_inst.iface.messageBar().pushMessage(
            self.translate.tr("Done"), duration=3, level=QgsMessageBar.INFO)
        self.dock.label_5.setText(self.translate.tr("Done"))

    def HandleApplyZoning(self):
        self.layer_inst.iface.messageBar().pushMessage(
            self.translate.tr("Processing"), duration=1, level=QgsMessageBar.INFO)
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        if id_planning:
            index2 = self.dock.comboBox_2.currentIndex()
            try:
                id_zoning = int(self.dock.comboBox_2.itemData(index2))
            except:
                return
            # layers = self.layer_inst.iface.legendInterface().layers()
            # for layer in layers:
            #     if layer.name() == self.translate.tr('planning'):
            #         lyr = layer
            #         break
            # for feature in lyr.getFeatures():
            #     try:
            #         old_id_zoning = int(feature.attribute('zoning_id'))
            #     except:
            #         old_id_zoning = None
            #     if old_id_zoning == id_zoning:
            #         return
            #     else:
            response = PlanningsApi(self.client).update_planning(id=id_planning, zoning_id=id_zoning)
            self.layer_inst.refresh()
        self.layer_inst.iface.messageBar().pushMessage(
            self.translate.tr("Done"), duration=3, level=QgsMessageBar.INFO)

    def getPlanningsId(self, id_plan):
        lyr = None
        self.handleButtonGeneric(
            [PlanningsApi(self.client).get_planning(id=id_plan)],
            SwaggerMapo.models.V01Planning,
            self.translate.tr("planning"))
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('planning'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changePlanningAttributes)
        self.getRoutes(id_plan)

    def getRoutes(self, id_plan):
        lyr = None
        self.handleButtonGeneric(
            PlanningsApi(self.client).get_routes(planning_id=id_plan),
            SwaggerMapo.models.V01Route,
            self.translate.tr("routes"))
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('routes'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeRouteAttributes)

    def getStops(self, id_plan):
        try:
            data = PlanningsApi(self.client).get_routes(planning_id=id_plan)
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        else:
            jsondata = self.client.sanitize_for_serialization(data)
            self.layer_inst.createLayerLine(
                SwaggerMapo.models.V01Stop,
                self.translate.tr("Stops"),
                jsondata)

    def getVehicles(self):
        self.handleButtonGeneric(
            VehiclesApi(self.client).get_vehicles(),
            SwaggerMapo.models.V01Vehicle,
            self.translate.tr("vehicles"))
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('vehicles'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeVehicleAttributes)

    def getZonings(self):
        self.handleButtonGeneric(
            ZoningsApi(self.client).get_zonings(),
            SwaggerMapo.models.V01Zoning,
            self.translate.tr("zonings"))
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr('zonings'):
                lyr = layer
        lyr.committedAttributeValuesChanges.connect(self.layer_inst.changeZoningAttributes)

    def getZone(self):
        try:
            data = ZoningsApi(self.client).get_zonings()
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        else:
            json = self.client.sanitize_for_serialization(data)
            for row in json:
                if 'zones' in row:
                    self.layer_inst.drawZone(row['zones'], row['name'], row['id'])
                else:
                    self.layer_inst.drawZone([], row['name'], row['id'])

    def getZoneId(self, id_plan):
        layers = self.layer_inst.iface.legendInterface().layers()
        self.id_zones_tab = {}
        planningLayer, zoningLayer = None, None
        for layer in layers:
            if layer.name() == self.translate.tr("planning"):
                planningLayer = layer
            elif layer.name() == self.translate.tr("zonings"):
                zoningLayer = layer
        for feature in planningLayer.getFeatures():
            if str(feature.attribute('id')) == str(id_plan):
                try:
                    self.id_zone = int(feature.attribute('zoning_id'))
                except:
                    self.id_zone = None
        self.dock.comboBox_2.addItem(
            self.translate.tr("Choose zoning to apply"), None)
        for feature in zoningLayer.getFeatures():
            zones = feature.attribute('zones')
            try:
                zones = eval('[' + zones + ']')
            except:
                zones = [[]]
            zonesTab = []
            for zone in zones[0]:
                zonesTab.append(int(zone['id']))
            self.id_zones_tab[int(feature.attribute('id'))] = zonesTab
            self.dock.comboBox_2.addItem(
                self.translate.tr("Zoning")+ ' ' + feature.attribute('name'), int(feature.attribute('id')))

    def newZoningLayer(self):
        if self.client:
            self.dlg_2.show()

    def handleButtonNewZoning(self):
        text = self.dlg_2.lineEdit.text()
        if text:
            self.layer_inst.iface.messageBar().pushMessage(
                self.translate.tr("Processing"), duration=1, level=QgsMessageBar.INFO)
            response = ZoningsApi(self.client).create_zoning(name=text)
            self.layer_inst.refresh()
            self.dlg_2.close()
        self.layer_inst.iface.messageBar().pushMessage(
            self.translate.tr("Done"), duration=3, level=QgsMessageBar.INFO)

    def listPlannings(self):
        try:
            data = PlanningsApi(self.client).get_plannings()
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        except ApiException as ae:
            print ae
            self.dock.label_5.setText(self.translate.tr("Connection problem"))
        else:
            self.saveConnectionData()
            jsondata = self.client.sanitize_for_serialization(data)

            self.dock.comboBox.clear()
            self.dock.comboBox_2.clear()
            self.dock.comboBox.addItem(
                self.translate.tr("Clic to choose a planning"), None)

            for row in jsondata:
                self.dock.comboBox.addItem(
                    unicode(row['name']), row['id'])

    def move_stop(self, route_id, stop_id, position):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        response = PlanningsApi(self.client).move_stop(planning_id=id_planning, id=route_id, stop_id=stop_id, index=position)
        self.layer_inst.littleRefresh()

    def update_stop(self, route_id, stop_id, state, refresh=True):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        active = None
        if state == 'CHECKED':
            active = 'true'
        elif state == 'UNCHECKED':
            active = 'false'
        response = PlanningsApi(self.client).update_stop(planning_id=id_planning, route_id=route_id, id=stop_id, active=active)
        if refresh:#bug table editing
            self.layer_inst.littleRefresh()

    def update_color_route(self, route_id, color, refresh=True):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        response = PlanningsApi(self.client).update_route(planning_id=id_planning, id=route_id, color=color)
        if refresh:#bug table editing
            self.layer_inst.littleRefresh()

    def update_planning(self, refresh=True, **kwargs):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        response = PlanningsApi(self.client).update_planning(id=id_planning, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_tag(self, tagId, refresh=True, **kwargs):
        response = TagsApi(self.client).update_tag(id=tagId, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_store(self, storeId, refresh=True, **kwargs):
        response = StoresApi(self.client).update_store(id=storeId, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_vehicle(self, vehicleId, refresh=True, **kwargs):
        response = VehiclesApi(self.client).update_vehicle(id=vehicleId, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_destination(self, destinationId, refresh=True, **kwargs):
        response = DestinationsApi(self.client).update_destination(id=destinationId, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_name_zone(self, zoningId, refresh=True, **kwargs):
        response = ZoningsApi(self.client).update_zoning(id=zoningId, **kwargs)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def update_geo_zone(self, layer, polygon, removedTab, refresh=True, **kwargs):
        zoningId = None
        zoningName = layer.name().split(self.translate.tr("Zoning") + ' ', 1).pop()
        layers = self.layer_inst.iface.legendInterface().layers()
        zoningLayer = None
        for layer in layers:
            if layer.name() == self.translate.tr("zonings"):
                zoningLayer = layer
        for feature in zoningLayer.getFeatures():
            if feature['name'] == zoningName:
                zoningId = feature['id']
                break

        jsonToSend = self.client.sanitize_for_serialization(polygon)
        for j in jsonToSend:
            j["polygon"] = string.replace(j["polygon"], '\'', '"')
            if not 'id' in j:
                j['id'] = None
            if not 'vehicle_id' in j:
                j['vehicle_id'] = None
                
        for idToRemove in self.layer_inst.removeZoneTab:
            jsonToSend.append({"id":idToRemove, "_destroy": True})

        headers = {'content-type': 'application/json'}
        if not SwaggerMapo.configuration.api_client:
            SwaggerMapo.configuration.api_client = SwaggerMapo.api_client.ApiClient('http://beta.app.mapotempo.com/api')
        url = SwaggerMapo.configuration.api_client.host + '/0.1/zonings/' + str(zoningId) + '.json?api_key=' + self.keyConnection
        zoningToSend = SwaggerMapo.models.V01Zoning()
        zoningToSend.id = zoningId
        zoningToSend.zones = jsonToSend
        payload = self.client.sanitize_for_serialization(zoningToSend)
        r = requests.put(url, data=json.dumps(payload), headers=headers)
        self.getZoneId(self.id_plan)
        if refresh:#bug table editing
            self.layer_inst.refresh()

    def optimize_route(self, idRoute):
        index = self.dock.comboBox.currentIndex()
        id_planning = self.dock.comboBox.itemData(index)
        if id_planning:
            route_id = int(idRoute)
            self.layer_inst.iface.messageBar().pushMessage(self.translate.tr("Route Optimizing..."), duration=35)
            worker = OptimizeWorker(self.client, id_planning, route_id)
            thread = QtCore.QThread()
            worker.moveToThread(thread)
            worker.finished.connect(self.workerFinished)
            worker.error.connect(self.workerError)
            worker.status.connect(self.layer_inst.iface.mainWindow().statusBar().showMessage)
            thread.started.connect(worker.run)
            thread.start()
            self.thread = thread
            self.worker = worker

    def workerFinished(self, ret):
        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        if ret is True:
            # report the result
            self.layer_inst.littleRefresh()
            self.layer_inst.iface.messageBar().pushMessage(self.translate.tr("Done"), duration=3)
        else:
            # notify the user that something went wrong
            self.layer_inst.iface.messageBar().pushMessage(self.translate.tr('Something went wrong! See the message log for more information.'), level=QgsMessageBar.CRITICAL, duration=10)


    def workerError(self, e, exception_string):
        self.layer_inst.iface.mainWindow().statusBar().showMessage('blop')
        QgsMessageLog.logMessage('Worker thread raised an exception:\n {ex}\n{e}'.format(ex=exception_string, e=e), level=QgsMessageLog.CRITICAL)


    def saveConnectionData(self):
        """Save the connection details"""
        self.s.setValue("PluginMapotempo/key", self.keyConnection)
        self.s.setValue("PluginMapotempo/host", self.hostConnection)

class OptimizeWorker(QtCore.QObject):
        
    def __init__(self, client, id_planning, route_id, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.killed = False
        self.id_planning = id_planning
        self.route_id = route_id
        self.client = client

    def run(self):
        ret = False
        try:
            self.status.emit('Task started!')
            PlanningsApi(self.client).optimize_route(planning_id=self.id_planning, id=self.route_id)
            self.status.emit('Task ended!')
            if self.killed is False:
                ret = True
        except Exception, e:
            import traceback
            # forward the exception upstream
            self.error.emit(e, traceback.format_exc())
        self.finished.emit(ret)

    def kill(self):
        self.killed = True

    finished = QtCore.pyqtSignal(bool)
    error = QtCore.pyqtSignal(Exception, basestring)
    status = QtCore.pyqtSignal(str)
