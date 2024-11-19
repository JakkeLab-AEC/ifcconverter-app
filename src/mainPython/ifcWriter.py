import ifcopenshell
import ifcopenshell.api

class IfcWriter:
    def __init__(self):
        """
        Create empty Ifc
        """
        self.model = ifcopenshell.file(schema="IFC4")

    """
    Set project name
    :param project_name: Project's name
    """
    def set_project_info(self, project_name="Default Project"):

        ifcopenshell.api.run(
            "root.create_entity",
            self.model,
            ifc_class="IfcProject",
            name=project_name
        )
        print(f"Project info set: {project_name}")

    def add_entity(self, entity_type, name, **kwargs):
        """
        Add IFC Entity
        :param entity_type: Type of entity (example: 'IfcWall', 'IfcDoor')
        :param name: Entity's name
        :param kwargs: Additional properties (will be applied)
        """
        entity = ifcopenshell.api.run(
            "root.create_entity",
            self.model,
            ifc_class=entity_type,
            name=name
        )
        print(f"Entity added: {entity_type}, {name}")
        return entity

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}")