import os

from rdflib import Dataset

# Load the TriG file
input_file = '../../releases/input.trig'
graph = Dataset()
graph.parse(input_file, format='trig')

# Serialize the graph into clean.trig
version = "0.0.0"
output_file = f'../../releases/latest.trig'
with open(output_file, 'w') as f:
    f.write(graph.serialize(format='trig'))

# Base directory for output files
base_dir = '../../data/mex/'

# Iterate over each named graph and save it to a separate file
for context in graph.contexts():
    graph_name = str(context.identifier)
    relative_path = graph_name.replace('http://datos.gob.mx/', '')
    output_dir = os.path.join(base_dir, relative_path)

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'main.ttl')

    with open(output_file, 'w') as f:
        f.write(context.serialize(format='turtle'))

print("Done")
