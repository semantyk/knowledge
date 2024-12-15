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
    def __init__(self, graph, power_class_uri):
        self.graph = graph
        self.power_class_uri = power_class_uri

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

    def generate_instance(self, entity_uri, entity_name):
        """Generate 3 instances of Power for each federal entity."""
        power_types_es = ["Ejecutivo", "Legislativo", "Judicial"]
        power_types_en = ["Executive", "Legislative", "Judicial"]
        for i in range(3):
            power_fragment = self._generate_uuid()
            power_uri = URIRef(MEX[power_fragment])

            self.graph.add((
                power_uri,
                RDF.type,
                MEX[self.power_class_uri]
            ))
            self.graph.add((
                power_uri,
                SKOS.prefLabel,
                Literal(entity_name, lang="es")
            ))
            self.graph.add((
                power_uri,
                SKOS.prefLabel,
                Literal(entity_name, lang="en")
            ))
            self.graph.add((
                power_uri,
                DCTERMS.isPartOf,
                MEX.cfe126af_96e5_43d7_8cbc_b52e6d3e1e3d
            ))
            self.graph.add((
                power_uri,
                MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
                MEX.c3003dc5_e891_4d38_a5b7_f6041566ce4e
            ))
            self.graph.add((
                power_uri,
                MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
                entity_uri
            ))
            self.graph.add((
                power_uri,
                RDFS.label,
                Literal(
                    f"El Poder {power_types_es[i]} de la Entidad Federal de {entity_name}", lang="es")
            ))
            self.graph.add((
                power_uri,
                RDFS.label,
                Literal(f"The {entity_name} Federal Entity {
                        power_types_en[i]} Power", lang="en")
            ))
            self.graph.add((
                power_uri,
                RDFS.isDefinedBy,
                MEX["fed/ef/pow/"]
            ))

# Pipeline to generate RDF for all federal entities


def generate_all_entities(cef_path, entity_class_uri, power_class_uri):
    graph = Graph()
    entity_generator = EntityCodeGenerator(graph, power_class_uri)

    # Load the federal entities data
    cef_graph = Graph()
    cef_graph.parse(cef_path, format="turtle")

    # Get all federal entities
    for entity in cef_graph.subjects(RDF.type, MEX[entity_class_uri]):
        labels = cef_graph.objects(entity, SKOS.prefLabel)
        entity_name = None
        for label in labels:
            if label.language == "es":
                entity_name = str(label)
                break

        if entity_name:
            # Generate RDF for the federal entity
            entity_generator.generate_instance(
                entity_uri=entity, entity_name=entity_name)
            print(f"Generated code for Federal Entity {entity_name}")

    return graph


# Execute the process to generate RDF for all federal entities
all_entities_graph = generate_all_entities(
    cef_path="data/MEX/FED/EF/main.ttl",
    entity_class_uri="fd98d032_2fdd_4491_a235_a445ec0a7bf6",
    power_class_uri="c12531d0_53c0_40ab_8bf0_10f019459b24"
)

# Save the RDF
output_all_entities_file_path = "/Users/danielbakas/Desktop/result.ttl"
with open(output_all_entities_file_path, "w", encoding="utf-8") as rdf_file:
    rdf_file.write(all_entities_graph.serialize(format="turtle"))

output_all_entities_file_path
