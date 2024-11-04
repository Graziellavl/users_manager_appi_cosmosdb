from azure.cosmos import CosmosClient, exceptions

cosmos_endpoint = 'https://acdbgvldev.documents.azure.com:443/'
cosmos_key = '6RWzeEoyI8Xuxq82wbz9S3O0L2RGVplh8XtFWwBN3AaSCtw6f2318d5YxOJsbudfGXJO0yA2Pg7LACDbhp5LVA=='
database_name = 'GestorProyectosBD'
container_users = 'Usuarios'
container_projects = 'Proyectos'

client = CosmosClient(cosmos_endpoint, cosmos_key)

# Crear u obtener la base de datos
try:
    database = client.create_database_if_not_exists(id=database_name)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(database_name)


# Crear u obtener el contenedor
try:
    container_users = database.create_container_if_not_exists(
    id=container_users, 
    partition_key={'paths': ['/id'], 'kind': 'Hash'},
    offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    container_users = database.get_container_client(container_users)

container = 'proyectos'
try:
    container_projects = database.create_container_if_not_exists(
    id=container_projects, 
    partition_key={'paths': ['/id'], 'kind': 'Hash'},
    offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    container_projects = database.get_container_client(container_projects)