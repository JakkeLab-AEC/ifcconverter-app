from dist.mainPython.ifcWriter import IfcWriter
from ifcopenshell import entity_instance

class IfcStoreyUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_storey(
        self,
        name,
    ) -> entity_instance:
