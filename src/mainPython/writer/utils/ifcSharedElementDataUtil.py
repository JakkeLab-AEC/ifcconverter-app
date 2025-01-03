import math

from ifcopenshell import entity_instance
import ifcopenshell.guid
import ifcopenshell.util.selector
from src.mainPython.writer.ifcWriter import IfcWriter
from .simpleVectorUtils import SimpleVectorUtil

class IfcSharedElementDataUtil:
    def __init__(self, ifc_writer: IfcWriter):
        self.writer = ifc_writer

    def create_column(
        self,
        profile_name: str,
        col_type_name: str,
        target_storey_name: str,
        coordinate: tuple[float, float],
        height: float = 2.,
        rotation_degree: float = 0.,
        base_offset: float = 0.,
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

        sub_context = self.writer.sub_context_body

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
            self.writer.element_types["column_types"][col_type_name] = {
                "Entity": column_type
            }

        # Create column's Placement
        radian = -math.radians(rotation_degree)
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
            owner_history=self.writer.owner_history
        )

        # Create RelDefinesByType
        self.writer.ifcResourceEntityUtil.create_rel_defines_by_type(
            name=col_type_name,
            related_objects=[column],
            relating_type=column_type
        )

        return column

    def create_beam(
        self,
        profile_name: str,
        beam_type_name: str,
        target_storey_name: str,
        pt_start: tuple[float, float],
        pt_end: tuple[float, float],
        rotation_degree: float = 0.,
        z_offset: float = 0.,
        profile_arg: dict[str, float]|None = None
    ) -> entity_instance:
        if profile_name in self.writer.profiles.keys():
            profile = self.writer.profiles[profile_name]
        else:
            profile = self.writer.ifcResourceEntityUtil.create_I_shape_beam_profile(
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


        vector_util = SimpleVectorUtil()
        distance = vector_util.vector_size(vector_util.vector_subtract(pt_end, pt_start))

        #region Production Definition Shape
        extruded_solid = self.writer.ifcResourceEntityUtil.create_extruded_area_solid_beam(
            swept_area=profile,
            depth=distance,
            extruded_direction=self.writer.axis_x_3d_neg,
            rotation_degree=rotation_degree
        )

        body_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_body,
            representation_identifier="Body",
            representation_type="SweptSolid",
            items=[extruded_solid],
        )

        axis_polyline = self.writer.ifcResourceEntityUtil.create_polyline(
            pts =[
                (0., 0.),
                (distance, 0.)
            ]
        )

        axis_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_axis,
            representation_identifier="Axis",
            representation_type="Curve2D",
            items=[axis_polyline],
        )

        # endregion

        product_definition_shape = self.writer.ifcResourceEntityUtil.create_product_define_shape(
            representations=[axis_representation, body_representation],
        )

        #region Placement
        pt_start_position = self.writer.ifcResourceEntityUtil.create_cartesian_point_3d(
            coordinate=(pt_start[0], pt_start[1], z_offset)
        )

        vector_direction = vector_util.vector_normalize(vector_util.vector_subtract(pt_end, pt_start))
        direction = self.writer.ifcResourceEntityUtil.create_direction_3d((vector_direction[0], vector_direction[1], 0.))

        relative_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location = pt_start_position,
            axis = self.writer.axis_z,
            ref_direction=direction
        )

        object_placement = self.writer.ifcResourceEntityUtil.create_local_placement(
            placement_rel_to=target_storey["ObjectPlacement"],
            relative_placement=relative_placement
        )

        #endregion

        #region Define beam type
        if beam_type_name in self.writer.element_types['beam_types'].keys():
            beam_type = self.writer.element_types['beam_types'][beam_type_name]['Entity']
        else:
            beam_type = self.writer.model.create_entity(
                type="IfcBeamType",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=self.writer.owner_history,
                Name=beam_type_name,
                PredefinedType="BEAM"
            )
            self.writer.element_types['beam_types'][beam_type_name] = {
                'Entity' : beam_type
            }
        #endregion

        beam = self.writer.model.create_entity(
            type="IfcBeam",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            Name=beam_type_name,
            ObjectType=beam_type_name,
            ObjectPlacement=object_placement,
            Representation=product_definition_shape
        )

        # Create RelContainedSpatialStructure
        self.writer.ifcCoreDataUtil.create_rel_contained_in_spatial_structure(
            related_elements=[beam],
            relating_structure=target_storey["Entity"],
            owner_history=self.writer.owner_history,
        )

        # Create RelDefinesByType
        self.writer.ifcResourceEntityUtil.create_rel_defines_by_type(
            name=beam_type_name,
            related_objects=[beam],
            relating_type=beam_type
        )

        return beam

    def create_ea_double(
        self,
        target_storey_name: str,
        pt: tuple[float, float],
        z_offset: float,
        rotation_degree: float,
        dipping_degree: float,
        dipping_fixed: float,
        dipping_free: float,
        wale_width: float,
        wale_height: float
    ) -> entity_instance:
        # Select storey
        if target_storey_name not in self.writer.storeys.keys():
            raise ValueError(f"Not Exist Error: Storey f'{target_storey_name}' does not exist.")

        target_storey = self.writer.storeys[target_storey_name]

        # region Create Extruded area solids
        if "CIRCLE_RADIUS_120" not in self.writer.profiles.keys():
            position = self.writer.ifcResourceEntityUtil.create_axis2placement_2d(
                location=self.writer.origin2d,
                ref_direction=self.writer.axis_x_2d
            )

            circle_profile = self.writer.model.create_entity(
                type="IfcCircleProfileDef",
                ProfileType="AREA",
                ProfileName="CIRCLE_RADIUS_120",
                Position=position,
                Radius=0.12,
            )

            self.writer.profiles["CIRCLE_RADIUS_120"] = circle_profile
        else:
            circle_profile = self.writer.profiles["CIRCLE_RADIUS_120"]

        extrusion_position = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.ifcResourceEntityUtil.create_cartesian_point_3d((0., 0., -dipping_fixed)),
            axis=self.writer.axis_z,
            ref_direction=self.writer.axis_x_3d_neg
        )

        self.writer.model.create_entity(
            type="IfcExtrudedAreaSolid",
            SweptArea=circle_profile,
            ExtrudedDirection=self.writer.axis_z,
            Position=extrusion_position,
            Depth=dipping_fixed
        )

        # endregion

        # region Create Representation
        mapped_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_body,
            representation_identifier="Body",
            representation_type="Brep",
            items=[]
        )

        mapping_source = self.writer.ifcResourceEntityUtil.create_representation_map(
            mapped_representation=mapped_representation,
            mapping_origin=self.writer.ifcResourceEntityUtil.create_axis2placement_3d(location=self.writer.origin3d),
        )

        mapping_target = self.writer.ifcResourceEntityUtil.create_cartesian_transformation_operator3d()

        mapped_item = self.writer.model.create_entity(
            type="IfcMappedItem",
            MappingSource=mapping_source,
            MappingTarget=mapping_target
        )
        # endregion

        # region Create Element Type
        ea_double_name = f"EA_DOUBLE_{dipping_free}-{dipping_fixed}-{dipping_degree}"
        self.writer.model.create_entity(
            type="IfcBuildingElementProxyType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            Name=ea_double_name,
            RepresentationMaps=[mapped_item]
        )

        # endregion

        # region Create object placement entity
        radian = math.radians(rotation_degree)
        relative_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.ifcResourceEntityUtil.create_cartesian_point_3d(pt[0], pt[1], z_offset),
            axis=self.writer.axis_z,
            ref_direction=self.writer.ifcResourceEntityUtil.create_direction_3d(
                (math.cos(radian), math.sin(radian), 0.0))
        )

        object_placement = self.writer.ifcResourceEntityUtil.create_local_placement(
            placement_rel_to=target_storey["ObjectPlacement"],
            relative_placement=relative_placement
        )
        # endregion

        # Create Element
        self.writer.model.create_entity(
            type="IfcBuildingElementProxy",
            GlobalId = ifcopenshell.guid.new(),
            OwnerHistory = self.writer.owner_history,
            ObjectPlacement=object_placement,
        )

    def test_extrusion(self):
        model = self.writer.model
        owner_history = self.writer.owner_history
        radian = math.radians(60)
        depth = 5.
        target_storey = self.writer.storeys["1F"]
        radius=0.1
        type_name = "TestType_01"
        coordinate = self.writer.ifcResourceEntityUtil.create_cartesian_point_3d(coordinate=(1., 1., 1.))

        # Create object placement
        entity_point = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.origin3d
        )

        entity_placement = self.writer.ifcResourceEntityUtil.create_local_placement(
            placement_rel_to=target_storey['ObjectPlacement'],
            relative_placement=entity_point,
        )

        extrusion_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=coordinate,
            axis=self.writer.ifcResourceEntityUtil.create_direction_3d(coordinate=(0., -math.sin(radian), math.cos(radian))),
            ref_direction=self.writer.ifcResourceEntityUtil.create_direction_3d(coordinate=(0., -math.cos(radian), -math.sin(radian)))
        )

        # Create Profiles
        profile_position=self.writer.ifcResourceEntityUtil.create_axis2placement_2d(
            location=self.writer.origin2d,
            ref_direction=self.writer.axis_x_2d
        )

        profile_name="R10"
        if profile_name in self.writer.profiles.keys():
            profile_circle = self.writer.profiles[profile_name]
        else:
            profile_circle = model.create_entity(
                type="IfcCircleProfileDef",
                ProfileType="AREA",
                ProfileName=profile_name,
                Position=profile_position,
                Radius=radius
            )
            self.writer.profiles[profile_name] = profile_circle

        extrusion = model.create_entity(
            type="IfcExtrudedAreaSolid",
            Depth=depth,
            ExtrudedDirection=self.writer.axis_z,
            Position=extrusion_placement,
            SweptArea=profile_circle
        )

        extrusions = self.create_ea_double_solid(
            host_wale_b=0.3,
            host_wale_d=0.3,
            dipping_degree=30,
            len_free=6.,
            len_fixed=5.
        )

        brep_items = extrusions

        # region Mapping items
        mapped_representation=self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_body,
            representation_identifier="Body",
            representation_type="Brep",
            items=brep_items
        )

        mapping_origin = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.origin3d
        )

        mapping_source = self.writer.ifcResourceEntityUtil.create_representation_map(
            mapping_origin=mapping_origin,
            mapped_representation=mapped_representation
        )

        mapping_target = self.writer.ifcResourceEntityUtil.create_cartesian_transformation_operator3d(
            scale=1.0,
            local_origin=self.writer.origin3d
        )

        mapped_item = self.writer.ifcResourceEntityUtil.create_mapped_item(
            mapping_target=mapping_target,
            mapping_source=mapping_source
        )

        shape_representation = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_body,
            representation_type="MappedRepresentation",
            representation_identifier="Body",
            items=[mapped_item]
        )

        product_definition_shape = self.writer.ifcResourceEntityUtil.create_product_define_shape(
            representations=[shape_representation]
        )

        # endregion

        # Create proxy element
        entity = model.create_entity(
            type="IfcBuildingElementProxy",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            ObjectPlacement=entity_placement,
            Representation=product_definition_shape
        )

        entity_type = model.create_entity(
            type="IfcBuildingElementProxyType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner_history,
            Name=type_name,
            PredefinedType="NOTDEFINED",
            RepresentationMaps=[mapped_item]
        )

        self.writer.ifcResourceEntityUtil.create_rel_defines_by_type(
            name=type_name,
            related_objects=[entity],
            relating_type=entity_type
        )

        #Assign storey
        self.writer.ifcCoreDataUtil.create_rel_contained_in_spatial_structure(
            related_elements=[entity],
            relating_structure=target_storey['Entity'],
            owner_history=owner_history,
        )

    def create_ea_double_solid(
        self,
        host_wale_b: float,
        host_wale_d: float,
        dipping_degree: float,
        len_free: float,
        len_fixed: float
    ) -> list[entity_instance]:
        model = self.writer.model
        converted_degree = 90 - dipping_degree
        dipping_radian = math.radians(90 - converted_degree)

        extrusions = []

        # region Extrusion dipping
        p_free_start = 0.5 * host_wale_d + 0.5 * host_wale_b * math.tan(dipping_radian)
        p_free_extrusion_start = p_free_start + len_free
        p_fixed_extrusion_start = p_free_start + len_free + len_fixed

        p_free_extrusion_start_vec = (p_free_extrusion_start * math.cos(dipping_radian), -p_free_extrusion_start * math.sin(dipping_radian))
        p_fixed_extrusion_start_vec = (p_fixed_extrusion_start * math.cos(dipping_radian), -p_fixed_extrusion_start * math.sin(dipping_radian))

        profile_name_dipping = "R10"
        if profile_name_dipping in self.writer.profiles.keys():
            profile_circle = self.writer.profiles[profile_name_dipping]
        else:
            profile_position = self.writer.ifcResourceEntityUtil.create_axis2placement_2d(
                location=self.writer.origin2d,
                ref_direction=self.writer.axis_x_2d
            )

            radius = 0.1

            profile_circle = model.create_entity(
                type="IfcCircleProfileDef",
                ProfileType="AREA",
                ProfileName=profile_name_dipping,
                Position=profile_position,
                Radius=radius
            )
            self.writer.profiles[profile_name_dipping] = profile_circle

        dipping_free = self.create_extrusion_plane_xz(
            point=p_free_extrusion_start_vec,
            rotation_degree=converted_degree,
            profile=profile_circle,
            depth=len_free
        )

        dipping_fixed = self.create_extrusion_plane_xz(
            point=p_fixed_extrusion_start_vec,
            rotation_degree=converted_degree,
            profile=profile_circle,
            depth=len_fixed
        )
        extrusions.append(dipping_free)
        extrusions.append(dipping_fixed)
        # endregion

        # region Extrusion plate
        plate_height = 0.3
        profile_name_plate="RECT_280x300"
        plate_thickness = 0.01
        if profile_name_plate in self.writer.profiles.keys():
            profile_plate = self.writer.profiles[profile_name_plate]
        else:
            profile_position = self.writer.ifcResourceEntityUtil.create_axis2placement_2d(
                location=self.writer.origin2d,
                ref_direction=self.writer.axis_x_2d
            )

            profile_plate = model.create_entity(
                type="IfcRectangleProfileDef",
                ProfileType="AREA",
                ProfileName=profile_name_plate,
                Position=profile_position,
                XDim=0.28,
                YDim=plate_height
            )
            self.writer.profiles[profile_name_plate] = profile_plate

        plate_start_dist = 0.5 * plate_height * math.tan(dipping_radian) + 0.5 * host_wale_d / math.cos(dipping_radian)
        plate_start_vector=(-plate_start_dist * math.cos(dipping_radian), plate_start_dist*math.sin(dipping_radian))
        plate = self.create_extrusion_plane_xz(
            point=plate_start_vector,
            rotation_degree=converted_degree,
            profile=profile_plate,
            depth=plate_thickness
        )
        extrusions.append(plate)
        # endregion

        # region Extrusion cap
        profile_name_cap = "C_R120"
        cap_radius = 0.12
        cap_depth = 0.12
        if profile_name_cap in self.writer.profiles.keys():
            profile_cap = self.writer.profiles[profile_name_cap]
        else:
            profile_position = self.writer.ifcResourceEntityUtil.create_axis2placement_2d(
                location=self.writer.origin2d,
                ref_direction=self.writer.axis_x_2d
            )

            radius = cap_radius

            profile_cap = model.create_entity(
                type="IfcCircleProfileDef",
                ProfileType="AREA",
                ProfileName=profile_name_cap,
                Position=profile_position,
                Radius=radius,
            )
            self.writer.profiles[profile_name_dipping] = profile_circle

        cap_start_dist = plate_start_dist + plate_thickness
        cap_start_vector = (-cap_start_dist * math.cos(dipping_radian), cap_start_dist * math.sin(dipping_radian))
        extrusion_cap = self.create_extrusion_plane_xz(
            point=cap_start_vector,
            rotation_degree=converted_degree,
            profile=profile_cap,
            depth=cap_depth
        )
        extrusions.append(extrusion_cap)
        # endregion

        # region Extra rebar
        profile_rebar = self.create_extra_rebar_profiles()
        rebar_start_dist = cap_start_dist + cap_depth
        rebar_length = 0.3
        rebar_start_vector = (-rebar_start_dist * math.cos(dipping_radian), rebar_start_dist * math.sin(dipping_radian))

        extrusion_rebars = []
        for profile in profile_rebar:
            extrusion_rebar = self.create_extrusion_plane_xz(
                point=rebar_start_vector,
                rotation_degree=converted_degree,
                profile=profile,
                depth=rebar_length
            )
            extrusions.append(extrusion_rebar)
        # endregion

        return extrusions

    def create_extrusion_plane_xz(
        self,
        point: tuple[float, float],
        rotation_degree: float,
        profile: entity_instance,
        depth: float
    ) -> entity_instance:
        model = self.writer.model
        coordinate = self.writer.ifcResourceEntityUtil.create_cartesian_point_3d(coordinate=(point[0], 0., point[1]))
        radian = math.radians(rotation_degree)

        extrusion_placement = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=coordinate,
            axis=self.writer.ifcResourceEntityUtil.create_direction_3d(
                coordinate=(-math.sin(radian), 0., math.cos(radian))),
            ref_direction=self.writer.ifcResourceEntityUtil.create_direction_3d(
                coordinate=(-math.cos(radian), 0., -math.sin(radian)))
        )

        extrusion = model.create_entity(
            type="IfcExtrudedAreaSolid",
            Depth=depth,
            ExtrudedDirection=self.writer.axis_z,
            Position=extrusion_placement,
            SweptArea=profile
        )

        return extrusion

    def create_extra_rebar_profiles(
        self,
    ) -> [entity_instance]:
        profile_names = ["PROF_Rebar_1", "PROF_Rebar_2", "PROF_Rebar_3", "PROF_Rebar_4"]
        profile_name_header = "PROF_Rebar"
        model = self.writer.model
        pitch = 0.085
        rebar_thickness = 0.0115
        profiles: list[entity_instance] = []

        if set(profile_names).issubset(self.writer.profiles.keys()):
            profiles = [self.writer.profiles[profile_name] for profile_name in profile_names]
        else:
            circle_centers = [
                (-0.5 * pitch, -0.5 * pitch),
                (0.5 * pitch, -0.5 * pitch),
                (0.5 * pitch, 0.5 * pitch),
                (-0.5 * pitch, 0.5 * pitch),
            ]
            radius = rebar_thickness  # Radius of each circle

            i = 1
            for center in circle_centers:
                # Create the profile for each circle
                profile_name = f"{profile_name_header}_{i}"
                placement = model.create_entity(
                    "IfcAxis2Placement2D",
                    Location=model.create_entity("IfcCartesianPoint", Coordinates=center),
                )
                profile = model.create_entity(
                    "IfcCircleProfileDef",
                    ProfileType="AREA",
                    Radius=radius,
                    Position=placement,
                    ProfileName=profile_name
                )

                self.writer.profiles[profile_name] = profile
                i += 1
                profiles.append(profile)

        return profiles

    def create_wall(
        self,
        profile_name: str,
        wall_type_name: str,
        target_storey_name: str,
        pt_start: tuple[float, float],
        pt_end: tuple[float, float],
        z_offset: float = 0.,
        wall_thickness: float = 0.1,
        wall_height: float = 4.
    ) -> entity_instance:

        if target_storey_name not in self.writer.storeys.keys():
            raise ValueError(f"Not Exist Error: Storey f'{target_storey_name}' does not exist.")

        target_storey = self.writer.storeys[target_storey_name]

        vector_util = SimpleVectorUtil()
        wall_cen_vector = vector_util.vector_subtract(pt_end, pt_start)
        wall_length = vector_util.vector_size(wall_cen_vector)
        wall_cen_normalized = vector_util.vector_normalize(wall_cen_vector)

        if wall_type_name in self.writer.element_types['wall_types'].keys():
            wall_type = self.writer.element_types['wall_types'][wall_type_name]['Entity']
        else:
            wall_type = self.writer.model.create_entity(
                type="IfcWallType",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=self.writer.owner_history,
                Name=wall_type_name,
                PredefinedType="STANDARD"
            )

        if profile_name in self.writer.profiles.keys():
            profile = self.writer.profiles[profile_name]
        else:
            profile = self.writer.ifcResourceEntityUtil.create_rectangle_profile(
                profile_name=profile_name,
                x_dim=wall_length,
                y_dim=wall_thickness
            )

        #region Create extrusion
        extrusion_position = self.writer.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=self.writer.origin3d
        )

        extrusion_direction = self.writer.axis_z

        extrusion = self.writer.ifcResourceEntityUtil.create_extruded_area_solid_wall(
            swept_area=profile,
            extruded_direction=extrusion_direction,
            position=extrusion_position,
            depth=wall_height
        )

        shape_representation_extrusion = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_body,
            representation_identifier="Body",
            representation_type="SweptSolid",
            items=[extrusion]
        )
        #endregion

        #region Create axis shape
        axis_polyline = self.writer.ifcResourceEntityUtil.create_polyline(
            pts=[
                (0., 0.),
                (wall_length, 0.)
            ]
        )

        shape_representation_axis = self.writer.ifcResourceEntityUtil.create_shape_representation(
            context_of_items=self.writer.sub_context_axis,
            representation_type="Curve2D",
            representation_identifier="Axis",
            items=[axis_polyline]
        )
        #endregion

        representation = self.writer.ifcResourceEntityUtil.create_product_define_shape(
            representations=[shape_representation_axis, shape_representation_extrusion]
        )

        wall_position = self.writer.ifcResourceEntityUtil.create_axis2placement_3d(
            location=self.writer.ifcResourceEntityUtil.create_cartesian_point_3d(coordinate=(pt_start[0], pt_start[1], z_offset)),
            axis=self.writer.axis_z,
            ref_direction=self.writer.ifcResourceEntityUtil.create_direction_3d(coordinate=(wall_cen_normalized[0], wall_cen_normalized[1], 0.))
        )

        wall_placement = self.writer.ifcResourceEntityUtil.create_local_placement(
            placement_rel_to=target_storey['ObjectPlacement'],
            relative_placement=wall_position
        )

        wall = self.writer.model.create_entity(
            type="IfcWallStandardCase",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.writer.owner_history,
            Name=wall_type_name,
            ObjectType=wall_type_name,
            ObjectPlacement=wall_placement,
            Representation=representation
        )

        # Create RelContainedSpatialStructure
        self.writer.ifcCoreDataUtil.create_rel_contained_in_spatial_structure(
            related_elements=[wall],
            relating_structure=target_storey['Entity'],
            owner_history=self.writer.owner_history
        )

        self.writer.ifcResourceEntityUtil.create_rel_defines_by_type(
            name=wall_type_name,
            related_objects=[wall],
            relating_type=wall_type
        )

        # Apply material
        self.writer.ifcResourceEntityUtil.create_material(
            name=f"MAT_{wall_type_name}",
            rgba={"r": 128, "g": 128, "b": 128, "a": 0.5}
        )

        return wall

