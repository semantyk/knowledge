# Importar la librería para manejar RDF
from rdflib import DCTERMS, Graph, URIRef, Namespace, Literal, RDFS, RDF, SKOS, OWL
import random
import string
import uuid

# Definir Namespaces
MEX = Namespace("http://datos.gob.mx/")

# Fragmentos de clases y relaciones
EF_FRAGMENT = "fd98d032_2fdd_4491_a235_a445ec0a7bf6"  # Clase EF
MUN_FRAGMENT = "bfcd1a25_1e78_4168_8e4d_f19885dbce23"  # Clase MUN
LOC_FRAGMENT = "b07b78f9_bfc9_4ea1_a6ba_d75e9eec3611"  # Clase LOC
CODIGO_FRAGMENT = "c8d8cdf0_8173_4233_9c11_a21c40337503"  # Clase Código
# Relación "tiene relación con"
RELACION_FRAGMENT = "e3a20fec_2cb0_44a7_8183_9d5b4d5a0886"
# Relación "tiene código"
TIENE_CODIGO_FRAGMENT = "dca9db1b_2f0f_49b7_bb54_223ec90c07cf"

# Función para generar fragmentos como en regex.py


def generar_fragmento():
    base = uuid.uuid4().hex
    fragmento = random.choice(string.ascii_letters[:6]) + base[1:8] + '_' + \
        base[8:12] + '_' + base[12:16] + '_' + base[16:20] + '_' + base[20:]
    return fragmento


# 1. Cargar los archivos RDF en un solo grafo
g = Graph()
# Archivo con Municipios
print("Cargando Municipios...")
g.parse("data/MEX/FED/OMUN/main.ttl", format="turtle")
print("Carga Exitosa!")
# Archivo con Códigos de Municipio
print("Cargando Códigos de Municipios...")
g.parse("data/MEX/FED/OMUN/CMUN/main.ttl", format="turtle")
print("Carga Exitosa!")
# Archivo con Códigos de Localidad
print("Cargando Códigos de Localidades...")
g.parse("data/MEX/FED/OLOC/CLOC/main.ttl", format="turtle")
print("Carga Exitosa!")

# 2. Crear un nuevo grafo para las Localidades
g_loc = Graph()
g_loc.bind("", MEX)
g_loc.bind("rdf", RDF)
g_loc.bind("rdfs", RDFS)
g_loc.bind("skos", SKOS)
g_loc.bind("owl", OWL)

# 3. Iterar sobre cada Código de Localidad (CLOC) usando SPARQL
query = """
PREFIX mex: <http://datos.gob.mx/>
SELECT ?cloc ?cmun ?mun
WHERE {
    ?cloc a mex:c8d8cdf0_8173_4233_9c11_a21c40337503 .
    ?cloc mex:e3a20fec_2cb0_44a7_8183_9d5b4d5a0886 ?cmun .
    ?mun mex:dca9db1b_2f0f_49b7_bb54_223ec90c07cf ?cmun .
}
"""

# 3.1 Inicializar un contador para las Localidades
count = 0

# 3.2 Ejecutar la consulta SPARQL y contar las Localidades
rows = g.query(query)
count = len(rows)
print(f"Total Esperada de Localidades: {count}")

count = 0

for row in rows:
    cloc_uri = row.cloc
    cmun_uri = row.cmun
    mun_uri = row.mun

    # 3.3 Generar un nuevo URI para la Localidad usando la función de fragmento
    fragmento = generar_fragmento()
    loc_uri = MEX[fragmento]

    # 3.4 Añadir la instancia de Localidad al nuevo grafo
    g_loc.add((loc_uri, RDF.type, MEX[LOC_FRAGMENT]))  # Tipo de instancia
    g_loc.add((loc_uri, RDF.type, OWL.NamedIndividual))  # OWL:NamedIndividual
    # Relación con Municipio
    g_loc.add((loc_uri, MEX[RELACION_FRAGMENT], mun_uri))
    # Relación con CLOC
    g_loc.add((loc_uri, MEX[TIENE_CODIGO_FRAGMENT], cloc_uri))
    # isDefinedBy
    g_loc.add((loc_uri, RDFS.isDefinedBy, MEX["fed/oloc/"]))
    g_loc.add((loc_uri, DCTERMS.isPartOf, MEX["fed/oloc#"]))

    # 3.5 Añadir prefLabels y etiquetas en dos idiomas
    # Obtener el nombre del CLOC
    name = g.value(subject=cloc_uri, predicate=SKOS.prefLabel)
    if name:
        g_loc.add((loc_uri, SKOS.prefLabel, Literal(name, lang="es")))
        g_loc.add((loc_uri, SKOS.prefLabel, Literal(name, lang="en")))
        g_loc.add((loc_uri, RDFS.label, Literal(f"La Localidad de {name}", lang="es")))
        g_loc.add((loc_uri, RDFS.label, Literal(f"The {name} Locality", lang="en")))
    count +=1

print(f"Total Real de Localidades: {count}")

# 4. Guardar el nuevo grafo con las instancias de Localidades
g_loc.serialize("localidades.ttl", format="turtle")
