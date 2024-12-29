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
    def __init__(self, graph, new_class_uri):
        self.graph = graph
        self.new_class_uri = new_class_uri

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

    def generate_instance(self, ef_uri, entity_name):
        fragment = self._generate_uuid()
        new_uri = URIRef(MEX[fragment])

        self.graph.add((
            new_uri,
            RDF.type,
            MEX[self.new_class_uri]
        ))
        self.graph.add((
            new_uri,
            SKOS.prefLabel,
            Literal(entity_name, lang="es")
        ))
        self.graph.add((
            new_uri,
            SKOS.prefLabel,
            Literal(entity_name, lang="en")
        ))
        self.graph.add((
            new_uri,
            DCTERMS.isPartOf,
            MEX.c75a5270_c160_4f1a_963d_7ec9b3cce455
        ))
        self.graph.add((
            new_uri,
            MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
            ef_uri
        ))
        self.graph.add((
            new_uri,
            RDFS.label,
            Literal(
                f"La Administración Pública Paraestatal de la Entidad Federal de {entity_name}", lang="es")
        ))
        self.graph.add((
            new_uri,
            RDFS.label,
            Literal(
                f"The {entity_name} Federal Entity Parastatal Public Administration", lang="en")
        ))
        self.graph.add((
            new_uri,
            RDFS.isDefinedBy,
            MEX["fed/ef/ap/par/"]
        ))

# Pipeline to generate RDF for all federal entities


def generate_all_entities(cef_path, ef_class_uri, new_class_uri):
    graph = Graph()
    entity_generator = EntityCodeGenerator(graph, new_class_uri)

    # Load the federal entities data
    cef_graph = Graph()
    cef_graph.parse(cef_path, format="turtle")

    # Get all federal entities
    for entity in cef_graph.subjects(RDF.type, MEX[ef_class_uri]):
        labels = cef_graph.objects(entity, SKOS.prefLabel)
        entity_name = None
        for label in labels:
            if label.language == "es":
                entity_name = str(label)
                break

        if entity_name:
            # Generate RDF for the federal entity
            entity_generator.generate_instance(
                ef_uri=entity, entity_name=entity_name)
            print(f"Generated new instance for Federal Entity {entity_name}")

    return graph


# Execute the process to generate RDF for all federal entities
all_entities_graph = generate_all_entities(
    cef_path="data/MEX/FED/EF/main.ttl",
    ef_class_uri="fd98d032_2fdd_4491_a235_a445ec0a7bf6",
    new_class_uri="e3e803ac_950f_4d74_a6ca_9931e68b0157"
)

# Save the RDF
output_all_entities_file_path = "/Users/danielbakas/Desktop/result.ttl"
with open(output_all_entities_file_path, "w", encoding="utf-8") as rdf_file:
    rdf_file.write(all_entities_graph.serialize(format="turtle"))

output_all_entities_file_path
