# based on example at https://buildmedia.readthedocs.org/media/pdf/nbconvert/latest/nbconvert.pdf
from nbconvert.exporters.html import HTMLExporter   
from datetime import datetime, timezone
import re
import base64

class AddFilters(HTMLExporter):
    """
    Custom exporter to register user functions as jinja2 filters.
    Filters is a way to let jinja2 templates interact with user functions.
    Filters in this exporter are expected to be called from "custom_template" template.
    To make this class available to custom template - place the directory under PYTHONPATH.
    """
    @classmethod
    def _diffTime(cls, end, start):
        """
        converts datetime interval into human friendly format
        """
        diff = (end - start).total_seconds()
        d = int(diff / 86400)
        h = int((diff - (d * 86400)) / 3600)
        m = int((diff - (d * 86400 + h * 3600)) / 60)
        s = int((diff - (d * 86400 + h * 3600 + m *60)))
        ms= round((diff - (d * 86400 + h * 3600 + m *60 + s))*1000)
        if d > 0:
            fdiff = f'{d}d {h}h {m}m {s}s'
        elif h > 0:
            fdiff = f'{h}h {m}m {s}s'
        elif m > 0:
            fdiff = f'{m}m {s}s'
        elif s > 0:
            fdiff = f'{s}.{ms}s'
        else:
            fdiff = f'{ms}ms'
        return fdiff

    @classmethod
    def store_start_time(cls, s):
        """
        """
        cls.start_time_str=s
        return ""

    @classmethod
    def store_end_time(cls, s):
        cls.end_time_str=s
        return ""

    @classmethod        
    def show_finished_at(cls, s):
        if s:
            dt=datetime.fromisoformat(s.replace('Z', '+00:00'))
            
            # convert to local TZ
            dt=dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
            
            # clear end time for next cell iteration
            cls.end_time_str=""
            
            return datetime.strftime(dt, '%H:%M:%S %Y-%m-%d')
        else:
            return ""

    @classmethod
    def show_executed_in(cls, s):
        if cls.start_time_str:
            dt_start=datetime.fromisoformat(cls.start_time_str.replace('Z', '+00:00'))
            
            # convert to local TZ
            dt_start=dt_start.replace(tzinfo=timezone.utc).astimezone(tz=None)
            
            # clear start time for next cell iteration
            cls.start_time_str=""
            
            if cls.end_time_str:
                dt_end=datetime.fromisoformat(cls.end_time_str.replace('Z', '+00:00'))
                return cls._diffTime(dt_end, dt_start)
            else:
                return ""
        return ""
    
    header_count_dict={}
    @classmethod
    def clear_header_count_dict(cls):
        """ this may be called from preprocessor """
        cls.header_count_dict=dict( (i+1, 0) for i in range(5) )
    
    # regex to search for ## (or more) in the beginning of a string
    pound_regex=re.compile("\s*(##+)(.*)")
    
    # Below is class attribute regex to edit TOC2 extension-generated Table Of Content HTML to fix HREF.
    # It is declared as class attribute to recompile it once.
    # The regex goal is to prepend HREF in Anchor with numbers taken from "data-toc-modified-id" suffix.
    # Ex., if the anchor element looks like : <a href="#three-hash" data-toc-modified-id="three-hash-1.1">
    #                    then it will become: <a href="#1.1-three-hash" data-toc-modified-id="three-hash-1.1">
    anchor_regex=re.compile(r'(<a href="#)(.+?" data-toc-modified-id=".+?-)([\.0-9]+?)(">)')
    
    @classmethod
    def fix_toc2_href(cls, s):
        """
        accepts an html text, searches for html anchor and edits href
        """
        s_ret=re.sub(cls.anchor_regex, r'\1\3-\2\3\4', s)
        return s_ret
    
    
    #
    # Example : <img src="19c_migration_diagram.png" alt="Drawing">
    #           will change to :
    #           <img src="data:image/png;base64,....base64-encoded-string..." alt="Drawing">
    #
    html_img_regex=re.compile( r'(<img src=")(.+?)(".*?>)' )
    
    @staticmethod
    def inline_img(m):
        """
        helper function to read img file and convert to base64 string
        Parameter: m: regex match object
        """
        fname = m.group(2)
        try:
            with open(fname, 'rb') as f:
                data = f.read()
        except IOError as error:
            data=b''
            
        b64_data = base64.b64encode(data).decode("utf-8")
        return f'{m.group(1)}data:image/png;base64,{b64_data}{m.group(3)}'
    
    @classmethod
    def markdown_embed_img(cls, s):
        """
        accepts a markdow text and embeds referenced images as base64 strings
        """
        s_ret=re.sub(cls.html_img_regex, cls.inline_img, s)
        return s_ret
    
    
    @classmethod
    def number_headers(cls, s):
        """
        this accepts a multiline markdown text
        searches for a header
        prepends a number to header
        increments the number and saves for next cell iteration
        """
        s_ret=""
        for line in s.splitlines():
            # if 1st non-blank letters are pounds, then increment numbering dict
            # and construct numbering prefix
            prefix=""
            m=cls.pound_regex.match(line)
            if m:
                pound_count=len(m.groups()[0])
                
                # increment count and save
                cls.header_count_dict[pound_count] += 1
                
                # nullify childs counts
                for n in cls.header_count_dict.keys():
                    if n > pound_count:
                        cls.header_count_dict[n]=0
                
                # construct prefix
                number_list=[str(cls.header_count_dict[n]) for n in cls.header_count_dict.keys() if n > 1 and n<= pound_count]
                prefix='.'.join(number_list)
                
                s_ret += m.groups()[0]+prefix+m.groups()[1]+'\n'
                
            else:
                s_ret += line+'\n'
                
        return s_ret
    
    def __init__(self, *args, **kwargs):
        # first call parent
        super(self.__class__, self).__init__(*args, **kwargs)
        
        self.register_filter('show_finished_at'  , self.__class__.show_finished_at)
        self.register_filter('show_executed_in'  , self.__class__.show_executed_in)
        self.register_filter('store_start_time'  , self.__class__.store_start_time)
        self.register_filter('store_end_time'    , self.__class__.store_end_time  )
        self.register_filter('number_headers'    , self.__class__.number_headers  )
        self.register_filter('fix_toc2_href'     , self.__class__.fix_toc2_href   )
        self.register_filter('markdown_embed_img', self.__class__.markdown_embed_img)
        
        self.clear_header_count_dict()

        
        

        
        
        
