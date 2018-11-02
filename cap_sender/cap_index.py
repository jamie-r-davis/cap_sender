import csv
import re

from lxml import etree
from zipfile import ZipFile


def read_form_type(filename):
    app_pattern = r'.+!\d+\.pdf'
    form_pattern = r'.+!\d+_(?P<form_type>\w+)_\d+\.pdf'
    if re.match(app_pattern, filename):
        return 'APP'
    if re.match(form_pattern, filename):
        return re.match(form_pattern, filename).group('form_type')


class CAPIndex:
    def __init__(self, fn):
        self.fn = fn
        self.data = list(self.parse())

    def read(self):
        if self.fn.endswith('.zip'):
            return self._read_zip()
        elif self.fn.endswith('.xml'):
            return self._read_xml()

    def _read_xml(self):
        with open(self.fn, 'rb') as f:
            self.xmlfile = self.fn
            return f.read()

    def _read_zip(self):
        with ZipFile(self.fn) as zf:
            for fn in zf.namelist():
                if fn.endswith('.xml'):
                    self.xmlfile = fn
                    return zf.read(fn)

    def parse(self):
        tree = etree.fromstring(self.read())
        for node in tree.findall('file'):
            yield self._parse_node(node)

    def _parse_node(self, node):
        attrs = {}
        for k, v in node.attrib.items():
            attrs[k] = v
        for child in node.iterchildren():
            for k, v in child.attrib.items():
                attrs[k] = v
        attrs['form_type'] = read_form_type(attrs['name'])
        return attrs

    def to_csv(self, filepath, **kwargs):
        keys = self.data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys, **kwargs)
            writer.writeheader()
            for item in self.data:
                writer.writerow(item)
