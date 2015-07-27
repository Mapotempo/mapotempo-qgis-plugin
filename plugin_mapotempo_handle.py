from PyQt4.QtCore import QSettings
from qgis.core import QgsProject
from urllib3.exceptions import MaxRetryError, LocationValueError


import SwaggerMapo

from SwaggerMapo import configuration
from SwaggerMapo.apis import TagsApi
from SwaggerMapo.apis import ProductsApi
from SwaggerMapo.apis import DestinationsApi
from SwaggerMapo.apis import PlanningsApi
from SwaggerMapo.apis import StoresApi
from SwaggerMapo.apis import VehiclesApi
from SwaggerMapo.apis import ZoningsApi
from SwaggerMapo.rest import ApiException

class PluginMapotempoHandle:
    def __init__(self, layer, dlg, dock, translate):
        self.translate = translate
        self.s = QSettings()
        self.keyConnection = None
        self.hostConnection = None
        self.dlg = dlg
        self.dock = dock

        self.layer_inst = layer
        self.client = None
        self.id_plan = None
        self.id_zone = None
        self.id_zones_tab = []

    def handleButtonTags(self):
        """action after Tags clic"""
        self.handleButtonGeneric(
            TagsApi(self.client).get_tags(),
            SwaggerMapo.models.V01Tag,
            self.translate.tr("tags"))

    def handleButtonProd(self):
        """action after Products clic"""
        self.handleButtonGeneric(
            ProductsApi(self.client).get_products(),
            SwaggerMapo.models.V01Product,
            self.translate.tr("prod"))

    def handleButtonDest(self):
        self.handleButtonGeoGeneric(
            DestinationsApi(self.client).get_destinations(),
            SwaggerMapo.models.V01Destination,
            self.translate.tr("destinations"),
            'destination')

    def handleButtonStores(self):
        self.handleButtonGeoGeneric(
            StoresApi(self.client).get_stores(),
            SwaggerMapo.models.V01Store,
            self.translate.tr("store"),
            'store')

    def handleButtonGeneric(self, get, model, name):
        """generic action after clic"""
        try:
            data = get
        except MaxRetryError as mte:
            print mte
        except LocationValueError as lve:
            print lve
        else:
            jsondata = self.client.sanitize_for_serialization(data)
            csv = self.layer_inst.json2csv(jsondata, model)
            self.layer_inst.loadCSVLayer(name, csv)

    def handleButtonGeoGeneric(self, get, model, name, typeIcon):
        """generic action after clic"""

        try:
            data = get
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
        tmp = self.dock.comboBox.currentText().split(' ')
        try:
            self.id_plan = int(tmp[len(tmp) - 1])
        except:
            return
        else:
            if len(self.layer_inst.layerTab) > 0:
                for layer in self.layer_inst.layerTab:
                    if layer.name() == self.translate.tr("planning"):
                        for feature in layer.getFeatures():
                            if feature.attribute('id') == self.id_plan:
                                return
            self.layer_inst.clearLayer()
            self.dock.label_5.repaint()
            if self.client:
                self.dock.label_5.setText(self.translate.tr("Processing"))
                self.dock.listWidget.clear()
                self.dock.model.clear()
                self.handleButtonTags()
                self.handleButtonProd()
                self.handleButtonDest()
                self.handleButtonStores()

                self.getPlanningsId(self.id_plan)
                self.getZonings()
                self.getZoneId(self.id_plan)
                self.getStops(self.id_plan)
                self.getVehicles()
                self.getZone()
                self.layer_inst.joinZoneVehicle()
                self.layer_inst.joinStopVehicle()
                self.layer_inst.joinDestinationVehicle()
                root = QgsProject.instance().layerTreeRoot()
                self.layer_inst.collapseTree(root)
                self.layer_inst.unplannedStop()
                self.layer_inst.vehiclesStop()
                self.layer_inst.setLabel()
                self.dock.label_5.setText(self.translate.tr("Done"))
            else:
                self.dock.label_5.setText(self.translate.tr("Connection problem"))


    def getPlanningsId(self, id_plan):
        self.handleButtonGeneric(
            [PlanningsApi(self.client).get_planning(id=id_plan)],
            SwaggerMapo.models.V01Planning,
            self.translate.tr("planning"))
        self.handleButtonGeneric(
            PlanningsApi(self.client).get_routes(planning_id=id_plan),
            SwaggerMapo.models.V01Route,
            self.translate.tr("routes"))

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

    def getZonings(self):
        self.handleButtonGeneric(
            ZoningsApi(self.client).get_zonings(),
            SwaggerMapo.models.V01Zoning,
            self.translate.tr("zonings"))

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
                self.layer_inst.drawZone(row['zones'], row['name'], row['id'])

    def getZoneId(self, id_plan):
        self.id_zones_tab = []
        layers = self.layer_inst.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == self.translate.tr("planning"):
                planningLayer = layer
            elif layer.name() == self.translate.tr("zonings"):
                zoningLayer = layer
        for feature in planningLayer.getFeatures():
            if str(feature.attribute('id')) == str(id_plan):
                self.id_zone = feature.attribute('zoning_id')
        for feature in zoningLayer.getFeatures():
            self.id_zones_tab.append(feature.attribute('id'))

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
            self.dock.comboBox.addItem(self.translate.tr("Clic to choose a planning"))
            for row in jsondata:
                self.dock.comboBox.addItem(
                    str(row['name']) + " " + str(row['id']))



    def saveConnectionData(self):
        """Save the connection details"""
        self.s.setValue("PluginMapotempo/key", self.keyConnection)
        self.s.setValue("PluginMapotempo/host", self.hostConnection)
