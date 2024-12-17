from dist.mainPython.ifcWriter import IfcWriter
from typing import Literal
from ifcopenshell import entity_instance
import ifcopenshell.guid

class IfcResourceEntityUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_cartesian_point_2d(self, coordinate:tuple[float, float]) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcCartesianPoint",
            Coordinates=coordinate
        )

    def create_cartesian_point_3d(self, coordinate:tuple[float, float, float]) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcCartesianPoint",
            Coordinates=coordinate
        )

    def create_direction_2d(self, coordinate: tuple[float, float]) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcDirection",
            DirectionRatios=coordinate
        )

    def create_direction_3d(self, coordinate: tuple[float, float, float]) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcDirection",
            DirectionRatios=coordinate
        )

    def create_axis2placement_2d(
            self,
            location: entity_instance | None = None,
            ref_direction: entity_instance | None = None
    ) -> entity_instance:
        """
        :param location: Entity of IfcCartesianPoint as 2D coordinates.
        :param ref_direction: Entity of IfcDirection as 2D coordinates.
        """

        return self.writer.model.create_entity(
            type="IfcAxis2Placement2D",
            Location=location,
            RefDirection=ref_direction
        )

    def create_axis2placement_3d(
            self,
            location: entity_instance|None = None,
            axis: entity_instance|None = None,
            ref_direction: entity_instance|None = None
    ) -> entity_instance:
        """
        Create IfcAxis2Placement3D entity.
        :param location: Entity of IfcCartesianPoint
        :param axis: Entity of IfcDirection
        :param ref_direction: Entity of IfcDirection
        """
        return self.writer.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=location,
            Axis=axis,
            RefDirection=ref_direction
        )

    def create_local_placement(
        self,
        relative_placement: entity_instance,
        placement_rel_to: entity_instance|None = None
    ) -> entity_instance:
        """
        The following conventions shall apply as default relative positions if the relative placement is used.
        The conventions are given for all five direct subtypes of IfcProduct, the IfcSpatialStructureElement, IfcElement, IfcAnnotation, IfcGrid, IfcPort.
        :param relative_placement: Entity of IfcObjectPlacement
        :param placement_rel_to: Entity of IfcAxis2Placement
        """
        return self.writer.model.create_entity(
            type="IfcLocalPlacement",
            PlacementRelTo=placement_rel_to,
            RelativePlacement=relative_placement
        )

    def create_profile_IShape(
            self,
            profile_name: str,
            overall_width: float,
            overall_depth: float,
            web_thickness: float,
            flange_thickness: float,
            fillet_radius: float,
    ) -> entity_instance:
        """
        Create I-shape profile.
        :param profile_name: Profile's name. If the profile with given name already
                             exists in writer instance, exception occurs.
        :param overall_width: Width of shape.
        :param overall_depth: Height of shape.
        :param web_thickness: Thickness of web.
        :param flange_thickness: Thickness of flange.
        :param fillet_radius: Radius of fillet.
        """
        if profile_name in self.writer.profiles.keys():
            raise ValueError(f"Profile '{profile_name}' already exists.")

        position = self.create_axis2placement_2d(
            location=self.create_cartesian_point_2d((0., 0.)),
            ref_direction=self.create_direction_2d((1.,0.))
        )

        profile = self.writer.model.create_entity(
            type="IfcIShapeProfileDef",
            ProfileType="AREA",
            ProfileName=profile_name,
            Position=position,
            OverallWidth=overall_width,
            OverallDepth=overall_depth,
            WebThickness=web_thickness,
            FlangeThickness=flange_thickness,
            FilletRadius=fillet_radius
        )

        self.writer.profiles[profile_name] = profile
        return profile

    def create_extruded_area_solid(
        self,
        swept_area: entity_instance,
        z_coordinate: float,
        extruded_direction: entity_instance,
        depth: float
    ) -> entity_instance:
        """
        Create extruded area solid. Adjusting z_coordinate makes difference while placing the extrusion.
        1. When z_coordinate is same with elevation of the linked building storey, extrusion places on that level.
        2. When higher or lower, the entity will be placed above or below of the difference of values.
           (Example: Elevation 2000, z_coordinate 2000, base offset is 0. 3000 and 2000, base offset is 1000)
        :param swept_area: Entity of IfcProfileDef
        :param z_coordinate: Absolute level of extrusion's base level,
        :param extruded_direction: Entity of IfcDirection
        :param depth: Extrusion distance.
        """
        position=self.create_axis2placement_3d(
            location=self.create_cartesian_point_3d((0.,0.,-z_coordinate)),
            axis=self.create_direction_3d((0.,0.,1.)),
            ref_direction=self.create_direction_3d((-1.,0.,0.))
        )

        return self.writer.model.create_entity(
            type="IfcExtrudedAreaSolid",
            SweptArea=swept_area,
            Position=position,
            ExtrudedDirection=extruded_direction,
            Depth=depth
        )

    def create_shape_representation(
        self,
        context_of_items: entity_instance,
        representation_identifier: Literal["Body", "Axis", "Box", "Footprint"],
        representation_type: Literal["SweptSolid", "MappedRepresentation"],
        items: list[entity_instance],
    ) -> entity_instance:
        """
        Create IfcShapeRepresentation.
        :param context_of_items: Entity of IfcRepresentationContext
        :param representation_identifier: String of value
        :param representation_type: String of value
        :param items: Sef of IfcRepresentationItem
        """

        return self.writer.model.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=context_of_items,
            RepresentationIdentifier=representation_identifier,
            RepresentationType=representation_type,
            Items=items
        )

    def create_representation_map(
        self,
        mapped_representation: entity_instance,
        mapping_origin: entity_instance | None = None,
    ) -> entity_instance:
        """
        Create an IfcRepresentationMap, which links an object's position to its representation.

        - The mapping origin sets where the object will be placed.
        - The mapped representation defines what the object looks like (e.g., its geometry).

        :param mapping_origin: IfcAxis2Placement instance that specifies the origin and orientation for the object.
        :param mapped_representation: IfcRepresentation instance that defines the object to be represented. If this is None,
                                      origin(0., 0., 0.) will be set.
        :return: A new IfcRepresentationMap instance linking the origin and representation.
        """
        if mapping_origin is None:
            mapping_origin = self.create_axis2placement_3d(location=self.writer.origin3d)

        return self.writer.model.create_entity(
            type="IfcRepresentationMap",
            MappingOrigin=mapping_origin,
            MappedRepresentation=mapped_representation
        )

    def create_cartesian_transformation_operator3d(
        self,
        axis1: entity_instance = None,
        axis2: entity_instance = None,
        axis3: entity_instance = None,
        local_origin: entity_instance = None,
        scale: float = 1.0,
    ) -> entity_instance:
        """
        :param axis1: Entity of IfcDirection
        :param axis2: Entity of IfcDirection
        :param axis3: Entity of IfcDirection
        :param local_origin: Entity of 	IfcCartesianPoint
        :param scale: Scale factor
        """
        if local_origin is None:
            local_origin = self.writer.origin3d

        return self.writer.model.create_entity(
            type="IfcCartesianTransformationOperator3D",
            Axis1=axis1,
            Axis2=axis2,
            Axis3=axis3,
            Scale=scale,
            LocalOrigin=local_origin
        )

    def create_mapped_item(
        self,
        mapping_source: entity_instance,
        mapping_target: entity_instance
    ) -> entity_instance:
        """
        This creates the representation by mapping target and source.
        :param mapping_source: Entity of IfcRepresentationMap
        :param mapping_target: Entity of IfcCartesianTransformationOperator
        """
        return self.writer.model.create_entity(
            type="IfcMappedItem",
            MappingSource=mapping_source,
            MappingTarget=mapping_target,
        )

    def create_geometric_representation_context(
        self,
        coordinate_space_dimension: int,
        precision: float=0.01,
        world_coordinate_system: entity_instance|None = None,
        context_type: Literal["Model", "Plan", "NotDefined"] | None = None,
        context_identifier: str|None=None,
        true_north: entity_instance|None=None
    ) -> entity_instance:
        """
        This defines the context of the shapes within a project.
        :param coordinate_space_dimension: Dimension of space.
        :param precision: the value of model's precision.
        :param world_coordinate_system: Entity of IfcAxis2Placement3D
        :param context_type: If this value is None, NotDefined will be selected.
        :param context_identifier: Identifier of context.
        :param true_north: Entity of IfcDirection (2D). If the value is None, (0., 1.) will be set as the direction.
        """
        if true_north is None:
            true_north = self.writer.axis_y_2d
        if world_coordinate_system is None:
            world_coordinate_system = self.create_axis2placement_3d(location=self.writer.origin3d)

        return self.writer.model.create_entity(
            type="IfcGeometricRepresentationContext",
            ContextIdentifier=context_identifier,
            ContextType=context_type,
            CoordinateSpaceDimension=coordinate_space_dimension,
            Precision=precision,
            WorldCoordinateSystem=world_coordinate_system,
            TrueNorth=true_north
        )

    def create_geometric_representation_sub_context(
        self,
        parent_context: entity_instance,
        context_identifier: str|None=None,
        context_type: Literal["Model", "Plan", "NotDefined"]|None = None,
        target_scale: float=1.0,
        target_view: str="MODEL_VIEW",
        user_defined_target_view: str|None=None
    ) -> entity_instance:
        """
        :param parent_context: Entity of IfcGeometricRepresentationContext.
        :param context_identifier: Identifying string.
        :param context_type: Type of context.
        :param target_scale: Scale of context.
        :param target_view: Name of view.
        :param user_defined_target_view: Name of user defined target view.
        """
        return self.writer.model.create_entity(
            type="IfcGeometricRepresentationSubContext",
            ContextIdentifier=context_identifier,
            ContextType=context_type,
            ParentContext=parent_context,
            TargetScale=target_scale,
            TargetView=target_view,
            UserDefinedTargetView=user_defined_target_view
        )

    def create_product_define_shape(
        self,
        representations: list[entity_instance],
        name: str|None=None,
        description: str|None=None
    ) -> entity_instance:
        """
        This is used for identifying the shape of product.
        :param representations: Entity of IfcRepresentation
        :param name: Name of product shape.
        :param description: Description of this entity.
        """
        return self.writer.model.create_entity(
            type="IfcProductDefinitionShape",
            Name=name,
            Description=description,
            Representations=representations
        )

    def create_rel_defines_by_type(
        self,
        name: str,
        description: str,
        related_objects: set[entity_instance],
        relating_type: entity_instance,
        owner_history: entity_instance | None = None,
    ) -> entity_instance:
        """
        This defines the relationships between an object type and objects.
        :param name: Name of relation
        :param owner_history: Entity of IfcOwnerHistory
        :param description: Description of relation
        :param related_objects: Entity of IfcObject to allocate the types.
        :param relating_type: Entity of IfcTypeObject. This will allocate as the type of all related objects.
        """

        if owner_history is None:
            owner_history = self.writer.owner_history

        return self.writer.model.create_entity(
            type="IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            Name=name,
            Description=description,
            RelatedObjects=related_objects,
            RelatingType=relating_type
        )

    # Material and styles
    def create_colour_rgb(
        self,
        red: float,
        green: float,
        blue: float
    ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcColourRgb",
            Red=red,
            Green=green,
            Blue=blue
        )

    def create_surface_style_rendering(
        self,
        rgba: dict[str, float],
    ) -> entity_instance:

        color = self.create_colour_rgb(
            red=min(rgba["r"]/255, 255),
            green=min(rgba["g"]/255, 255),
            blue=min(rgba["b"] / 255, 255),
        )

        return self.writer.model.create_entity(
            type="IfcSurfaceStyleRendering",
            SurfaceColour=color,
            Transparency=rgba['a'],
            ReflectionColour=self.writer.model.create_entity(type="IfcNormalisedRatioMeasure", wrappedValue=0.5),
            SpecularColour=self.writer.model.create_entity(type="IfcSpecularExponent", wrappedValue=128.),
            ReflectanceMethod='NOTDEFINED'
        )

    def create_surface_style(
        self,
        name: str,
        side: Literal["POSITIVE", "NEGATIVE", "BOTH"],
        styles: list[entity_instance]
    ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcSurfaceStyle",
            Name=name,
            Side=side,
            Styles=styles
        )

    def create_presentation_style_assignment(
        self,
        styles: list[entity_instance]
    ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcPresentationStyleAssignment",
            Styles=styles
        )

    def create_styled_item(
        self,
        styles: list[entity_instance]
    ) -> entity_instance:

        return self.writer.model.create_entity(
            type="IfcStyledItem",
            Styles=styles
        )

    def create_styled_representation(
        self,
        representation_identifier: Literal["Style"],
        representation_type: Literal["Material"],
        items: list[entity_instance],
        context_of_items: entity_instance
    ) -> entity_instance:
        return self.writer.model.create_entity(
            type="IfcStyledRepresentation",
            Items=items,
            RepresentationIdentifier=representation_identifier,
            RepresentationType=representation_type,
            ContextOfItems=context_of_items
        )

    def create_material(
        self,
        name: str,
        rgba: dict[str, float]
    ) -> entity_instance:

        if name in self.writer.materials.keys():
            raise ValueError(f"Duplication Error : Material {name} already exists.")

        surface_style_rendering = self.create_surface_style_rendering(rgba)

        surface_style = self.create_surface_style(
            name=f"SRF_{name}",
            side="BOTH",
            styles=[surface_style_rendering]
        )

        presentation_style_assignment = self.create_presentation_style_assignment(
            styles=[surface_style]
        )

        styled_item = self.create_styled_item(
            styles=[presentation_style_assignment]
        )

        styled_representation = self.create_styled_representation(
            representation_identifier="Style",
            representation_type="Material",
            items=[styled_item],
            context_of_items=self.writer.context
        )

        material = self.writer.model.create_entity(
            type="IfcMaterial",
            Name=name
        )

        material_definition_representation = self.writer.model.create_entity(
            type="IfcMaterialDefinitionRepresentation",
            RepresentedMaterial=material,
            Representations = [styled_representation]
        )

        entity_set = {
            "Definition": material_definition_representation,
            "Material": material,
        }

        self.writer.materials[name] = entity_set
        return entity_set

    def assign_material(
        self,
        material_name: str,
        target_objects: set[entity_instance]
    ) -> entity_instance:
        if material_name not in self.writer.materials.keys():
            raise ValueError(f"Not Exist Error : Material ${material_name} does not exist")

        material_entity = self.writer.materials[material_name]["Material"]
        return self.writer.model.create_entity(
            type="IfcRelAssociatesMaterial",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            RelatedObjects=target_objects,
            RelatingMaterial=material_entity
        )

    #Arbitary Profile
    def create_polyline(
        self,
        pts: list[tuple[float, float]],
    ) -> entity_instance:

        pt_entities: list[entity_instance] = []
        for pt in pts:
            pt_entity = self.create_cartesian_point_2d(pt)
            pt_entities.append(pt_entity)

        return self.writer.model.create_entity(
            type="IfcPolyline",
            Points=pt_entities,
        )

    def create_composite_curve_segment_linear(
        self,
        pts: list[tuple[float, float]]
    ) -> entity_instance:
        polyline = self.create_polyline(pts)
        return self.writer.model.create_entity(
            type="IfcCompositeCurveSegment",
            Transition="CONTINUOUS",
            SameSense=True,
            ParentCurve=polyline
        )

    def create_circle(
        self,
        center: tuple[float, float],
        radius: float,
        degree: float,
        direction: tuple[float, float] | None = None
    ) -> entity_instance:

        if direction is None:
            axis_direction = self.create_direction_2d((1., 0.))
        else:
            axis_direction = self.create_direction_2d(coordinate=direction)

        point = self.create_cartesian_point_2d(coordinate=center)
        position = self.create_axis2placement_2d(
            location=point,
            ref_direction=axis_direction
        )

        circle = self.writer.model.create_entity(
            type="IfcCircle",
            Radius=radius,
            Position=position
        )

        return self.writer.model.create_entity(
            type="IfcTrimmedCurve",
            BasisCurve=circle,
            Trim1=self.writer.model.create_entity(type="IfcParameterValue", wrappedValue=0.0),
            Trim2=self.writer.model.create_entity(type="IfcParameterValue", wrappedValue=degree),
            SenseAgreement=True,
            MasterRepresentation='PARAMETER'
        )

    def create_composite_curve_segment_circular(
        self,
        center: tuple[float, float],
        radius: float,
        degree: float,
        direction: tuple[float, float] | None = None
    ) -> entity_instance:

        curve = self.create_circle(center=center, radius=radius, degree=degree, direction=direction)
        return self.writer.model.create_entity(
            type="IfcCompositeCurveSegment",
            Transition="CONTINUOUS",
            SameSense=False,
            ParentCurve=curve
        )

    def create_arbitrary_closed_profile_def(
        self,
        profile_name: str,
        outer_curve: entity_instance
    ) -> entity_instance:
        if profile_name in self.writer.profiles.keys():
            raise ValueError(f"Duplication Error : Profile '{profile_name}' already exists.")

        profile = self.writer.model.create_entity(
            type="IfcArbitraryClosedProfileDef",
            ProfileType="AREA",
            ProfileName=profile_name,
            OuterCurve=outer_curve
        )

        self.writer.profiles[profile_name] = profile
        return profile

    def create_I_shape_beam_profile(
        self,
        profile_name: str,
        outer_width: float,
        outer_height: float,
        flange_thickness: float,
        web_thickness: float,
        fillet_radius: float
    ) -> entity_instance:

        if profile_name in self.writer.profiles.keys():
            raise ValueError(f"Duplication Error : Profile '{profile_name}' already exists.")

        segment1 = self.create_polyline(
            pts=[
                (-outer_width * 0.5, -outer_height * 0.5),
                (outer_width * 0.5, -outer_height * 0.5)
            ]
        )

        segment2 = self.create_polyline(
            pts=[
                (outer_width * 0.5, -outer_height * 0.5),
                (outer_width * 0.5, -outer_height * 0.5 + flange_thickness),
            ]
        )

        segment3 = self.create_polyline(
            pts=[
                (outer_width * 0.5, -outer_height * 0.5 + flange_thickness),
                (fillet_radius + web_thickness * 0.5, -outer_height * 0.5 + flange_thickness),
            ]
        )

        segment4 = self.create_circle(
            center=(fillet_radius + web_thickness * 0.5, -outer_height * 0.5 + flange_thickness + fillet_radius),
            radius=fillet_radius,
            degree=90,
            direction=(-1, 0)
        )

        segment5 = self.create_polyline(
            pts=[
                (web_thickness * 0.5, -outer_height * 0.5 + flange_thickness + fillet_radius),
                (web_thickness * 0.5, outer_height * 0.5 - flange_thickness - fillet_radius),
            ]
        )

        segment6 = self.create_circle(
            center=(fillet_radius + web_thickness * 0.5, outer_height * 0.5 - flange_thickness - fillet_radius),
            radius=fillet_radius,
            degree=90,
            direction=(0, 1)
        )

        segment7 = self.create_polyline(
            pts=[

            ]
        )