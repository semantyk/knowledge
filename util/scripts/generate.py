from rdflib import Graph, URIRef, Literal, Namespace, RDF, OWL, RDFS, SKOS, DCTERMS
import os
import uuid
import random
import string

# Define custom namespace
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

# GovernmentGenerator Class


class GovernmentGenerator:
    def __init__(self, rdf_processor, class_uri, graph):
        self.rdf_processor = rdf_processor
        self.class_uri = class_uri
        self.graph = graph

        # Bind namespaces for clean prefixes
        self.graph.bind("rdf", RDF)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("skos", SKOS)
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("", MEX)

    def generate_instance(self, fragment, name):
        """Generate a generic RDF instance for a given fragment and name."""
        new_fragment = self._generate_uuid()
        subject = URIRef(f"http://datos.gob.mx/{new_fragment}")

        self.graph.add((subject, RDF.type, URIRef(self.class_uri)))
        self.graph.add((subject, SKOS.prefLabel, Literal(name, lang="es")))
        self.graph.add((subject, SKOS.prefLabel, Literal(name, lang="en")))
        self.graph.add((
            subject,
            RDFS.label,
            Literal(f"El Gobierno del Municipio de {name}", lang="es")
        ))
        self.graph.add((
            subject,
            RDFS.label,
            Literal(f"The {name} Municipality Government", lang="en")
        ))
        self.graph.add((
            subject,
            MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
            URIRef(fragment)
        ))
        self.graph.add((
            subject,
            MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
            MEX.c3003dc5_e891_4d38_a5b7_f6041566ce4e
        ))
        self.graph.add((
            subject,
            DCTERMS.isPartOf,
            MEX.f33467fd_e94a_451a_86d2_890c518da6d6
        ))
        self.graph.add((
            subject,
            RDFS.isDefinedBy,
            URIRef("http://datos.gob.mx/fed/gef/")
        ))

    def _generate_uuid(self):
        identifier = uuid.uuid4().hex
        return f"{random.choice(string.ascii_letters[0:6])}{identifier[1:8]}_{identifier[8:12]}_{identifier[12:16]}_{identifier[16:20]}_{identifier[20:]}"

# Main Functionality


def extract_municipalities_by_ef(omun_processor, ef_fragment):
    """Extract municipalities belonging to a specific EF fragment."""
    municipalities = []
    for s in omun_processor.get_subjects_by_type("http://datos.gob.mx/bfcd1a25_1e78_4168_8e4d_f19885dbce23"):
        relation = omun_processor.graph.value(subject=URIRef(
            s), predicate=MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886)
        if relation and str(relation).split('/')[-1] == ef_fragment:
            municipalities.append(
                {"Fragment": s, "PrefLabel": omun_processor.get_pref_label(s)})
    return municipalities


def generate_all_instances(oef_path, omun_path, output_path, class_uri):
    oef_processor = RDFProcessor(oef_path)
    omun_processor = RDFProcessor(omun_path)
    graph = Graph()
    generator = GovernmentGenerator(oef_processor, class_uri, graph)

    efs = oef_processor.get_subjects_by_type(
        "http://datos.gob.mx/fd98d032_2fdd_4491_a235_a445ec0a7bf6")

    for ef in efs:
        ef_fragment = ef.split("/")[-1]
        municipalities = extract_municipalities_by_ef(
            omun_processor, ef_fragment)

        for municipality in municipalities:
            generator.generate_instance(
                fragment=municipality["Fragment"],
                name=municipality["PrefLabel"]
            )

    with open(output_path, "w") as rdf_file:
        rdf_file.write(graph.serialize(format="turtle"))


# Example Usage
oef_path = "data/MEX/FED/OEF/main.ttl"
omun_path = "data/MEX/FED/OMUN/main.ttl"
output_path = "/Users/danielbakas/Desktop/result.ttl"
class_uri = "http://datos.gob.mx/cfd6b6b3_92a7_4a12_9080_92ff26f6c85c"
generate_all_instances(oef_path, omun_path, output_path, class_uri)
print(f"Generated all instances: {output_path}")
