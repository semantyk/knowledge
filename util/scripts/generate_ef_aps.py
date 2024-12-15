# Reload the complete code from the canvas to ensure the environment has the required functions

from rdflib import Graph, URIRef, Literal, Namespace, RDF, OWL, RDFS, SKOS, DCTERMS, XSD
import pandas as pd
import uuid
import random
import string

# Define custom namespaces
MEX = Namespace("http://datos.gob.mx/")

# RDFProcessor Class


class RDFProcessor:
    def __init__(self, file_path):
        self.graph = Graph()
        self.graph.parse(file_path, format="turtle")

    def get_subjects_by_type(self, rdf_type):
        """Retrieve all subjects of a given RDF type."""
        return [
            str(s) for s in self.graph.subjects(
                predicate=RDF.type, object=URIRef(rdf_type)
            )
        ]

    def get_pref_label(self, subject):
        """Retrieve the preferred label of a subject."""
        label = self.graph.value(subject=URIRef(
            subject), predicate=SKOS.prefLabel)
        return str(label) if label else "Unknown"

    def get_related_object(self, subject, predicate):
        """Retrieve the object of a subject-predicate pair."""
        obj = self.graph.value(subject=URIRef(
            subject), predicate=URIRef(predicate))
        return str(obj) if obj else None

# EntityCodeGenerator Class


class EntityCodeGenerator:
    def __init__(self, graph, entity_class_uri):
        self.graph = graph
        self.entity_class_uri = entity_class_uri

        # Bind namespaces for clean prefixes
        self.graph.namespace_manager.bind("rdf", RDF)
        self.graph.namespace_manager.bind("owl", OWL)
        self.graph.namespace_manager.bind("rdfs", RDFS)
        self.graph.namespace_manager.bind("skos", SKOS)
        self.graph.namespace_manager.bind("dcterms", DCTERMS)
        self.graph.namespace_manager.bind("", MEX)

    def _generate_uuid(self):
        identifier = uuid.uuid4().hex
        return f"{random.choice(string.ascii_letters[0:6])}{identifier[1:8]}_{identifier[8:12]}_{identifier[12:16]}_{identifier[16:20]}_{identifier[20:]}"

    def generate_instance(self, entity_name, entity_code):
        """Generate a federal entity RDF instance."""
        new_fragment = self._generate_uuid()
        uri = URIRef(MEX[new_fragment])

        self.graph.add((
            uri,
            RDF.type,
            MEX[self.entity_class_uri]
        ))
        self.graph.add((
            uri,
            SKOS.prefLabel,
            Literal(entity_name, lang="es")
        ))
        self.graph.add((
            uri,
            SKOS.prefLabel,
            Literal(entity_name, lang="en")
        ))
        self.graph.add((
            uri,
            DCTERMS.isPartOf,
            URIRef(MEX["cat/cloc#"])
        ))
        self.graph.add((
            uri,
            RDFS.label,
            Literal(f"El Código de la Entidad Federal de {entity_name}", lang="es")
        ))
        self.graph.add((
            uri,
            RDFS.label,
            Literal(f"The {entity_name} Federal Entity Code", lang="en")
        ))
        self.graph.add((
            uri,
            RDF.value,
            Literal(entity_code, datatype=XSD.integer)
        ))
        self.graph.add((
            uri,
            RDFS.isDefinedBy,
            URIRef(MEX["fed/cloc/"])
        ))

# Pipeline to generate RDF for all federal entities


def generate_all_entities(cef_path, entity_class_uri, entities_csv):
    graph = Graph()
    entity_generator = EntityCodeGenerator(graph, entity_class_uri)

    # Load the entities data
    entities_df = pd.read_csv(entities_csv, encoding='latin1')

    # Get unique entity codes and names
    unique_entities = entities_df[['CVE_ENT', 'NOM_ENT']].drop_duplicates()

    for _, entity in unique_entities.iterrows():
        entity_code = entity['CVE_ENT']
        entity_name = entity['NOM_ENT']

        # Generate RDF for the federal entity
        entity_generator.generate_instance(
            entity_name=entity_name,
            entity_code=int(entity_code)
        )

        print(f"Generated code for Federal Entity {entity_name} with code {entity_code}")

    return graph


# Execute the process to generate RDF for all federal entities
all_entities_graph = generate_all_entities(
    cef_path="data/MEX/FED/OEF/CEF/main.ttl",
    entity_class_uri="c8d8cdf0_8173_4233_9c11_a21c40337503",
    entities_csv="/Users/danielbakas/Desktop/Catálogo áreas geoestadísticas/CATUN/AGEEML_202411211456316.csv"
)

# Save the RDF
output_all_entities_file_path = "/Users/danielbakas/Desktop/result.ttl"
with open(output_all_entities_file_path, "w", encoding="utf-8") as rdf_file:
    rdf_file.write(all_entities_graph.serialize(format="turtle"))

output_all_entities_file_path
