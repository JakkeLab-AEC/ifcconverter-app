import ifcopenshell

from src.mainPython.model.enums.WriterCategory import WriterCategory


class IfcWriterModel(ifcopenshell.entity_instance):
    def __init__(self, writer_category: WriterCategory):
        self.writer_category = writer_category
        super().__init__()