from enum import Enum

class WriterCategory(Enum):
    Project = "Project"
    Site = "Site"
    Building = "Building"
    Storey = "Storey"
    Space = "Space"
    Material = "Material"
    MaterialSet = "MaterialSet"
    ElementInstance = "ElementInstance"             # Each ifc elements (Wall, Slab, Beam, Column, and so on)
    Profile = "Profile"
    ElementType = "ElementType"                     # Element's type (WallType, ColumnType, and so on)
    Geometry = "Geometry"
    Property = "Property"
    Connection = "Connection"
    System = "System"
    Group = "Group"
    Annotation = "Annotation"
    Actor = "Actor"
    Resource = "Resource"
    Context = "Context"
    Owner = "Owner"
    Person = "Person"
    Organization = "Organization"