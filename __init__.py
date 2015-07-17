# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginMapotempo
                                 A QGIS plugin
 test
                             -------------------
        begin                : 2015-06-19
        copyright            : (C) 2015 by me
        email                : azazaz@æzaz.fe
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PluginMapotempo class from file PluginMapotempo.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .plugin_mapotempo import PluginMapotempo
    from .plugin_mapotempo_layer import PluginMapotempoLayer
    from .plugin_mapotempo_handle import PluginMapotempoHandle
    __all__ = [
       'SwaggerPetstore', 'apis'
       ]

    return PluginMapotempo(iface)
