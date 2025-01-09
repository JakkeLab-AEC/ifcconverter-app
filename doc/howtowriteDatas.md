# How to Write the Mapping Table and Target Data

When working with this system, two key components define how JSON data is converted into IFC entities: the **Mapping Table** and the **Target Data**. Here's a step-by-step explanation of how to write both.

---

### 1. Writing the Mapping Table

The **Mapping Table** (`mappingTableExample.json`) serves as a bridge between the user-defined JSON data (Target Data) and the expected IFC entity arguments. It defines:

* Which **IFC class** each entity corresponds to
* The mapping between user-defined argument keys and the required IFC arguments

#### Structure of the Mapping Table

1. **`mappingEntity`**:
   * A collection of key-value pairs where each key is an IFC class (e.g., `IfcColumn`, `IfcBeam`)
   * Each value defines how to map the user-defined arguments (`userKey` and `userArgs`) to the required IFC arguments

2. **`userKey`**:
   * This specifies the name of the entity in the Target Data that corresponds to the IFC class

3. **`userArgs`**:
   * A dictionary mapping user-defined argument names (as found in the Target Data) to the required argument names for the corresponding IFC class

#### Example

For `IfcColumn`:

```json
"IfcColumn": {
    "userKey": "Column",
    "userArgs": {
        "coordinate": "coordinate",
        "height": "height",
        "rotation": "rotation",
        "targetStorey": "targetStorey"
    }
}
```

* The `userKey` is `Column`, meaning all entries in the Target Data with the key `"userKey": "Column"` are processed as `IfcColumn` entities
* `userArgs` maps:
  * `coordinate` → `coordinate`
  * `height` → `height`
  * `rotation` → `rotation`
  * `targetStorey` → `targetStorey`

This structure ensures that the system understands how to interpret and convert the user-provided data into the format required for `IfcColumn`.

---

### 2. Writing the Target Data

The **Target Data** (`targetFileExample.json`) contains the actual input data defining the elements to be converted into IFC entities. It follows the structure defined by the Mapping Table.

#### Structure of the Target Data

1. **Each Entry**:
   * Contains a `userKey` corresponding to the `userKey` in the Mapping Table
   * Includes a `userArgs` object that matches the mapped arguments in the Mapping Table

2. **Keys and Values**:
   * Keys within `userArgs` must align with the names defined in the Mapping Table for each IFC class
   * Values provide the specific data required for the IFC entity

#### Example

For a column in the Target Data:

```json
{
    "userKey": "Column",
    "userArgs": {
        "targetStorey": "1F",
        "rotation": 30,
        "height": 3,
        "coordinate": [0, 0]
    }
}
```

* The `userKey` is `Column`, linking this entry to `IfcColumn` in the Mapping Table
* `userArgs` provides:
  * `coordinate`: `[0, 0]`
  * `height`: `3`
  * `rotation`: `30`
  * `targetStorey`: `"1F"`

---

### Steps to Write the Mapping Table and Target Data

1. **Identify the IFC Classes Needed**:
   * Review the `MappableIfcClasses` enum for supported IFC classes (e.g., `IfcColumn`, `IfcBeam`, etc.)

2. **Define the Mapping Table**:
   * For each IFC class, define a `userKey` that represents the entity in the Target Data
   * Map each required IFC argument to its corresponding key in the Target Data

3. **Write the Target Data**:
   * Use the defined `userKey` to categorize each entry
   * Provide the required arguments as specified in the Mapping Table

---

### Tips

* **Ensure Consistency**: The keys in the Mapping Table (`userArgs`) must exactly match the keys in the Target Data
* **Extendability**: If you want to add support for a new IFC class, update both the Mapping Table and the Target Data accordingly
* **Validation**: Validate that the Target Data conforms to the argument structures (`IfcColumnArgs`, `IfcBeamArgs`, etc.) defined in the TypeScript interfaces

---

### Conclusion

The Mapping Table serves as a flexible guide for interpreting and transforming user-defined JSON data into IFC entities, while the Target Data contains the specific instances to be converted. Together, they allow for seamless and customizable IFC file generation based on user input.

Currently, only supports IfcBuildingStorey, IfcColumn, IfcWallStandardCase, IfcBeam as simplified type (like single layer Wall, 300x300 H-Beam shaped). Will update other form and types in future.
