import csv
import os
import re
import tempfile
from io import StringIO
from zipfile import ZipFile
from cap_sender.cap_index import CAPIndex


class ZipProcessor:
    """
    Base class for handling zip files.
    """
    zip_pattern = ''
    pdf_pattern = ''

    def __init__(self, filename):
        self.fn = filename

    @classmethod
    def match(cls, filename):
        """
        Class method which, when the given filename
        matches cls.zip_pattern, will return the class.
        """
        bn = os.path.basename(filename)
        if re.match(cls.zip_pattern, bn):
            return cls(filename)

    def transform(self):
        """
        Method which will be called to perform transformations
        on the files belonging to this class.
        """
        pass


class TransferProcessor(ZipProcessor):
    """
    Class for handling CommonApp transfer zip files, which all need
    an index file to be generated for DIP.
    """
    pdf_fieldnames=[]

    def transform(self):
        """
        Create an `index.txt` tsv listing each pdf file and attributes
        parsed from the filename.
        """
        with ZipFile(self.fn, 'r') as zf:
            namelist = zf.namelist()
        with StringIO(newline='') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=self.pdf_fieldnames,
                                    delimiter='\t')
            writer.writeheader()
            for fn in namelist:
                writer.writerow(re.match(self.pdf_pattern, fn).groupdict())
            with ZipFile(self.fn, 'a') as zf:
                zf.writestr('index.txt', f.getvalue())


class TransferAppProcessor(TransferProcessor):
    """
    TransferProcessor class for handling
    CommonApp Transfer Application zip files.
    """
    zip_pattern = r'\d+_\d+_\d+_TR_Applications\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_.+)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name']


class TransferEvalProcessor(TransferProcessor):
    """
    TransferProcessor class for handling
    CommonApp Transfer Evaluation zip files.
    """
    zip_pattern = r'\d+_\d+_\d+_TR_Evaluations\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_(?P<doc_id>\d+)_Evaluation_(?P<recommender>.+?)_.+)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name',
                      'doc_id', 'recommender']


class TransferTranscriptProcessor(TransferProcessor):
    """
    TransferProcessor class for handling
    CommonApp Transfer Transcript zip files.
    """
    zip_pattern = r'\d+_\d+_\d+_TR_College_Transcript\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_(?P<doc_id>\d+)_(?P<doc_type>Transcript)_(?P<college_code>\d+)_(?P<college_name>.+?)_(?P<submit_dt>.+?)\.pdf)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name',
                      'doc_id', 'college_name', 'submit_dt']


class FreshmanProcessor(ZipProcessor):
    """
    Class for handling CommonApp Freshman zip files, which all need
    to have the xml index file transformed into a tsv DIP index.
    """
    def transform(self):
        temp_dir = tempfile.TemporaryDirectory()
        with ZipFile(self.fn, 'a') as zf:
            zf.extractall(temp_dir.name)
        for f in os.listdir(temp_dir.name):
            if f.endswith('.xml'):
                infile = os.path.join(temp_dir.name, f)
                outfile = infile + '.txt'
                c = CAPIndex(infile)
                c.to_csv(outfile, delimiter='\t')
                os.remove(infile)
        with ZipFile(self.fn, 'w') as zf:
            for f in os.listdir(temp_dir.name):
                out_file = os.path.join(temp_dir.name, f)
                zf.write(out_file, f)


class FreshmanAppProcessor(FreshmanProcessor):
    """
    FreshmanProcessor class for handling
    CommonApp Freshman Application zip files.
    """
    zip_pattern = r'ugaappl_.+\.zip'


class FreshmanFormsProcessor(FreshmanProcessor):
    """
    FreshmanProcessor class for handling
    CommonApp Freshman School Forms zip files.
    """
    zip_pattern = r'ugaapplsform_.+\.zip'
