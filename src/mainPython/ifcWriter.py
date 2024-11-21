import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate

class IfcWriter:
    def __init__(self):
        """
        Create empty Ifc
        Currently created as IFC4
        """
        model = ifcopenshell.api.project.create_file(version="IFC4")
        ifcopenshell.api.unit.assign_unit(model)

    """
    Set project name
    :param project_name: Project's name
    """
    def set_project_info(self, project_name="Default Project"):
        ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcProject", name="project_name")
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

    def add_entity_wall(self):
        wall = ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(
            self.model,
            product=wall
        )

        representation = ifcopenshell.api.geometry.add_wall_representation(
            self.model,
            context=self.body,
            length=5,
            height=3,
            thickness=0.2
        )

        ifcopenshell.api.geometry.assign_representation(
            self.model,
            product=wall,
            representation=representation
        )

        ifcopenshell.api.spatial.assign_container(
            self.model,
            relating_structure=self.storey,
            products=[wall]
        )

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}")