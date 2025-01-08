import random
import string
import uuid

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, DCTERMS

# Configuración
files = [
    "/Users/danielbakas/Documents/Profesional/Semantyk/Interno/Proyectos/Plataforma/Data/Knowledge/data/mex/fed/ef/main.ttl",
    "/Users/danielbakas/Documents/Profesional/Semantyk/Interno/Proyectos/Plataforma/Data/Knowledge/data/mex/fed/ef/gob/main.ttl",
    "/Users/danielbakas/Documents/Profesional/Semantyk/Interno/Proyectos/Plataforma/Data/Knowledge/data/mex/fed/ef/gob"
    "/pow/pe/main.ttl",
    "/Users/danielbakas/Documents/Profesional/Semantyk/Interno/Proyectos/Plataforma/Data/Knowledge/data/mex/fed/ef"
    "/gob/ap/main.ttl",
    "/Users/danielbakas/Documents/Profesional/Semantyk/Interno/Proyectos/Plataforma/Data/Knowledge/data/mex/fed/ef"
    "/gob/ap/cen/main.ttl",
]
base_uri = "http://datos.gob.mx/"


# Función para generar fragmentos personalizados
def generate_custom_fragment():
    identifier = uuid.uuid4().hex
    identifier = random.choice(string.ascii_letters[:6]) + identifier[1:8] + '_' + identifier[8:12] + '_' + \
                 identifier[12:16] + '_' + identifier[16:20] + '_' + identifier[20:]
    return identifier


# Crear un grafo global para combinar datos
global_graph = Graph()

# Cargar los archivos en el grafo global
for path in files:
    print(f"Cargando datos desde {path}")
    global_graph.parse(path, format="ttl")

# Espacios de nombres
datos = Namespace(base_uri)
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dcterms = Namespace("http://purl.org/dc/terms/")

# Consulta SPARQL
query = """
BASE <http://datos.gob.mx/>
PREFIX : <http://datos.gob.mx/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?APC ?prefLabel
WHERE {
  ?EF rdf:type <fd98d032_2fdd_4491_a235_a445ec0a7bf6> .
  ?GOB <e3a20fec_2cb0_44a7_8183_9d5b4d5a0886> ?EF .
  ?GOB rdf:type <cfd6b6b3_92a7_4a12_9080_92ff26f6c85c> .
  ?PE <e3a20fec_2cb0_44a7_8183_9d5b4d5a0886> ?GOB .
  ?PE rdf:type <c12531d0_53c0_40ab_8bf0_10f019459b24> .
  ?AP <e3a20fec_2cb0_44a7_8183_9d5b4d5a0886> ?PE .
  ?AP rdf:type <e3e803ac_950f_4d74_a6ca_9931e68b0157> .
  ?APC <e3a20fec_2cb0_44a7_8183_9d5b4d5a0886> ?AP .
  ?APC rdfs:label ?label .
  ?APC skos:prefLabel ?prefLabel .
  FILTER(CONTAINS(?label, "Centralizada de la Entidad"))
  FILTER(LANG(?label)="es")
}
ORDER BY ?prefLabel
"""

# Ejecutar la consulta en el grafo global
results = global_graph.query(query)

# Crear un nuevo grafo para las inserciones
insert_graph = Graph()

# Añadir el prefijo por defecto ":"
insert_graph.bind("", datos)

# Lista de labels
labels = [
    "Reto Verde",
    "Ponte Pilas con tu Ciudad",
    "Basura Cero",
    "Sello Verde",
    "Saneamiento del Arbolado",
    "Residuos Sólidos",
    "Registros Ambientales",
    "Hoy No Circula",
    "Infraestructura Verde",
    "Inventario de Áreas Verdes",
    "Altépetl Bienestar",
    "Verificación Vehicular",
    "Cambio Climático",
    "Cosecha de Lluvia",
    "Reciclatrón",
    "Mercado de Trueque",
    "Vehículos Contaminantes"
]

# Procesar los resultados de la consulta e insertar triples
for label in labels:
    # Generar un nuevo fragmento único para cada sujeto
    fragment = generate_custom_fragment()
    fragment_uri = datos[fragment]

    # Insertar triples
    # RDF.type
    insert_graph.add((fragment_uri, RDF.type, datos.b0984e57_8b64_484b_81c2_b143dd70181a))

    # Añadir los labels de la lista
    insert_graph.add((fragment_uri, RDFS.label, Literal(label, lang="es")))
    insert_graph.add((fragment_uri, RDFS.label, Literal(label, lang="en")))

    # tiene relación con
    insert_graph.add(
        (fragment_uri, datos.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886, datos.f2d7e39b_7aec_4215_bbef_fa82608c37e9))
    # DCTERMS.isPartOf
    insert_graph.add((fragment_uri, DCTERMS.isPartOf, datos.b3fe7fe8_3c6f_4c24_b350_225d75f6ea51))
    # RDFS.isDefinedBy
    insert_graph.add((fragment_uri, RDFS.isDefinedBy, datos["fed/ef/gob/ap/cen/sec/prog/"]))

# Guardar el grafo de inserciones en un archivo
output_file = "/Users/danielbakas/Desktop/result.ttl"
insert_graph.serialize(destination=output_file, format="turtle")

print(f"Archivo generado: {output_file}")
