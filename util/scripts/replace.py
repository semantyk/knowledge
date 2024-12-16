import rdflib

def replace_uri(input_file, old_uri, new_uri):
    g = rdflib.Graph()
    g.parse(input_file, format='ttl')

    for s, p, o in g:
        if isinstance(s, rdflib.URIRef) and old_uri in s:
            g.remove((s, p, o))
            s = rdflib.URIRef(str(s).replace(old_uri, new_uri))
            g.add((s, p, o))
        if isinstance(o, rdflib.URIRef) and old_uri in o:
            g.remove((s, p, o))
            o = rdflib.URIRef(str(o).replace(old_uri, new_uri))
            g.add((s, p, o))

    g.serialize(destination=input_file, format='ttl')

if __name__ == "__main__":
    input_file = 'data/MEX/FED/LOC/CODE/main.ttl'
    old_uri = 'http://datos.gob.mx/fed/loc/code/'
    new_uri = 'http://datos.gob.mx/fed/loc/cod/'
    replace_uri(input_file, old_uri, new_uri)