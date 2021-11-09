
import nbformat
from nbconvert.preprocessors import Preprocessor
from traitlets.config import Config
import re

# AddFilters is my custom exporter inherited from HTMLExporter
from custom_exporter import AddFilters
    
def save_as_instructions(nb_file, out_file):
  
    # define custom preprocessor class
    class CustomPreprocessor(Preprocessor):

        # class attribute regex to search for not escaped "{variable}" pattern
        #var_regex=re.compile("({.+?})")
        #var_regex=re.compile(r"(?<=[^\\]){[^\\]*?}")
    
        # get_ipython().user_ns[] gives variable value
        ip=get_ipython()

        def preprocess_cell(self, cell, resources, index):
            """
                A cell preprocessor to substitute any Notebook variables inside not escaped curly braces in code cells
                To inline images in markdown cells
                To enumerate headers in markdown cells
                To adjust HREF in toc2-generated table of content html to match enumerated markdown headers
                To remove all output
            """

            #print(f'called on cell {index}')
            
            # expand any Notebook variables inside not escaped curly braces
            if cell['cell_type']=='code':
                cell['source']=re.sub(r"(?<=[^\\]){[^\\]*?}",
                                      lambda x: self.ip.user_ns.get(x.group(0)[1:-1], '{'+ x.group(0)[1:-1]+ '}'),
                                      cell['source'],
                                      flags=re.MULTILINE)
                            
                # if curly braces were escaped with backslash then remove backslash
                cell['source']=re.sub(r"\\([{}])",
                                      r"\1",
                                      cell['source'],
                                      flags=re.MULTILINE)

                           
            # inline images references in markdown cells
            if cell['cell_type']=='markdown':
                cell['source']=AddFilters.markdown_embed_img(cell['source'])
            
            # enumerate headers in markdown cells
            if cell['cell_type']=='markdown':
                cell['source']=AddFilters.number_headers(cell['source'])
                       
            #fix HREF in TOC2 extension-generated Table Of Content HTML to align it with enumerated markdown headers 
            if cell['cell_type']=='markdown' and cell['metadata'].get('toc', False):
                cell['source']=AddFilters.fix_toc2_href(cell['source'])
            
            return cell, resources

    c =  Config()

    # add custom preprocessor to exporter
    c.AddFilters.preprocessors = [CustomPreprocessor]
    
    # add hide_cell removal preprocessor
    c.TagRemovePreprocessor.remove_cell_tags = ("hide_cell",)
    
    # add output removal preprocessor
    c.ClearOutputPreprocessor.enabled=True

    # create exporter
    custom_exporter = AddFilters(config=c)

    # read notebook from disk
    this_notebook = nbformat.read(nb_file, as_version=4)
    
    # convert notebook using the exporter
    body, _ = custom_exporter.from_notebook_node(this_notebook)

    # save converted output
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(body)
    
    

