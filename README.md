# Mapotempo QGis Plugin

Mapotempo QGis Plugin (MapotempoPlugin) is a plugin which can access to Mapotempo data through QGis software

Mapotempo is a planning and optimization web software for delivery tours. Effective for light and heavy vehicles (+ 3.5t)

### Version
0.1

### Tech

This plugin uses python and some library :

* [SwaggerCodeGen] - generates some code which can connect to Mapotempo API
* [Polyline python library]
* [Geojson python library] 
* [PyQt] - UI for python and QGis

### Compiling

```sh
pyrcc4 -o resources_rc.py resources.qrc
cd i18n
lrelease PluginMapotempo_*
```

### Installation

Copy the entire directory containing your new plugin to the QGIS plugin directory.
Then activate your plugin in QGis

### Usage

For the first use, clic on parameters. Enter your API's key and host's key, save
import a map from an other plugin
You can now access your Mapotempo data

### Development

Want to contribute? Great!

### Todo's

