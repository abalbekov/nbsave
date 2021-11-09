
import nbformat

# AddFilters is my custom exporter inherited from HTMLExporter
from custom_exporter import AddFilters
    
def save_as_evidence(nb_file, out_file):

    custom_exporter = AddFilters(template_name='custom_template')

    # read notebook from disk
    this_notebook = nbformat.read(nb_file, as_version=4)
    
    # convert notebook using the exporter
    body, _ = custom_exporter.from_notebook_node(this_notebook)

    # save converted output
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(body)
    
    

