import math

from ifcopenshell import entity_instance
import ifcopenshell.guid
import ifcopenshell.util.selector
from dist.mainPython.ifcWriter import IfcWriter

class IfcSharedElementDataUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_column(
        self,
        profile_name: str,
        col_type_name: str,
        target_storey_name: str,
        coordinate: tuple[float, float],
        base_offset: float,
        height: float,
        rotation_degree: float,
        profile_arg: dict[str, float] | None = None
    ) -> entity_instance:

        if profile_name in self.writer.profiles.keys():
            profile = self.writer.profiles[profile_name]
        else:
            profile = self.writer.ifcResourceEntityUtil.create_profile_IShape (
                profile_name=profile_name,
                overall_width=profile_arg['w'],
                overall_depth=profile_arg['h'],
                web_thickness=profile_arg['tw'],
                flange_thickness=profile_arg['tf'],
                fillet_radius=profile_arg['r']
            )

        if target_storey_name not in self.writer.storeys.keys():
            raise ValueError(f"Not Exist Error: Storey f'{target_storey_name}' does not exist.")

        target_storey = self.writer.storeys[target_storey_name]

        context = self.writer.ifcResourceEntityUtil.create_geometric_representation_context(
            coordinate_space_dimension=3,
            context_type="Model",
        )

        sub_context = self.writer.ifcResourceEntityUtil.create_geometric_representation_sub_context(
            parent_context=context,
            context_identifier="Body"
        )

        extrusion_solid = self.writer.ifcResourceEntityUtil.create_extruded_area_solid(
            swept_area=profile,
            z_coordinate=target_storey['Elevation'] + base_offset,
            extruded_direction=self.writer.axis_z,
            depth=height
        )

        extrusion_solid_shape_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=sub_context,
            representation_identifier="Body",
            representation_type="SweptSolid",
            items=[extrusion_solid]
        )

        representation_map = self.writer.ifcResourceEntityUtil.create_representation_map(
            mapped_representation=extrusion_solid_shape_representation
        )

        mapped_item = self.writer.ifcResourceEntityUtil.create_mapped_item(
            mapping_source=representation_map,
            mapping_target=self.writer.ifcResourceEntityUtil.create_cartesian_transformation_operator3d()
        )

        mapped_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=sub_context,
            representation_type="MappedRepresentation",
            representation_identifier="Body",
            items=[mapped_item]
        )

        product_definition_shape = self.writer.ifcResourceEntityUtil.create_product_define_shape(
            representations=[mapped_representation]
        )

        # Create column type
        if col_type_name in self.writer.element_types['column_types'].keys():
            column_type=self.writer.element_types['column_types'][col_type_name]['Entity']
        else:
            column_type = self.writer.model.create_entity(
                type="IfcColumnType",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=self.writer.owner_history,
                Name=col_type_name,
                RepresentationMaps=[mapped_item]
            )

        # Create column's Placement
        radian = math.radians(rotation_degree)
        col_relative_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.ifcResourceEntityUtil.create_cartesian_point_3d((coordinate[0], coordinate[1], abs(target_storey['Elevation']))),
            axis=self.writer.axis_z,
            ref_direction=self.writer.ifcResourceEntityUtil.create_direction_3d((math.cos(radian), math.sin(radian), 0.0))
        )

        column_placement = self.writer.ifcResourceEntityUtil.create_local_placement(
            placement_rel_to=target_storey['ObjectPlacement'],
            relative_placement=col_relative_placement
        )

        # Create column entity
        column = self.writer.model.create_entity(
            type="IfcColumn",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            Name=col_type_name,
            ObjectType=col_type_name,
            ObjectPlacement=column_placement,
            Representation=product_definition_shape
        )

        # Create RelContainedSpatialStructure
        self.writer.ifcCoreDataUtil.create_rel_contained_in_spatial_structure(
            related_elements=[column],
            relating_structure=target_storey["Entity"],
            owner_history=self.writer.owner_history,
        )