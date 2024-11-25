from typing import Literal

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
from ifcopenshell import entity_instance

default_units = {
    "LENGTHUNIT": None,     #
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

class IfcWriter:
    def __init__(self, project_name: str="Default Project", site_name: str="Default Site", building_name: str="Default Building"):
        """
        Initialize an IFC file with a project, site, and building.

        :param project_name: Name of the project. Defaults to "Default Project".
        :param site_name: Name of the site. Defaults to "Default Site".
        :param building_name: Name of the building. Defaults to "Default Building".

        - Creates an IFC4 file.
        - Defines project units (length, area, volume).
        - Sets up the basic hierarchy: Project -> Site -> Building.
        """

        model = ifcopenshell.api.project.create_file(version="IFC4")
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
        self.storeys = {}
        self.elements = {}
        self.materials = {}
        self.element_types: dict[str, dict[str, entity_instance]] = {
            "wall_types" : {},
        }

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
    def define_material(self, material_name: str, material_description: str = None, material_category: str = "concrete", rgba: dict[str, float] = None) -> entity_instance:
        """
        Define a material with optional surface style (color) and assign it to the project.

        :param material_name: The name of the material (must be unique within the project).
                              Example: "Concrete"
        :param material_description: An optional description for the material.
                                     Example: "Strong and durable material"
        :param material_category: The category of the material (e.g., "concrete", "steel").
                                  Must be one of the supported categories in `supported_material_categories`.
                                  Defaults to "concrete".
        :param rgba: A dictionary containing RGBA values for the material's color.
                     Example: {"r": 192, "g": 192, "b": 192, "a": 1.0}
                     If not provided, a predefined color from `predefined_styles` for the given category is used.
        :return: The created material entity instance.

        :raises ValueError:
            - If the material name already exists in the project.
            - If the material category is not supported.
            - If the provided RGBA dictionary is invalid or missing required keys.

        Steps:\n
        1. Validate that the material name is unique and the category is supported.\n
        2. Create the material using `ifcopenshell.api.material.add_material`.\n
        3. Optionally, set a description for the material.\n
        4. Create and add a surface style (`IfcSurfaceStyleShading`) for the material:\n
        - Use the provided RGBA values if available.
        - Use a predefined style color for the category if RGBA is not provided.
        5. Assign the style to the material and add it to the project.\n
        6. Store the material in `self.materials` for future reference.\n
        """
        # Validation for preventing the duplication of material name and unsupported category name
        if material_name in self.materials.keys():
            raise ValueError(f'Duplication Error: Material named "{material_name}" already exists on the project.')

        if material_category not in supported_material_categories:
            raise ValueError(f'Unsupported Material Category: "{material_category}" is not supported.')

        # Creation of material
        material = ifcopenshell.api.material.add_material(self.model, name=material_name, category=material_category)
        if material_description:
            material.Description = material_description

        # Add style
        style = ifcopenshell.api.style.add_style(self.model)

        if rgba:
            # Validate RGBA dictionary if provided
            required_keys = {"r", "g", "b", "a"}
            if not all(key in rgba for key in required_keys):
                raise ValueError(f'Invalid RGBA: Missing one or more keys from {required_keys}. Received: {rgba}')

            # Add surface style with user-provided RGBA values
            ifcopenshell.api.style.add_surface_style(
                self.model,
                style=style,
                ifc_class="IfcSurfaceStyleShading",
                attributes={
                    "SurfaceColour": {
                        "Name": None,
                        "Red": rgba["r"] / 255.0,
                        "Green": rgba["g"] / 255.0,
                        "Blue": rgba["b"] / 255.0,
                    },
                    "Transparency": rgba['a'],  # Alpha is used directly for transparency
                }
            )
        else:
            # Use predefined color for the given category if RGBA is not provided
            predefined_style = predefined_styles[material_category]
            ifcopenshell.api.style.add_surface_style(
                self.model,
                style=style,
                ifc_class="IfcSurfaceStyleShading",
                attributes={
                    "SurfaceColour": {
                        "Name": None,
                        "Red": predefined_style["r"] / 255.0,
                        "Green": predefined_style["g"] / 255.0,
                        "Blue": predefined_style["b"] / 255.0,
                    },
                    "Transparency": predefined_style['a'],  # Predefined transparency
                }
            )

        # Assign the style to the material in the context of the model
        ifcopenshell.api.style.assign_material_style(self.model, material=material, style=style, context=self.body)

        # Store the material in the internal dictionary for future reference
        self.materials[material_name] = material

        # Return the created material instance
        return material

    def define_wall_type(
            self,
            wall_type_name: str,
            wall_type_description: str = None,
            material_name: str = None,
            thickness: float = None
    ) -> entity_instance:
        """
        Define an IfcWallType with optional properties and a linked material.

        :param wall_type_name: The name of the wall type (must be unique within the project).
                               Example: "Exterior Wall Type A"
        :param wall_type_description: An optional description for the wall type.
                                       Example: "High insulation for exterior walls."
        :param material_name: The name of the material to be linked to this wall type.
                              The material must already exist in `self.materials`.
                              Example: "Concrete"
        :param thickness: The thickness of the wall type in model units (e.g., meters).
                          Example: 0.2 for 200mm thickness.
        :return: The created IfcWallType entity instance.

        :raises ValueError:
            - If the wall type name already exists.
            - If the material name is provided but does not exist in `self.materials`.
            - If thickness is not provided (optional, depends on requirements).
        """
        # Validate that the wall type name is unique
        if wall_type_name in self.element_types['wall_types'].keys():
            raise ValueError(f'Duplication Error: Wall type named "{wall_type_name}" already exists.')

        # Validate that the material exists, if provided
        if material_name and material_name not in self.materials:
            raise ValueError(f'Material Error: Material named "{material_name}" does not exist.')

        # Validate that thickness is provided
        if thickness is None or thickness <= 0:
            raise ValueError(f'Invalid Thickness: Thickness must be greater than zero. Received: {thickness}')

        # Create the IfcWallType entity
        wall_type = ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcWallType", name=wall_type_name)
        if wall_type_description:
            wall_type.Description = wall_type_description

        # Assign material to the wall type, if provided
        if material_name:
            ifcopenshell.api.material.assign_material(
                self.model, products=[wall_type], material=self.materials[material_name]
            )

        # Add layer
        target_material = self.materials[material_name]
        material_set = ifcopenshell.api.material.add_material_set(self.model, name=f"MAT_LAYERSET_{wall_type_name}", set_type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(self.model, layer_set=material_set, material=target_material)
        ifcopenshell.api.material.edit_layer(self.model, layer=layer, attributes={"LayerThickness": thickness})

        # Store the wall type in the internal dictionary for future reference
        self.element_types['wall_types'][wall_type_name] = wall_type

        # Return the created wall type entity
        return wall_type

    def create_wall(self, target_storey: str, length: float, height: float, thickness: float=0.3,
                    wall_type_name: str = None) -> entity_instance:
        """
        Create a wall and assign it to a specific storey in the IFC model.

        :param target_storey: The name of the storey where the wall will be placed.
                              This must correspond to an existing storey in `self.storeys`.
        :param length: The length of the wall in model units.
        :param height: The height of the wall in model units.
        :param thickness: The thickness of the wall in model units. If a valid `wall_type_name` is provided,
                          this value will be replaced with the sum of the wall type's material layers.
        :param wall_type_name: The name of a wall type in the model. If None, no wall type is assigned.
        :return: The created IfcWall entity instance.

        This method performs the following steps:
        1. Validates that the target storey exists in the model.
        2. Creates a new IfcWall entity in the model.
        3. Sets the placement of the wall using the default coordinates.
        4. Assigns the wall type (if provided) and calculates the wall's thickness from the wall type.
        5. Generates a geometric representation of the wall with the specified dimensions.
        6. Links the wall to the specified storey in the model hierarchy.

        Raises:
            ValueError: If the specified storey does not exist in `self.storeys`.
            ValueError: If the specified wall type is not defined.
        """
        if self.storeys[target_storey] is None:
            raise ValueError(f'The storey {target_storey} does not exist.')

        storey = self.storeys[target_storey]
        wall = ifcopenshell.api.root.create_entity(self.model, ifc_class="IfcWall")
        calculated_thickness = thickness

        # Assign wall type
        if wall_type_name is not None:
            if wall_type_name not in self.element_types['wall_types']:
                raise ValueError(f'Wall type "{wall_type_name}" is not defined.')
            target_wall_type: entity_instance = self.element_types['wall_types'][wall_type_name]
            ifcopenshell.api.type.assign_type(self.model, related_objects=[wall], relating_type=target_wall_type)

            # Calculate thickness from wall type layers
            calculated_thickness = self.get_wall_type_thickness(target_wall_type)

        # Create representation
        ifcopenshell.api.geometry.edit_object_placement(self.model, product=wall)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            self.model,
            context=self.body,
            length=length,
            height=height,
            thickness=calculated_thickness
        )

        # Validate geometry representation creation
        if representation is None:
            raise RuntimeError("Failed to create a geometric representation for the wall.")

        ifcopenshell.api.geometry.assign_representation(self.model, product=wall, representation=representation)
        ifcopenshell.api.spatial.assign_container(self.model, relating_structure=storey, products=[wall])

        return wall

    # Sub methods (utils)
    def get_wall_type_thickness(self, wall_type: entity_instance) -> float:
        """
        Calculate the total thickness of all material layers in the given wall type.

        :param wall_type: The IfcWallType entity to analyze.
        :return: The total thickness of the wall type in model units (e.g., meters).

        Steps:
        1. Traverse the IfcRelAssociatesMaterial relationship to find the material layers.
        2. Check for valid material types (IfcMaterialLayerSet or IfcMaterialLayerSetUsage).
        3. Sum up the LayerThickness values for all layers in the material set.

        Raises:
            ValueError: If no material is associated with the wall type.
            ValueError: If the material does not reference a valid layer set.

        Example:
            wall_type_thickness = get_wall_type_thickness(wall_type)
        """
        # Access the associated material relationship
        rel_materials = [
            rel for rel in self.model.by_type("IfcRelAssociatesMaterial")
            if wall_type in rel.RelatedObjects  # Use RelatedObjects instead of RelatingObject
        ]

        if not rel_materials:
            raise ValueError(f'The wall type "{wall_type.Name}" does not have an associated material.')

        material = rel_materials[0].RelatingMaterial
        print(self.model.write("test1.ifc"))

        # Sum up the thickness of all layers
        # total_thickness = sum(layer.LayerThickness for layer in material_layer_set.MaterialLayers)

        return 0.3

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}"),