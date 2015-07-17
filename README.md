# Mapotempo QGis Plugin

[Mapotempo] QGis Plugin (MapotempoPlugin) is a plugin which can access to [Mapotempo] data through [QGis] software

[Mapotempo] is a planning and optimization web software for delivery tours. Effective for light and heavy vehicles (+ 3.5t)

### Version
0.1

### Tech

This plugin uses python and some library :

* [SwaggerCodeGen] - generates some code which can connect to [Mapotempo] API
* [Polyline python library]
* [Geojson python library] 
* [PyQt] - UI for python and [QGis]

### Dependencies

```sh
apt-get install pyqt4-dev-tools
```

### Compiling

```sh
make
```

### Installation

Copy the entire directory containing your new plugin to the [QGis] plugin directory.
Then activate your plugin in [QGis]

### Usage

For the first use, clic on parameters. Enter your API's key and host's key, save
import a map from an other plugin
You can now access your [Mapotempo] data

### Development

Want to contribute? Great!

### Todo's




[Mapotempo]:http://www.mapotempo.com/
[SwaggerCodeGen]:https://github.com/swagger-api/swagger-codegen
[Polyline python library]:https://pypi.python.org/pypi/polyline/
[Geojson python library]:https://pypi.python.org/pypi/geojson/
[PyQt]:https://wiki.python.org/moin/PyQt
[QGis]:http://qgis.org