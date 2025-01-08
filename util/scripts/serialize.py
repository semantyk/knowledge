import os

from rdflib import Dataset, Graph

# Base directory for input files
base_dir = '../../data/mex/'

# Base URI
base_uri = 'http://datos.gob.mx/'

# Paths to skip
skip_paths = [
    '../../data/mex/fed/loc/main.ttl',
    '../../data/mex/fed/loc/cod/main.ttl',
]

# Create a new dataset
dataset = Dataset()

# Traverse the directory structure to find all main.ttl files
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == 'main.ttl':
            file_path = os.path.join(root, file)
            if file_path in skip_paths:
                continue
            relative_path = os.path.relpath(file_path, base_dir)
            graph_name = base_uri + os.path.dirname(relative_path).replace(os.sep, '/')
            if not graph_name.endswith('/'):
                graph_name += '/'
            # Create a new named graph
            graph = Graph(identifier=graph_name)

            # Parse the main.ttl file into the named graph
            graph.parse(file_path, format='turtle')

            # Add the named graph to the dataset
            dataset.add_graph(graph)

# Serialize the dataset into a TriG file
output_file = '../../releases/latest.trig'
with open(output_file, 'w') as f:
    f.write(dataset.serialize(format='trig'))

print(f"Dataset serialized to {output_file}")
