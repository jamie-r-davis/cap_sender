import os
import tempfile
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
