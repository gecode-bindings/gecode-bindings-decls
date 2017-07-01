import xml.etree.ElementTree as ET
import yaml
import sys

NOTICE = """# This file was automatically extracted from Gecode source files.
# It is subject to the same Copyright as the source files from which
# it is derived, and is distributed under the same Licensing conditions.
"""

class Extractor:

    def __init__(self, version, filename):
        self.filename = filename
        self.version = version
        tree = ET.parse(filename)
        self.root = tree.getroot()

    @property
    def prototypes(self):
        for e in self.root.findall("./compounddef/sectiondef[@kind='func']/memberdef"):
            _id = e.get("id")
            if (not _id.startswith("group__TaskModel")) \
               or _id.startswith("group__TaskModelMiniModel"):
                continue
            txt = e.findtext("name")
            if txt.startswith("operator") or txt=="tiebreak" or txt=="wait":
                continue
            yield self._extract_prototype(e)

    def _text(self, e):
        return None if e is None else "".join(e.itertext())

    def _extract_prototype(self, e):
        typ = self._text(e.find("type"))
        for pr in self.PREFIXES_TO_REMOVE:
            if typ.startswith(pr):
                typ = typ[len(pr)+1:]
                break
        return {
            "type": typ,
            "name": self._text(e.find("name")),
            "args": [
                {"type": self._text(p.find("type")),
                 "name": self._text(p.find("declname")),
                 "default": self._text(e.find("defval"))}
                for p in e.findall("param")]}

    PREFIXES_TO_REMOVE = ("GECODE_SET_EXPORT", "GECODE_INT_EXPORT",
                          "GECODE_FLOAT_EXPORT", "GECODE_KERNEL_EXPORT")
            
    def extract_prototypes(self):
        with open("data/gecode-prototypes-%s.yml" % self.version, "w") as f:
            f.write(NOTICE)
            yaml.safe_dump_all(self.prototypes, stream=f, indent=4, default_flow_style=False)

    @property
    def enums(self):
        for e in self.root.findall("./compounddef/sectiondef[@kind='enum']/memberdef"):
            yield {
                "name": self._text(e.find("name")),
                "values": [
                    self._text(v)
                    for v in e.findall("enumvalue/name")]}

    def extract_enums(self):
        with open("data/gecode-enums-%s.yml" % self.version, "w") as f:
            f.write(NOTICE)
            yaml.safe_dump_all(self.enums, stream=f, indent=4, default_flow_style=False)


if __name__ == '__main__':
    version = sys.argv[1]
    extractor = Extractor(version, "xml/namespaceGecode.xml")
    extractor.extract_prototypes()
    extractor.extract_enums()
