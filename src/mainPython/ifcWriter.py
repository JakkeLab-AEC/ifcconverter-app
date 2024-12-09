from typing import Literal
from typing import Optional
import math
import networkx as nx
import matplotlib.pyplot as plt

import json


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
from bpy import context
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
    def __init__(self, schema: Literal["IFC4","IFC2x3"]="IFC2x3", userinfo: dict[str, str]=defaultUserInfo, orginaizationInfo: dict[str, str]=defaultOrganizationInfo, project_name: str="Default Project", site_name: str="Default Site", building_name: str="Default Building"):
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

        # Add context, body
        context = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context)

        # Save properties
        self.model = model
        self.project = project
        self.units = units
        self.site = site
        self.building = building
        self.context = context
        self.body = body
        self.users: dict[str, UserData] = {
            registered_person.identification: registered_person
        }
        self.storeys = {}
        self.elements = {}
        self.material_sets: dict[str, entity_instance] = {}
        self.materials = {}
        self.element_types: dict[str, dict[str, dict[str, any]]] = {
            "wall_types" : {},
            "column_types" : {},
        }
        self.styles = {}
        self.profiles: dict[str, entity_instance] = {}

    @property
    def get_site(self) -> entity_instance:
        """
        Access the IfcSite entity.

        :return: The IfcSite entity instance.
        """
        return self.site

    @property
    def get_building(self) -> entity_instance:
        """
        Access the IfcBuilding entity.

        :return: The IfcBuilding entity instance.
        """
        return self.building

    @property
    def get_context(self) -> entity_instance:
        return self.context

    @property
    def get_body(self) -> entity_instance:
        return self.body

    # Storey
    def create_storey(self, storey_name: str, elevation: float) -> entity_instance:
        """
        Create a single storey (IfcBuildingStorey) with a specified name and elevation.

        :param storey_name: Name of the storey (must be unique).
        :param elevation: Elevation (height) of the storey in the building's coordinate system.
        :return: The created IfcBuildingStorey entity instance.

        - Updates the building's aggregated storeys.
        - Raises a ValueError if the storey name already exists in the project.
        """
        if storey_name in self.elements.keys():
            raise ValueError(f'Duplication Error : Storey named "{storey_name}" already exist on the project.')

        storey = ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcBuildingStorey", name=storey_name)
        storey.Elevation = elevation

        existing_storeys = []
        for rel in self.model.by_type("IfcRelAggregates"):
            if rel.RelatingObject == self.building:
                existing_storeys.extend(obj for obj in rel.RelatedObjects if obj.is_a("IfcBuildingStorey"))

        # Add new storey
        updated_storeys = existing_storeys + [storey]
        ifcopenshell.api.aggregate.assign_object(self.model, relating_object=self.building, products=updated_storeys)

        # Update writer
        self.storeys[storey_name] = storey
        return storey

    def create_storeys(self, storey_definitions: dict[str, float]) -> dict[str, entity_instance]:
        """
        Create multiple storeys based on a dictionary of definitions.

        :param storey_definitions: A dictionary where:
                                   - Keys are storey names (str).
                                   - Values are elevations (float).
                                   Example: {"Ground Floor": 0.0, "First Floor": 3.0}.
        :return: A dictionary with storey names as keys and IfcBuildingStorey instances as values.

        - Calls `create_storey` for each entry in the dictionary.
        - Skips storeys with duplicate names and logs the error.
        """
        created_storeys = {}

        for storey_name, elevation in storey_definitions.items():
            try:
                # Create each storey using the existing create_storey method
                storey = self.create_storey(storey_name=storey_name, elevation=elevation)
                created_storeys[storey_name] = storey
            except ValueError as e:
                print(f"Error: {e} (Skipped {storey_name})")

        return created_storeys

    # Material
    def define_material(self, material_name: str, rgba: dict[str, float]=None,  material_description: str=None, material_category: str=None)->entity_instance:
        if material_name in self.materials.keys():
            raise ValueError(f"Material named {material_name} is already exist.")

        material = ifcopenshell.api.material.add_material(
            self.model,
            name=material_name,
            category=material_category,
            description=material_description
        ) if self.schema == "IFC4" else ifcopenshell.api.material.add_material(
            self.model,
            name=material_name
        )

        style = ifcopenshell.api.style.add_style(self.model, name=material_name)

        if rgba is None:
            rgba = {'r': 128, 'g': 128, 'b': 128, 'a': 1}
        elif 'r' not in rgba.keys() and 'g' not in rgba.keys() and 'b' not in rgba.keys():
            ValueError("The parameter rgba should contain 'r', 'g', 'b' values as float type.")

        style_attribute = {
            "SurfaceColour": { "Name": f"SRF_{material_name}", "Red": rgba['r']/255, "Green": rgba['g']/255, "Blue": rgba['b']/255 },
        }

        if self.schema == 'IFC4' and 'a' in rgba.keys():
            style_attribute["Transparency"] = rgba['a']

        ifcopenshell.api.style.add_surface_style(
            self.model,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes=style_attribute
        )

        ifcopenshell.api.style.assign_material_style(self.model, material=material, style=style, context=self.body)
        self.styles[material_name] = style
        self.materials[material_name] = material

        return material

    def define_material_set(self, name: str, layers: list[dict[str, str|float]]) -> dict[str, any]:
        if name in self.material_sets.keys():
            raise ValueError(f"Duplication Error : Material set named '{name}' is already exist.")

        material_set = ifcopenshell.api.material.add_material_set(self.model, name=name, set_type="IfcMaterialLayerSet")

        total_thickness = 0
        for layer_prop in layers:
            if layer_prop['MaterialName'] not in self.materials.keys():
                raise ValueError(f"Invalid Value Error : Material named '{layer_prop['MaterialName']}' is not defined.")
            if layer_prop['LayerThickness'] is None:
                raise ValueError(f"Invalid Value Error : LayerThickness is not given.")

            material = self.materials[layer_prop['MaterialName']]
            thickness = layer_prop['LayerThickness']
            layer = ifcopenshell.api.material.add_layer(self.model, layer_set=material_set, material=material)
            ifcopenshell.api.material.edit_layer(self.model, layer=layer, attributes={"LayerThickness": thickness})
            total_thickness += thickness

        self.material_sets[name] = material_set
        return {"MaterialSet": material_set, "TotalThickness": total_thickness}

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

    def define_col_type(
        self,
        name: str,
        dimension_arg: dict[str, float]
        ) -> entity_instance:
        """
        Define an IfcColumnType with an IShape profile.
        """
        # Create IfcIShapeProfileDef
        profile = self.model.create_entity(
            type="IfcIShapeProfileDef",
            ProfileName=name,
            ProfileType="AREA",
            OverallWidth=dimension_arg['w'],
            OverallDepth=dimension_arg['h'],
            WebThickness=dimension_arg['tw'],
            FlangeThickness=dimension_arg['tf'],
            FilletRadius=dimension_arg['r']
        )

        # Create axis placement
        axis_placement = self.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=self.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Axis=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

        # Create extruded solid
        extruded_solid = self.model.create_entity(
            type="IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=axis_placement,
            ExtrudedDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            Depth=3.0
        )

        # Create shape representation
        shape_representation = self.model.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=self.model.by_type("IfcGeometricRepresentationContext")[0],
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )

        # Create representation map
        representation_map = self.model.create_entity(
            type="IfcRepresentationMap",
            MappingOrigin=axis_placement,
            MappedRepresentation=shape_representation
        )

        # Create IfcColumnType
        column_type = self.model.create_entity(
            type="IfcColumnType",
            OwnerHistory=self.model.by_type("IFCOWNERHISTORY")[0],
            GlobalId=ifcopenshell.guid.new(),
            Name=name,
            RepresentationMaps=[representation_map],
            PredefinedType="COLUMN"
        )

        # Save in element_types for reuse
        self.element_types['column_types'][name] = {"Entity": column_type, "Profile": profile}
        return column_type

    def create_object_placement(
            self,
            coordinates: tuple[float, float, float],
            placement_rel_to: Optional[entity_instance] = None
        ) -> entity_instance:
        """
        Create an IfcLocalPlacement.
        """
        cartesian_point = self.model.create_entity(
            type="IfcCartesianPoint",
            Coordinates=coordinates
        )

        axis_placement = self.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=cartesian_point,
            Axis=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

        local_placement = self.model.create_entity(
            type="IfcLocalPlacement",
            PlacementRelTo=placement_rel_to,  # Optionally relate to a parent placement
            RelativePlacement=axis_placement
        )

        return local_placement

    def create_representation(
            self,
            profile: entity_instance,
            extrusion_depth: float
        ) -> entity_instance:
        """
        Create an IfcProductDefinitionShape for a column.
        """
        axis_placement = self.model.create_entity(
            type="IfcAxis2Placement3D",
            Location=self.model.create_entity(type="IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Axis=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            RefDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
        )

        extruded_solid = self.model.create_entity(
            type="IfcExtrudedAreaSolid",
            SweptArea=profile,
            Position=axis_placement,
            ExtrudedDirection=self.model.create_entity(type="IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
            Depth=extrusion_depth
        )

        shape_representation = self.model.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=self.model.by_type("IfcGeometricRepresentationContext")[0],
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[extruded_solid]
        )

        product_definition_shape = self.model.create_entity(
            type="IfcProductDefinitionShape",
            Representations=[shape_representation]
        )

        return product_definition_shape

    def assign_to_spatial_structure(self, column: entity_instance, storey: entity_instance):
        """
        Assigns the column to a specific building storey.
        """
        self.model.create_entity(
            type="IfcRelContainedInSpatialStructure",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            RelatedElements=[column],
            RelatingStructure=storey
        )

    def relate_to_column_type(self, column: entity_instance, column_type: entity_instance):
        """
        Relates the column to its type definition (IfcColumnType).
        """
        self.model.create_entity(
            type="IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            RelatedObjects=[column],
            RelatingType=column_type
        )

    def add_column_properties(self, column: entity_instance):
        """
        Adds common property sets to the column.
        """
        # is_external = self.model.create_entity(
        #     type="IfcPropertySingleValue",
        #     Name="IsExternal",
        #     NominalValue=self.model.create_entity(type="IfcBoolean", value=False)
        # )
        #
        # load_bearing = self.model.create_entity(
        #     type="IfcPropertySingleValue",
        #     Name="LoadBearing",
        #     NominalValue=self.model.create_entity(type="IfcBoolean", value=True)
        # )

        property_set = self.model.create_entity(
            type="IfcPropertySet",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            Name="Pset_ColumnCommon",
            # HasProperties=[is_external, load_bearing]
        )

        self.model.create_entity(
            type="IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            RelatedObjects=[column],
            RelatingPropertyDefinition=property_set
        )

    def create_column(
        self,
        column_type_name: str,
        placement_coordinates: tuple[float, float, float],
        extrusion_depth: float,
        storey: entity_instance
    ) -> entity_instance:
        """
        Create an IfcColumn and relate it to a specific IfcColumnType.
        """
        # Validate column type existence
        if column_type_name not in self.element_types['column_types'].keys():
            raise ValueError(f"Not Exist Error : Column type '{column_type_name}' does not exist.")

        column_type = self.element_types['column_types'][column_type_name]['Entity']
        profile = self.element_types['column_types'][column_type_name]['Profile']

        # Create object placement
        object_placement = self.create_object_placement(
            coordinates=placement_coordinates,
            placement_rel_to=storey.ObjectPlacement  # Relate to the storey's placement
        )

        # Create representation
        representation = self.create_representation(
            profile=profile,
            extrusion_depth=extrusion_depth
        )

        # Create IfcColumn
        column = self.model.create_entity(
            type="IfcColumn",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=self.model.by_type("IfcOwnerHistory")[0],
            ObjectPlacement=object_placement,
            Representation=representation,
            ObjectType=column_type_name
        )

        # Assign column to spatial structure
        self.assign_to_spatial_structure(column, storey)

        # Relate column to its type
        self.relate_to_column_type(column, column_type)

        # Add common properties
        # self.add_column_properties(column)

        return column

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}"),
