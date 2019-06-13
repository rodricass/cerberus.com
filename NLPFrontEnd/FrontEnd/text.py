import argparse
import re
import xml.etree.ElementTree as ET
import zipfile
import os
import sys

class Lector:
    def __init__(self, document):
        """
        Clase abstracta de la que heredan los lectores.

        :param path: path al archivo para leer
        """
        self.document = document

    def read(self):
        """
        Devuelve todo el texto del archivo self.document.
        """
        pass

class LectorTXT(Lector):
    def __init__(self, document):
        self.encoding = "utf-8"
        super().__init__(document)

    def read(self):
        """
        Devuelve todo el texto del archivo self.document.
        """
        self.document.seek(0)
        texto = self.document.read()
        try:
            texto = texto.decode(self.encoding)
        except UnicodeDecodeError:
            return ""
        texto = texto.replace("\r\n", "\n")
        return texto

class LectorDOCX(Lector):
    nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
    def qn(self, tag):
        """
        Stands for 'qualified name', a utility function to turn a namespace
        prefixed tag name into a Clark-notation qualified tag name for lxml. For
        example, ``qn('p:cSld')`` returns ``'{http://schemas.../main}cSld'``.
        Source: https://github.com/python-openxml/python-docx/
        """
        prefix, tagroot = tag.split(':')
        uri = self.nsmap[prefix]
        return '{{{}}}{}'.format(uri, tagroot)
    
    
    def xml2text(self, xml):
        """
        A string representing the textual content of this run, with content
        child elements like ``<w:tab/>`` translated to their Python
        equivalent.
        Adapted from: https://github.com/python-openxml/python-docx/
        """
        text = u''
        root = ET.fromstring(xml)
        for child in root.iter():
            if child.tag == self.qn('w:t'):
                t_text = child.text
                text += t_text if t_text is not None else ''
            elif child.tag == self.qn('w:tab'):
                text += '\t'
            elif child.tag in (self.qn('w:br'), self.qn('w:cr')):
                text += '\n'
            elif child.tag == self.qn("w:p"):
                text += '\n\n'
        return text
    
    
    def read(self):
        docx = self.document

        text = u''
    
        # unzip the docx in memory
        zipf = zipfile.ZipFile(docx)
        filelist = zipf.namelist()
    
        # get header text
        # there can be 3 header files in the zip
        header_xmls = 'word/header[0-9]*.xml'
        for fname in filelist:
            if re.match(header_xmls, fname):
                text += self.xml2text(zipf.read(fname))
    
        # get main text
        doc_xml = 'word/document.xml'
        text += self.xml2text(zipf.read(doc_xml))
    
        # get footer text
        # there can be 3 footer files in the zip
        footer_xmls = 'word/footer[0-9]*.xml'
        for fname in filelist:
            if re.match(footer_xmls, fname):
                text += self.xml2text(zipf.read(fname))
    
        zipf.close()
        return text.strip()
    
 
         