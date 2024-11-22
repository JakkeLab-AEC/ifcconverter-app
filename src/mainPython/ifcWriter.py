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
from ifcopenshell import entity_instance

default_units = {
    "LENGTHUNIT": None,     #
    "AREAUNIT": None,
    "VOLUMEUNIT" : None,
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

        # Save properties
        self.model = model
        self.project = project
        self.units = units
        self.site = site
        self.building = building
        self.storeys = {}
        self.elements = {}

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

    def save(self, output_file):
        """
        Save as IFC File
        :param output_file: File path to save IFC file
        """
        self.model.write(output_file)
        print(f"IFC file saved: {output_file}"),