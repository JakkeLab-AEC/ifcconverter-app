from typing import Literal

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.selector
import ifcopenshell.api
import ifcopenshell.api.type

from ifcopenshell import entity_instance

from ifcWriter import IfcWriter

class IfcUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_direction(
        self,
        coordinate: tuple[float, float, float]
        ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcDirection",
            DirectionRatios=coordinate
        )

    def create_axis2placement3d(
            self,
            coordinate: entity_instance|None = None
        ) -> entity_instance:
        if coordinate is None:
            coordinate = self.writer.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))

        return self.writer.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=coordinate,
            Axis=self.writer.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=self.writer.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

    def create_axis2placement2d(
            self
        ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcAxis2Placement2D",
            Location=self.writer.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            RefDirection=self.writer.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

    def create_cartesian_point(
            self,
            coordinates: tuple[float, float, float]
        ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcCartesianPoint",
            Coordinates=coordinates
        )

    def create_geometric_representation_context(
            self,
            coordinate_space_dimension: int = 3,
            precision: float = 0.01,
            world_coordinate_system: entity_instance = None,
            true_north: tuple[float, float] = None
        ) -> entity_instance:

        if world_coordinate_system is None:
            world_coordinate_system = self.create_axis2placement3d()

        true_north_entity = None
        if true_north:
            true_north_entity = self.writer.model.create_entity(
                type="IfcDirection",
                DirectionRatios=true_north
            )

        return self.writer.model.create_entity(
            type="IfcGeometricRepresentationContext",
            ContextType="Model",
            CoordinateSpaceDimension=coordinate_space_dimension,
            Precision=precision,
            WorldCoordinateSystem=world_coordinate_system,
            TrueNorth=true_north_entity
        )

    def create_geometric_representation_sub_context(
            self,
            parent_context: entity_instance,
            context_identifier: str = "Body",
            context_type: str = "Model",
            target_view: str = "MODEL_VIEW",
            target_scale: float = None,
            user_defined_target_view: str = None
    ) -> entity_instance:

        entity = self.writer.model.create_entity(
            type="IfcGeometricRepresentationSubContext",
            ContextIdentifier=context_identifier,
            ContextType=context_type,
            ParentContext=parent_context,
            TargetView=target_view,
            TargetScale=target_scale,
            UserDefinedTargetView=user_defined_target_view
        )

        self.writer.geometric_representation_subContext['Body'] = entity
        return entity

    def create_i_shape_profile_def(
            self,
            profile_name: str,
            position: entity_instance,
            overall_width: float,
            overall_depth: float,
            web_thickness: float,
            flange_thickness: float,
            fillet_radius: float,
        ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcIShapeProfileDef",
            Position=position,
            ProfileType="AREA",
            ProfileName=profile_name,
            OverallWidth=overall_width,
            OverallDepth=overall_depth,
            WebThickness=web_thickness,
            FlangeThickness=flange_thickness,
            FilletRadius=fillet_radius,
        )

    def create_extrude_area_solid(
            self,
            profile: entity_instance,
            position: entity_instance,
            direction: entity_instance,
            depth: float
        ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=position,
            ExtrudedDirection=direction,
            Depth=depth
        )

    def create_shape_representation(
            self,
            context_of_items: entity_instance,
            representation_identifier: Literal['Body'],
            representation_type: Literal['SweptSolid', 'MappedRepresentation'],
            items: list[entity_instance],   #IfcExtrudedAreaSolid, ...
        ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=context_of_items,
            RepresentationIdentifier=representation_identifier,
            RepresentationType=representation_type,
            Items=items
        )


    def create_representation_map(
            self,
            mapping_origin: entity_instance,
            representation: entity_instance,
    ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcRepresentationMap",
            MappingOrigin=mapping_origin,
            MappedRepresentation=representation
        )

    def create_column_type(
            self,
            name: str,
            extrusion_depth: float,
            dimension_args: dict[str, float]
    ) -> dict[str, any]:
        # Create origin point
        origin = self.create_axis2placement3d()

        # Create GeometricRepresentationContext
        geom_representation_ctx = self.create_geometric_representation_context()
        geom_representation_sub_ctx = self.create_geometric_representation_sub_context(
            parent_context=geom_representation_ctx
        )

        # Create Profile and placement
        profile = self.create_i_shape_profile_def(
            profile_name=name,
            position=self.create_cartesian_point((0.0, 0.0, 0.0)),
            overall_width=dimension_args['w'],
            overall_depth=dimension_args['h'],
            web_thickness=dimension_args['tw'],
            flange_thickness=dimension_args['tf'],
            fillet_radius=dimension_args['r']
        )

        # Create ExtrudedAreaSolid
        extruded_area_solid = self.create_extrude_area_solid(
            profile=profile,
            position=origin,
            direction=self.create_direction(coordinate=(0.0, 0.0, 1.0)),
            depth=extrusion_depth
        )

        # Create ShaperRepresentation
        shape_representation = self.create_shape_representation(
            context_of_items=geom_representation_sub_ctx,
            representation_identifier='Body',
            representation_type='SweptSolid',
            items=[extruded_area_solid]
        )

        # Create representation map
        representation_map = self.create_representation_map(
            mapping_origin=origin,
            representation=shape_representation
        )

        # Create column type
        column_type = self.writer.model.create_entity(
            type="IfcColumnType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.model.by_type("IfcOwnerHistory")[0],
            Name=name,
            RepresentationMaps=[representation_map],
            PredefinedType="COLUMN"
        )

        created_data = {
            "Entity" : column_type,
            "RepresentationMap": representation_map,
            "Origin": origin,
            "Extrusion": extruded_area_solid,
            "Depth": extrusion_depth
        }

        self.writer.element_types['column_types'][name] = created_data
        return created_data

    def create_mapped_item(
            self,
            mapping_source: entity_instance,
            mapping_target: entity_instance,
       ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcMappedItem",
            MappingSource=mapping_source,   # IfcRepresentationMap
            MappingTarget=mapping_target,   # IfcCartesianTransformationOperator
        )

    def create_product_definition_shape(
        self,
        representations: list[entity_instance]
    ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcProductDefinitionShape",
            Representations=representations
        )

    def create_storey_location(
        self,
        level: float
    ) -> entity_instance:

        local_placement1 = self.writer.model.create_entity(
            type="IfcLocalPlacement",
            RelativePlacement=self.create_axis2placement3d(coordinate=self.writer.origin),
        )

        local_placement2 = self.writer.model.create_entity(
            type="IfcLocalPlacement",
            PlacementRelTo=local_placement1,
            RelativePlacement=self.create_axis2placement3d(coordinate=self.writer.origin)
        )

        level_location = self.create_axis2placement3d(
            coordinate=self.create_cartesian_point((0.0, 0.0, level))
        )

        storey_placement = self.writer.model.create_entity(
            type="IfcLocalPlacement",
            PlacementRelTo=local_placement2,
            RelativePlacement=level_location
        )

        return storey_placement

    def create_column(
        self,
        name: str,
        depth: float,
        dimension_args: dict[str, float],
        scale: float,
        coordinate: tuple[float, float, float],
        target_storey_name: str,
    ) -> entity_instance:

        #region Create ProductDefinitionShape
        # Create column type
        filtered_items = filter(
            lambda item: item['Depth'] == depth,
            self.writer.element_types['column_types'].values()
        )

        if len(list(filtered_items)) > 0:
            col_type_data = filtered_items[0]
        else:
            col_type_data = self.create_column_type(name=name, extrusion_depth=depth, dimension_args=dimension_args)

        # Create IfcMappedItem
        cartesian_transform_operator = self.writer.model.create_entity(
            type="IfcCartesianTransformationOperator",
            LocalOrigin=self.writer.origin,
            Scale=scale
        )

        mapped_item = self.create_mapped_item(
            mapping_source=col_type_data['RepresentationMap'],
            mapping_target=cartesian_transform_operator
        )

        # Create IfcShapeRepresentation
        shape_representation = self.create_shape_representation(
            context_of_items=self.writer.geometric_representation_subContext['Body'],
            representation_identifier='Body',
            representation_type='MappedRepresentation',
            items=[mapped_item]
        )

        # Create IfcProductDefinitionShape
        column_representation = self.create_product_definition_shape(
            representations=[shape_representation]
        )
        #endregion

        #region Create local coordination
        coordinate = self.create_cartesian_point(coordinate)
        column_location = self.writer.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=coordinate
        )
        
        #endregion

        query = "IfcBuildingStorey"
        filtered_elements = list(ifcopenshell.util.selector.filter_elements(self.writer.model, query=query))
        result_dict = {item.Name: item for item in filtered_elements}

        storey_object_placement = result_dict[target_storey_name].ObjectPlacement

        column_placement = self.writer.model.create_entity(
            type="IfcLocalPlacement",
            PlacementRelTo=column_location,
            RelativePlacement=storey_object_placement
        )

        column = self.writer.model.create_entity(
            type="IfcColumn",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.model.by_type("IfcOwnerHistory")[0],
            Representation=column_representation,
            ObjectPlacement=column_placement,
            Name=name
        )

        ifcopenshell.api.type.assign_type(
            file=self.writer.model,
            related_objects=[column],
            relating_type=col_type_data["Entity"]
        )

        return column







