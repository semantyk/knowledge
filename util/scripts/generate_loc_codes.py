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

# LocalityCodeGenerator Class


class LocalityCodeGenerator:
    def __init__(self, graph, locality_class_uri):
        self.graph = graph
        self.locality_class_uri = locality_class_uri

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

    def generate_instance(self, locality_name, locality_code, municipality_uri):
        """Generate a locality RDF instance."""
        new_fragment = self._generate_uuid()
        locality_uri = URIRef(MEX[new_fragment])

        self.graph.add((
            locality_uri,
            RDF.type,
            MEX[self.locality_class_uri]
        ))
        self.graph.add((
            locality_uri,
            SKOS.prefLabel,
            Literal(locality_name, lang="es")
        ))
        self.graph.add((
            locality_uri,
            SKOS.prefLabel,
            Literal(locality_name, lang="en")
        ))
        self.graph.add((
            locality_uri,
            DCTERMS.isPartOf,
            URIRef(MEX["cat/cloc#"])
        ))
        self.graph.add((
            locality_uri,
            RDFS.label,
            Literal(f"El Código de la Localidad de {locality_name}", lang="es")
        ))
        self.graph.add((
            locality_uri,
            RDFS.label,
            Literal(f"The {locality_name} Locality Code", lang="en")
        ))
        self.graph.add((
            locality_uri,
            RDF.value,
            Literal(locality_code, datatype=XSD.integer)
        ))
        self.graph.add((
            locality_uri,
            MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886,
            municipality_uri
        ))
        self.graph.add((
            locality_uri,
            RDFS.isDefinedBy,
            URIRef(MEX["fed/cloc/"])
        ))

# Function to retrieve the Municipality URI


def get_municipality_uri(cef_path, cmun_path, ef_code, mun_code):
    """
    Given a Code of EF and Municipality, retrieve the URI of the Municipality Code,
    ensuring the Municipality is linked to the EF and both have the provided values.
    """
    # Load graphs
    cef_graph = Graph()
    cef_graph.parse(cef_path, format="turtle")

    cmun_graph = Graph()
    cmun_graph.parse(cmun_path, format="turtle")

    # Find the URI for the EF Code
    ef_uri = None
    ef_class_uri = MEX.c8d8cdf0_8173_4233_9c11_a21c40337503

    for subject in cef_graph.subjects(RDF.type, ef_class_uri):
        ef_value = cef_graph.value(subject, RDF.value)
        if ef_value and int(ef_value) == ef_code:
            ef_uri = subject
            break

    if not ef_uri:
        return None

    # Find the URI for the Municipality Code and ensure it is linked to the EF
    mun_uri = None
    for subject in cmun_graph.subjects(RDF.type, ef_class_uri):
        mun_value = cmun_graph.value(subject, RDF.value)
        linked_ef_uri = cmun_graph.value(
            subject, MEX.e3a20fec_2cb0_44a7_8183_9d5b4d5a0886
        )

        if mun_value and int(mun_value) == mun_code and linked_ef_uri == ef_uri:
            mun_uri = subject
            break

    return mun_uri

# Pipeline to generate RDF for all localities in all EFs


def generate_all_localities(cef_path, cmun_path, locality_class_uri, localities_csv):
    graph = Graph()
    locality_generator = LocalityCodeGenerator(graph, locality_class_uri)

    # Load the localities data
    localities_df = pd.read_csv(localities_csv, encoding='latin1')

    # Get unique EF codes
    unique_efs = localities_df['CVE_ENT'].unique()

    for ef_code in unique_efs:
        # Get unique municipalities for the EF
        municipalities = localities_df[localities_df['CVE_ENT']
                                       == ef_code]['CVE_MUN'].unique()

        ef_locality_count = 0

        for mun_code in municipalities:
            # Retrieve the Municipality URI
            municipality_uri = get_municipality_uri(
                cef_path, cmun_path, ef_code, mun_code)

            if not municipality_uri:
                print(f"No URI found for Municipality Code {
                      mun_code} in EF {ef_code}")
                continue

            # Filter localities for the current Municipality
            filtered_localities = localities_df[
                (localities_df['CVE_ENT'] == ef_code) &
                (localities_df['CVE_MUN'] == mun_code)
            ]

            mun_locality_count = 0

            # Generate RDF for each locality
            for _, locality in filtered_localities.iterrows():
                locality_name = locality['NOM_LOC']
                locality_code = int(locality['CVE_LOC'])

                locality_generator.generate_instance(
                    locality_name=locality_name,
                    locality_code=locality_code,
                    municipality_uri=municipality_uri
                )
                mun_locality_count += 1

            ef_locality_count += mun_locality_count

            print(f"Generated {mun_locality_count} localities for Municipality {
                  mun_code} in EF {ef_code}")

        print(f"Generated {ef_locality_count} localities for EF {ef_code}")

    return graph


# Execute the process to generate RDF for all localities across all EFs
all_localities_graph = generate_all_localities(
    cef_path="data/MEX/FED/OEF/CEF/main.ttl",
    cmun_path="data/MEX/FED/OMUN/CMUN/main.ttl",
    locality_class_uri="c8d8cdf0_8173_4233_9c11_a21c40337503",
    localities_csv="/Users/danielbakas/Desktop/Catálogo áreas geoestadísticas/CATUN/AGEEML_202411211456316.csv"
)

# Save the RDF
output_all_localities_file_path = "/Users/danielbakas/Desktop/localities.ttl"
with open(output_all_localities_file_path, "w", encoding="utf-8") as rdf_file:
    rdf_file.write(all_localities_graph.serialize(format="turtle"))

output_all_localities_file_path
