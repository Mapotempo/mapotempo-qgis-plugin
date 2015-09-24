# Utilisation du code

## L'API
Le lien entre l'API et le code du plugin est généré par [swagger-codegen](https://github.com/swagger-api/swagger-codegen)    
Normalement le code est utilisable directement. Or à cause d'incompatibilité entre swagger-codegen et swagger-1.2 ([issue  #1240](https://github.com/swagger-api/swagger-codegen/issues/1240))
le code généré doit être modifié afin qu'il fonctionne.   
Il faut remplacer la méthode auth_settings() dans configuration.py par  
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
Ensuite  pour chaque méthode présente dans le dossier apis il faut préciser les paramètres d'authentification et le content-type pour les méthodes PUT PATCH POST:   
pour les paramètre d'authentification, remplacer
```python
auth_settings = []
```
par
```python
auth_settings = ['api_key']
```
et pour les content-type à changer voici un exemple ci-dessous:   
remplacer
```python
header_params['Content-Type'] = self.api_client.select_header_content_type([])
```
par
```python
header_params['Content-Type'] = self.api_client.select_header_content_type(['application/x-www-form-urlencoded'])
```
Normalement le code généré devrait être fonctionnel.
## Le plugin

Le code de ce plugin est structuré en 4 blocs principaux.
### plugin_mapotempo.py

Cette classe permet d'initier le plugin et d'instancier les autres classes.    
Elle a été générée par le plugin QGIS [plugin builder](https://plugins.qgis.org/plugins/pluginbuilder/) puis modifiée afin de satisfaire la réalisation du plugin mapotempo   

### plugin_mapotempo_dialog.py

Il y a 4 objets dans cette classe. Ce sont que des objets d'interfaces graphiques : deux fenêtres et le widget. Il y a en plus un arbre QTreeView personnalisé afin de pouvoir faire ce qui 
était demandé pour le listing des tournées.

### plugin_mapotempo_handle.py

Cette classe permet de faire le lien entre la gestion des layers dans QGIS et la solution Mapotempo. C'est elle qui va appeler le code généré par [swagger-codegen](https://github.com/swagger-api/swagger-codegen)    

### plugin_mapotempo_layer.py

Cette classe s'occupe de la gestion des layers dans QGIS. Dès qu'elle reçoit des informations de la classe handle, elle va appeler la classe dialog si jamais il y a des changements de fenêtre à faire ou alors elle va gérer les données dans QGIS que ce soit zonages, points, tracés d'itinéraires. S'il y a une modification des données, elle va les transmettre au handle qui les fera remonter en interrogeant l'API.