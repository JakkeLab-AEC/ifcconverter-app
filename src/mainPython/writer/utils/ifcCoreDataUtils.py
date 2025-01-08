from ifcopenshell import entity_instance
import ifcopenshell.guid
import ifcopenshell.util.selector
from dist.mainPython.writer.ifcWriter import IfcWriter

class IfcCoreDataUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_storey(
        self,
        name: str,
        elevation: float,
        description: str|None=None,
        object_type: str|None=None,
        long_name: str|None=None,
    ) -> entity_instance:
        if name in self.writer.storeys.keys():
            raise ValueError(f"Duplication Error : Storey '{name}' already exists.")

        # Create default plane
        placement_rel_to = self.writer.ifcResourceEntityUtil.create_local_placement(
            relative_placement=self.writer.ifcResourceEntityUtil.create_axis2placement_2d(location=self.writer.origin2d),
            placement_rel_to=self.writer.ifcResourceEntityUtil.create_local_placement(relative_placement=self.writer.ifcResourceEntityUtil.create_axis2placement_2d(location=self.writer.origin2d))
        )

        relative_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(location=self.writer.ifcResourceEntityUtil.create_cartesian_point_3d((0., 0., elevation)))

        # Create storey
        object_placement = self.writer.ifcResourceEntityUtil.create_local_placement(relative_placement=relative_placement, placement_rel_to=placement_rel_to)
        storey = self.writer.model.create_entity(
            type="IfcBuildingStorey",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            Name=name,
            Description=description,
            ObjectType=object_type,
            ObjectPlacement=self.writer.ifcResourceEntityUtil.create_local_placement(relative_placement=relative_placement, placement_rel_to=placement_rel_to),
            LongName=long_name,
            Elevation=elevation
        )

        # Relating story to building
        filtered_elements = list(ifcopenshell.util.selector.filter_elements(self.writer.model, query="IfcRelAggregates, Name=RelStoreyToBuilding"))
        if len(filtered_elements) == 0:
            self.create_rel_aggregates(
                name="RelStoreyToBuilding",
                relating_object=self.writer.building,
                related_objects=[storey]
            )
        else:
            rel_aggregates = filtered_elements[0]
            existing_storeys = list(rel_aggregates.RelatedObjects)
            existing_storeys.append(storey)
            rel_aggregates.RelatedObjects = tuple(existing_storeys)

        self.writer.storeys[name] = {
            "Entity": storey,
            "ObjectPlacement": object_placement,
            "Elevation": elevation
        }

        return storey

    def create_rel_aggregates(
        self,
        name: str,
        relating_object: entity_instance,
        related_objects: list[entity_instance]
    ) -> entity_instance:
        """
         The aggregation relationship IfcRelAggregates is a special type of the general composition/decomposition (or whole/part) relationship IfcRelDecomposes.
         The aggregation relationship can be applied to all subtypes of object.
         RelatingObjects will be related to RelatingObject. For example, a set of building storeys can be related to a IfcBuilding.
         :param name: Name of this entity. Use for identification factor
         :param relating_object: Entity of IfcObjectDefinition
         :param related_objects: Set of IfcObjectDefinition
        """

        return self.writer.model.create_entity(
            type="IfcRelAggregates",
            Name=name,
            RelatingObject=relating_object,
            RelatedObjects=related_objects
        )

    def create_rel_contained_in_spatial_structure(
            self,
            related_elements: set[entity_instance],
            relating_structure: entity_instance,
            owner_history: entity_instance | None = None,
            name: str | None = None,
            description: str | None = None
    ) -> entity_instance:
        """
        This entity is used to assign elements to a certain level of the spatial project structure.
        Predefined spatial structure elements to which elements can be assigned are \n
        - site as IfcSite
        - building as IfcBuilding
        - storey as IfcBuildingStorey
        - space as IfcSpace
        For example, IfcColumn can be related to IfcBuildingStorey.
        :param related_elements: Set of IfcProduct
        :param relating_structure: Entity of IfcSpatialStructureElement
        :param owner_history: Entity of IfcOwnerHistory
        :param name: Name of this entity
        :param description: Description of this entity
        """
        if owner_history is None:
            owner_history = self.writer.owner_history

        return self.writer.model.create_entity(
            type="IfcRelContainedInSpatialStructure",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            Name=name,
            Description=description,
            RelatedElements=related_elements,
            RelatingStructure=relating_structure
        )


