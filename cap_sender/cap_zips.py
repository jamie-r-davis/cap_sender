import csv
import os
import re
import tempfile
from io import StringIO
from zipfile import ZipFile
from cap_sender.cap_index import CAPIndex


def process_zips(src_dir, output_dir):
    outfiles = []
    # iterate over files in src_dir
    for f in os.listdir(src_dir):
        if not f.endswith('.zip'):
            continue
        src_path = os.path.join(src_dir, f)
        out_path = os.path.join(output_dir, f)
        temp_dir = tempfile.TemporaryDirectory()
        print(f"Found {src_path}...")
        # extract zip contents to temp dir
        with ZipFile(src_path) as zf:
            zf.extractall(temp_dir.name)
        # convert any xml into csv
        for f in os.listdir(temp_dir.name):
            if f.endswith('.xml'):
                infile = os.path.join(temp_dir.name, f)
                outfile = infile + '.txt'
                c = CAPIndex(infile)
                c.to_csv(outfile, delimiter='\t')
                os.remove(infile)
        # re-zip files to output_dir
        print(f"Writing {out_path}...")
        with ZipFile(out_path, 'w') as zf:
            for f in os.listdir(temp_dir.name):
                out_file = os.path.join(temp_dir.name, f)
                zf.write(out_file, f)
        print(f"Complete.")
        outfiles.append(out_path)
    return outfiles


class ZipProcessor:
    zip_pattern = ''
    pdf_pattern = ''

    def __init__(self, filename):
        self.fn = filename

    @classmethod
    def match(cls, filename):
        bn = os.path.basename(filename)
        if re.match(cls.zip_pattern, bn):
            return cls(filename)

    def transform(self):
        pass


class TransferProcessor(ZipProcessor):
    pdf_fieldnames=[]

    def transform(self):
        """
        Create a csv listing each pdf file and attributes
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
    zip_pattern = r'\d+_\d+_\d+_TR_Applications\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_.+)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name']


class TransferEvalProcessor(TransferProcessor):
    zip_pattern = r'\d+_\d+_\d+_TR_Evaluations\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_(?P<doc_id>\d+)_Evaluation_(?P<recommender>.+?)_.+)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name',
                      'doc_id', 'recommender']


class TransferTranscriptProcessor(TransferProcessor):
    zip_pattern = r'\d+_\d+_\d+_TR_College_Transcript\.zip'
    pdf_pattern = r'(?P<filename>TR_(?P<commonapp_id>\d+)_(?P<last_name>.+?)_(?P<first_name>.+?)_(?P<doc_id>\d+)_(?P<doc_type>Transcript)_(?P<college_code>\d+)_(?P<college_name>.+?)_(?P<submit_dt>.+?)\.pdf)'
    pdf_fieldnames = ['filename', 'commonapp_id', 'last_name', 'first_name',
                      'doc_id', 'college_name', 'submit_dt']


class FreshmanProcessor(ZipProcessor):

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
    zip_pattern = r'ugaappl_.+\.zip'


class FreshmanFormsProcessor(FreshmanProcessor):
    zip_pattern = r'ugaapplsform_.+\.zip'
