from rdflib import Graph

# Crear un gráfico RDF
g = Graph()

# Cargar los datos de los archivos TTL en el mismo gráfico
cod_path = "cod/main.ttl"
data_path = "data/main.ttl"
print(f'Parsing {cod_path}')
g.parse(cod_path, format="ttl")
print(f'Parsed {cod_path}')
print(f'Parsing {data_path}')
g.parse(data_path, format="ttl")
print(f'Parsed {data_path}')

# Guardar el gráfico combinado en un nuevo archivo
print('Serializing result/main.ttl')
g.serialize(destination="result/main.ttl", format="ttl")
print('Serialized result/main.ttl')
