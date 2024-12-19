from typing import Literal
import math

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.api.material
import ifcopenshell.api.style
import ifcopenshell.api.type
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.selector
import ifcopenshell.util.representation
from ifcopenshell import entity_instance

default_units = {
    "LENGTHUNIT": None,
    "AREAUNIT": None,
    "VOLUMEUNIT" : None,
}

predefined_styles = {
    'concrete':     {'r': 192, 'g': 192, 'b': 192, 'a': 1.0},       # Light gray for concrete
    'steel':        {'r': 150, 'g': 150, 'b': 150, 'a': 1.0},       # Dark gray for steel
    'aluminium':    {'r': 200, 'g': 200, 'b': 200, 'a': 1.0},       # Light metallic gray for aluminium
    'block':        {'r': 169, 'g': 169, 'b': 169, 'a': 1.0},       # Medium gray for block
    'brick':        {'r': 156, 'g': 90, 'b': 60, 'a': 1.0},         # Reddish-brown for brick
    'stone':        {'r': 120, 'g': 120, 'b': 120, 'a': 1.0},       # Medium-dark gray for stone
    'wood':         {'r': 139, 'g': 69, 'b': 19, 'a': 1.0},         # Brown for wood
    'glass':        {'r': 135, 'g': 206, 'b': 235, 'a': 0.3},       # Light blue and transparent for glass
    'gypsum':       {'r': 245, 'g': 245, 'b': 245, 'a': 1.0},       # Very light gray for gypsum
    'plastic':      {'r': 255, 'g': 255, 'b': 255, 'a': 1.0},       # White for plastic
    'earth':        {'r': 139, 'g': 115, 'b': 85, 'a': 1.0}         # Earthy brown for soil/earth
}

predefined_material_sets: dict[str, list[dict[str, str|float|list]]] = {
    "Wall": [
        {"name": "WA_CONC_100", "category": "concrete", "layer_type": "single", "thickness": 0.1},
    ],
    "Floor": [
        {"name": "FL_CONC_01", "category": "concrete", "layer_type": "single", "thickness": 0.1},
    ],
    "Column": [
        {"name": "COL_CONC_01", "category": "concrete", "layer_type": "single", "thickness": 0.1},
    ],
}

supported_units = [
    "ABSORBEDDOSEUNIT",
    "AMOUNTOFSUBSTANCEUNIT",
    "AREAUNIT",
    "DOSEEQUIVALENTUNIT",
    "ELECTRICCAPACITANCEUNIT",
    "ELECTRICCHARGEUNIT",
    "ELECTRICCONDUCTANCEUNIT",
    "ELECTRICCURRENTUNIT",
    "ELECTRICRESISTANCEUNIT",
    "ELECTRICVOLTAGEUNIT",
    "ENERGYUNIT",
    "FORCEUNIT",
    "FREQUENCYUNIT",
    "ILLUMINANCEUNIT",
    "INDUCTANCEUNIT",
    "LENGTHUNIT",
    "LUMINOUSFLUXUNIT",
    "LUMINOUSINTENSITYUNIT",
    "MAGNETICFLUXDENSITYUNIT",
    "MAGNETICFLUXUNIT",
    "MASSUNIT",
    "PLANEANGLEUNIT",
    "POWERUNIT",
    "PRESSUREUNIT",
    "RADIOACTIVITYUNIT",
    "SOLIDANGLEUNIT",
    "THERMODYNAMICTEMPERATUREUNIT",
    "TIMEUNIT",
    "VOLUMEUNIT"
]

supported_prefixes = [
    "ATTO",
    "CENTI",
    "DECA",
    "DECI",
    "EXA",
    "FEMTO",
    "GIGA",
    "HECTO",
    "KILO",
    "MEGA",
    "MICRO",
    "MILLI",
    "NANO",
    "PETA",
    "PICO",
    "TERA"
]

supported_material_categories = [
    'concrete',
    'steel',
    'aluminium',
    'block',
    'brick',
    'stone',
    'wood',
    'glass',
    'gypsum',
    'plastic',
    'earth'
]

defaultUserInfo = {
    "identification":"DefaultUserId",
    "family_name":"DefaultFamilyName",
    "given_name":"DefaultGivenName"
}

defaultOrganizationInfo = {
    "identification":"DefaultOrganzationId",
    "name": "DefaultOrganizationName"
}

def vector_rotate(vector: tuple[float, float], degree: float) -> tuple[float, float]:
    radian = degree * (math.pi/180)
    x = vector[0] * math.cos(radian) - vector[1] * math.sin(radian)
    y = vector[0] * math.sin(radian) + vector[1] * math.cos(radian)
    return x, y

def vector_normalize(vector: tuple[float, float]) -> tuple[float, float]:
    size = math.sqrt(vector[0]**2 + vector[1]**2)
    return vector[0]/size, vector[1]/size

def vector_add(v1: tuple[float, float], v2: tuple[float, float]):
    return v1[0] + v2[0], v1[1] + v2[1]

def vector_subtract(v1: tuple[float, float], v2: tuple[float, float]):
    return v1[0] - v2[0], v1[1] - v2[1]

def vector_multiply_scalar(vector: tuple[float, float], scalar: float) -> tuple[float, float]:
    return vector[0] * scalar, vector[1] * scalar

class UserData:
    def __init__(self, identification: str="DefaultUserId", family_name: str="DefaultFamilyName", given_name: str="DefaultGivenName"):
        self.identification = identification
        self.family_name = family_name
        self.given_name = given_name

class OrganizationData:
    def __init__(self, identification: str="DefaultOrganzationId", name: str="DefaultOrganizationName"):
        self.identification = identification
        self.name = name

class IfcWriter:
    def __init__(self, schema: Literal["IFC4","IFC2x3"]="IFC4", userinfo: dict[str, str]=defaultUserInfo, orginaizationInfo: dict[str, str]=defaultOrganizationInfo, project_name: str="Default Project", site_name: str="Default Site", building_name: str="Default Building"):
        """
        Initialize an IFC file with a project, site, and building.

        :param project_name: Name of the project. Defaults to "Default Project".
        :param site_name: Name of the site. Defaults to "Default Site".
        :param building_name: Name of the building. Defaults to "Default Building".

        - Creates an IFC2x3 file.
        - Defines project units (length, area, volume).
        - Sets up the basic hierarchy: Project -> Site -> Building.
        """
        model = ifcopenshell.api.project.create_file(version=schema)
        self.schema = schema

        # Import utils
        from utils.ifcResourceEntityUtils import IfcResourceEntityUtil
        from utils.ifcCoreDataUtils import IfcCoreDataUtil
        from utils.ifcSharedElementDataUtil import IfcSharedElementDataUtil

        ifcResourceEntityUtil = IfcResourceEntityUtil(self)
        self.ifcResourceEntityUtil = ifcResourceEntityUtil

        ifcCoreDataUtil = IfcCoreDataUtil(self)
        self.ifcCoreDataUtil = ifcCoreDataUtil

        ifcSharedElementDataUtil = IfcSharedElementDataUtil(self)
        self.ifcSharedElementDataUtil = ifcSharedElementDataUtil

        application = ifcopenshell.api.owner.add_application(model)

        #Owner setting
        if 'identification' not in userinfo.keys() or 'family_name' not in userinfo.keys() or 'given_name' not in userinfo.keys() :
            raise ValueError(f"User info should contain 'identification', 'family_name', 'given_name' values")

        if 'identification' not in orginaizationInfo.keys() or 'name' not in orginaizationInfo.keys():
            raise ValueError(f"Organization info should contain 'identification', 'name', values")

        person = ifcopenshell.api.owner.add_person(model, identification=userinfo['identification'], family_name=userinfo['family_name'], given_name=userinfo['given_name'])
        registered_person = UserData(userinfo['identification'], userinfo['family_name'], userinfo['given_name'])
        organization = ifcopenshell.api.owner.add_organisation(model, identification=orginaizationInfo['identification'], name=orginaizationInfo['name'])
        user = ifcopenshell.api.owner.add_person_and_organisation(model, person=person, organisation=organization)
        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name=project_name)

        ownerhistory = ifcopenshell.util.selector.filter_elements(model, "IfcOwnerHistory")
        self.owner_history = list(ownerhistory)[0]

        # Define Units
        units = default_units
        unit_instances = []
        for key in units.keys():
            if key not in supported_units:
                raise ValueError(f"Unsupported unit type: {key}")

            elif units[key] is None:
                unit = ifcopenshell.api.unit.add_si_unit(model, unit_type=key)
                unit_instances.append(unit)

            else:
                if units[key] in supported_prefixes:
                    unit = ifcopenshell.api.unit.add_si_unit(model, unit_type=key, prefix=units[key])
                    unit_instances.append(unit)
                else:
                    unit = ifcopenshell.api.unit.add_si_unit(model, unit_type=key)
                    unit_instances.append(unit)

        ifcopenshell.api.unit.assign_unit(model, units=unit_instances)

        # Define site and building
        site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name=site_name)
        building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name=building_name)
        ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
        ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])


        # Save properties
        self.model = model
        self.project = project
        self.units = units
        self.site = site
        self.building = building
        self.users: dict[str, UserData] = {
            registered_person.identification: registered_person
        }

        self.storeys:dict[str, dict[str, any]] = {}
        self.elements = {}
        self.material_sets: dict[str, entity_instance] = {}
        self.materials: dict[str, dict[str: entity_instance]] = {}
        self.element_types: dict[str, dict[str, dict[str, any]]] = {
            "wall_types" : {},
            "column_types" : {},
            "beam_types" : {},
            "ea_single_types": {},
            "ea_double_types": {},
        }
        self.styles = {}
        self.profiles: dict[str, entity_instance] = {}
        self.geometric_representation_subContext: dict[str, entity_instance] = {}

        origin2d = ifcResourceEntityUtil.create_cartesian_point_2d((0., 0.))
        self.origin2d = origin2d

        origin3d = ifcResourceEntityUtil.create_cartesian_point_3d((0.0, 0.0, 0.0))
        self.origin3d = origin3d

        axis_z = ifcResourceEntityUtil.create_direction_3d((0., 0., 1.))
        self.axis_z = axis_z

        axis_z_neg = ifcResourceEntityUtil.create_direction_3d((0., 0., -1.))
        self.axis_z_neg = axis_z_neg

        axis_x_2d = ifcResourceEntityUtil.create_direction_2d((1., 0.))
        self.axis_x_2d = axis_x_2d

        axis_y_2d = ifcResourceEntityUtil.create_direction_2d((0., 1.))
        self.axis_y_2d = axis_y_2d

        axis_x_2d_neg = ifcResourceEntityUtil.create_direction_2d((-1., 0.))
        self.axis_x_2d_neg = axis_x_2d_neg

        axis_y_2d_neg = ifcResourceEntityUtil.create_direction_2d((0., -1.))
        self.axis_y_2d_neg = axis_y_2d_neg

        axis_x_3d = ifcResourceEntityUtil.create_direction_3d((1., 0., 0.))
        self.axis_x_3d = axis_x_3d

        axis_x_3d_neg = ifcResourceEntityUtil.create_direction_3d((-1., 0., 0.))
        self.axis_x_3d_neg = axis_x_3d_neg

        axis_y_3d = ifcResourceEntityUtil.create_direction_3d((0., 1., 0.))
        self.axis_y_3d = axis_y_3d

        # Define context, sub contexts
        context = ifcResourceEntityUtil.create_geometric_representation_context(
            coordinate_space_dimension=3,
            context_type="Model",
        )

        sub_context_axis = ifcResourceEntityUtil.create_geometric_representation_sub_context(
            parent_context=context,
            context_identifier="Axis",
            target_view="GRAPH_VIEW"
        )

        sub_context_body = ifcResourceEntityUtil.create_geometric_representation_sub_context(
            parent_context=context,
            context_identifier="Body",
            target_view="MODEL_VIEW"
        )

        sub_context_box = ifcResourceEntityUtil.create_geometric_representation_sub_context(
            parent_context=context,
            context_identifier="Box",
            target_view="MODEL_VIEW"
        )

        sub_context_footprint = ifcResourceEntityUtil.create_geometric_representation_sub_context(
            parent_context=context,
            context_identifier="FootPrint",
            target_view="MODEL_VIEW"
        )

        self.context = context
        self.sub_context_body = sub_context_body
        self.sub_context_axis = sub_context_axis
        self.sub_context_box = sub_context_box
        self.sub_context_footprint = sub_context_footprint

    def define_wall_type(
            self,
            name: str,
            material_layers: list[dict[str, str|float]],
            material_set_name: str,
            wall_type_description: str = None,
    ) -> entity_instance:
        # Validations
        if name in self.element_types['wall_types'].keys():
            raise ValueError(f'Duplication Error: Wall type named "{name}" already exists.')

        if material_set_name in self.material_sets:
            raise ValueError(f"Duplication Error: Material named '{material_set_name}' already exists.")

        if not all(
                isinstance(layer, dict) and 'MaterialName' in layer and 'LayerThickness' in layer
                for layer in material_layers
        ):
            raise ValueError("Each element in material_layers must contain 'MaterialName' and 'LayerThickness' keys.")

        # Define layers
        material_set_creation = self.define_material_set(material_set_name, material_layers)
        material_set: entity_instance = material_set_creation['MaterialSet']
        total_thickness: float = material_set_creation['TotalThickness']

        # Create the IfcWallType entity
        wall_type = {"entity" : ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcWallType", name=name), "thickness" : total_thickness}
        if wall_type_description:
            wall_type["entity"].Description = wall_type_description

        # Assign material to the wall type, if provided
        ifcopenshell.api.material.assign_material(self.model, products=[wall_type["entity"]], material=material_set)

        # Return the created wall type entity
        self.element_types['wall_types'][name] = wall_type
        return wall_type

    def create_wall(
        self,
        target_storey: str,
        p1: tuple[float, float],
        p2: tuple[float, float],
        elevation: float,
        height: float,
        wall_type_name: str
    ) -> entity_instance:
        if self.storeys[target_storey] is None:
            raise ValueError(f'The storey {target_storey} does not exist.')

        storey = self.storeys[target_storey]
        wall = ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcWall")

        # Assign wall type
        if wall_type_name not in self.element_types['wall_types']:
            raise ValueError(f'Wall type "{wall_type_name}" is not defined.')
        target_wall_type: entity_instance = self.element_types['wall_types'][wall_type_name]
        ifcopenshell.api.type.assign_type(self.model, related_objects=[wall], relating_type=target_wall_type['entity'])

        # Convert vector
        thickness = target_wall_type['thickness']
        direction = vector_normalize((p2[0] - p1[0], p2[1] - p1[1]))
        rotated_direction = vector_rotate(direction, degree=-90)
        converted_p1 = vector_add(p1, vector_multiply_scalar(rotated_direction, 0.5 * thickness))
        converted_p2 = vector_add(p2, vector_multiply_scalar(rotated_direction, 0.5 * thickness))

        # Create representation
        ifcopenshell.api.geometry.edit_object_placement(self.model, product=wall)
        representation = ifcopenshell.api.geometry.create_2pt_wall(
            self.model,
            element=wall,
            context=self.context,
            p1=converted_p1,
            p2=converted_p2,
            elevation=elevation,
            height=height,
            thickness=thickness
        )

        # Validate geometry representation creation
        if representation is None:
            raise RuntimeError("Failed to create a geometric representation for the wall.")

        ifcopenshell.api.geometry.assign_representation(self.model, product=wall, representation=representation)
        ifcopenshell.api.spatial.assign_container(self.model, relating_structure=storey, products=[wall])

        return wall

    def query_test(self):
        query = "IfcBuildingStorey"
        filtered_elements = list(ifcopenshell.util.selector.filter_elements(self.model, query=query))
        result_dict = {item.Name: item for item in filtered_elements}

        return result_dict

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}"),
