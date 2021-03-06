# Code usage

## The API
The link between mapotempo API and this plugin is generated by [swagger-codegen](https://github.com/swagger-api/swagger-codegen).    
The generated code is normally usable. But swagger-codegen and swagger-1.2 aren't compatible. ([issue  #1240](https://github.com/swagger-api/swagger-codegen/issues/1240))
The generated code have to be modified.
auth_settings() method in configuration.py have to be replace with   
```python
def auth_settings():
    return {
        'api_key': {
           'type': 'api_key',
           'in': 'query',
           'key': 'api_key',
           'value': get_api_key_with_prefix('api_key')
           },
    }
```
Then for each method in apis folder, authentification settings and content-type for PUT PATCH POST method have to be specified.    
For authentification settings, replace:
```python
auth_settings = []
```
with
```python
auth_settings = ['api_key']
```
And for the Content-Type which must change:   
Replace
```python
header_params['Content-Type'] = self.api_client.select_header_content_type([])
```
with
```python
header_params['Content-Type'] = self.api_client.select_header_content_type(['application/x-www-form-urlencoded'])
```
## The plugin

There are 4 principal parts in this code :
### plugin_mapotempo.py

This class initiates the plugin and instantiates the others class.
This class has been generated by [QGIS plugin builder](https://plugins.qgis.org/plugins/pluginbuilder/) and then modified in order to satisfy the plugin's realization.   

### plugin_mapotempo_dialog.py

There are 4 objects in this class. They are graphic objects : two windows and one widget. A custom QTreeView is also here, in order to do what was asked for the route listing.

### plugin_mapotempo_handle.py

This class binds layer management in QGIS and Mapotempo solution. This class will call the generated [swagger-codegen](https://github.com/swagger-api/swagger-codegen) code.   

### plugin_mapotempo_layer.py

This class manages QGIS layers. When she receives informations from the handle class, she will call the dialog class if graphics changes have to be made. She also manages layer data in QGIS, and draws zonings, points, routes. If data have changed un QGIS attributes table, this class will call handle class which will up the information to mapotempo API.