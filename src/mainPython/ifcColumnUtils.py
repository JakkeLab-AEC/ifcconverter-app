from typing import Literal

import ifcopenshell
import ifcopenshell.guid
from ifcopenshell import entity_instance

class IfcUtil:
    def __init__(self, ifc_model: ifcopenshell.file):
        self.model = ifc_model

    def create_direction(
        self,
        coordinate: tuple[float, float, float]
        ) -> entity_instance:
        return self.model.create_entity(
            type="IfcDirection",
            DirectionRatios=coordinate
        )

    def create_axis2placement3d(
            self,
        ) -> entity_instance:
        return self.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=self.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Axis=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

    def create_axis2placement2d(
            self
        ) -> entity_instance:
        return self.model.create_entity(
            type="IfcAxis2Placement2D",
            Location=self.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            RefDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

    def create_cartesian_point(
            self,
            coordinates: tuple[float, float, float]
        ) -> entity_instance:
        return self.model.create_entity(
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
            true_north_entity = self.model.create_entity(
                type="IfcDirection",
                DirectionRatios=true_north
            )

        return self.model.create_entity(
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
            target_view: str = ".MODEL_VIEW.",
            target_scale: float = None,
            user_defined_target_view: str = None
    ) -> entity_instance:
        return self.model.create_entity(
            type="IfcGeometricRepresentationSubContext",
            ContextIdentifier=context_identifier,
            ContextType=context_type,
            ParentContext=parent_context,
            TargetView=target_view,
            TargetScale=target_scale,
            UserDefinedTargetView=user_defined_target_view
        )

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

        return self.model.create_entity(
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

        return self.model.create_entity(
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

        return self.model.create_entity(
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

        return self.model.create_entity(
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

        extruded_area_axis = self.create_axis2placement3d()


        # Create ExtrudedAreaSolid
        self.create_extrude_area_solid(
            profile=profile,
            position=self.create_
        )

        column_type = self.model.create_entity(
            type="IfcColumnType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            Name=name,
            RepresentationMaps=[representation_map],
            PredefinedType="COLUMN"
        )




