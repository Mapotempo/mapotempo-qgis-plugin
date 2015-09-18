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

Le code de ce plugin est en 4 blocs principaux.
### plugin_mapotempo.py

Cette classe permet d'initier le plugin et d'instancier les autres classes

