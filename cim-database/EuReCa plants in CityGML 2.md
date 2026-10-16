# EuReCa plants in CityGML


This page is for whoever writes the CityGML file. It says how to write a building's heating and cooling plant so that our EuReCa pipeline reads it, and which units to use.

 this works in our code, for a ready plant and for your own plant. The rules on this page are agreed.

## 1. The idea

- A plant is an Energy ADE device, written directly on the `bldg:Building`.
- The device's operation type says what it is: `spaceHeating` is the heating plant, `spaceCooling` is the cooling plant.
- The plant's EuReCa name is written in a `gml:name` with our `codeSpace`.
- A building may have one heating plant and one cooling plant.
- Whatever the file does not state comes from our own run settings. No device: the whole plant. No cooling device: the cooling. No size on a device: the size.

There are two ways to say which plant it is:

| Way | You write | EuReCa takes its numbers from |
| --- | --- | --- |
| A ready plant (section 2) | one of EuReCa's ready names (section 5) | its own tables |
| Your own plant (section 3) | the name `From manual parameters`, and the plant's values | you |

## 2. A ready plant

```xml
<bldg:Building gml:id="my_building">

  <nrg3:device>
    <nrg3:Boiler>
      <gml:name codeSpace="urn:eureca:heating-system">Condensing Gas Boiler, Centralized, Low Temp Radiator</gml:name>
      <nrg3:numberOfDevices>1</nrg3:numberOfDevices>
      <nrg3:installedPower uom="kW">12</nrg3:installedPower>
      <nrg3:deviceOperation>
        <nrg3:DeviceOperation>
          <nrg3:type>spaceHeating</nrg3:type>
        </nrg3:DeviceOperation>
      </nrg3:deviceOperation>
      <nrg3:hasCondensation>true</nrg3:hasCondensation>
    </nrg3:Boiler>
  </nrg3:device>

  <nrg3:device>
    <nrg3:HeatPump>
      <gml:name codeSpace="urn:eureca:cooling-system">A-W chiller, Centralized, Fan coil</gml:name>
      <nrg3:installedPower uom="kW">8</nrg3:installedPower>
      <nrg3:deviceOperation>
        <nrg3:DeviceOperation>
          <nrg3:type>spaceCooling</nrg3:type>
        </nrg3:DeviceOperation>
      </nrg3:deviceOperation>
      <nrg3:heatSource>ambientAir</nrg3:heatSource>
    </nrg3:HeatPump>
  </nrg3:device>

  ...the rest of the building...
```

| What | Where | What to write | Required |
| --- | --- | --- | --- |
| The device | `nrg3:device`, directly on the `bldg:Building` | Any kind the schema has: `Boiler`, `HeatPump`, `GenericDevice`, `GenericElectricalDevice`. Pick the closest one. We do not read the kind. The schema has no chiller, so a chiller is a `HeatPump`. | yes |
| Heating or cooling | `nrg3:DeviceOperation` / `nrg3:type` | `spaceHeating` or `spaceCooling` | yes |
| The EuReCa name | `gml:name` with `codeSpace` | The `codeSpace` is exactly `urn:eureca:heating-system` for a heating plant, or `urn:eureca:cooling-system` for a cooling plant. The text is one name from section 5, copied exactly. | yes |
| The size | `nrg3:installedPower` | A positive number with `uom="W"` or `uom="kW"`. It is the heat the plant can give to the building, or take out of it. It is not the electricity the machine draws. Write a positive number for a cooling plant too. | no |
| Several machines | `nrg3:numberOfDevices` | A whole number. It multiplies `installedPower`. When it is missing, there is one machine. | no |
| Your own label | a second `gml:name`, without a `codeSpace` | free text | no |

The schema itself asks for `hasCondensation` on a `Boiler` and for `heatSource` on a `HeatPump`. We do not read them, but the file is not valid without them.

## 3. Your own plant

EuReCa can also build a plant that is not in its list, if you give it the numbers a ready name would bring. Write `From manual parameters` as the EuReCa name, under the same `codeSpace` as a ready name. Then write the plant's values on the same device. Each value is a CityGML generic attribute, named exactly as in the tables below. Generic attributes are standard CityGML 2.0 (the Generics module), and the schema accepts them on a device.

The device, the operation type, the size and your own label work as in section 2. Both examples below pass validation against the Energy ADE 3.0 beta 7 schema.

A heating plant:

```xml
<nrg3:device>
  <nrg3:Boiler>
    <gml:name>My own boiler</gml:name>
    <gml:name codeSpace="urn:eureca:heating-system">From manual parameters</gml:name>
    <gen:stringAttribute name="name"><gen:value>My own boiler</gen:value></gen:stringAttribute>
    <gen:stringAttribute name="description"><gen:value>a gas boiler with radiators</gen:value></gen:stringAttribute>
    <gen:doubleAttribute name="SH generation efficiency [-]"><gen:value>0.99</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SH distribution efficiency [-]"><gen:value>0.92</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SH emission efficiency [-]"><gen:value>0.88</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SH regulation efficiency [-]"><gen:value>1.0</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SH emission convective fraction [-]"><gen:value>0.6</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SH emission target temperature [°C]"><gen:value>45</gen:value></gen:doubleAttribute>
    <gen:stringAttribute name="SH fuel"><gen:value>Natural Gas</gen:value></gen:stringAttribute>
    <gen:doubleAttribute name="DHW generation efficiency [-]"><gen:value>0.99</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="DHW distribution efficiency [-]"><gen:value>0.92</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="DHW emission efficiency [-]"><gen:value>0.88</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="DHW regulation efficiency [-]"><gen:value>1.0</gen:value></gen:doubleAttribute>
    <gen:stringAttribute name="DHW fuel"><gen:value>Natural Gas</gen:value></gen:stringAttribute>
    <nrg3:installedPower uom="kW">12</nrg3:installedPower>
    <nrg3:deviceOperation>
      <nrg3:DeviceOperation>
        <nrg3:type>spaceHeating</nrg3:type>
      </nrg3:DeviceOperation>
    </nrg3:deviceOperation>
    <nrg3:hasCondensation>true</nrg3:hasCondensation>
  </nrg3:Boiler>
</nrg3:device>
```

A cooling plant:

```xml
<nrg3:device>
  <nrg3:HeatPump>
    <gml:name>My own chiller</gml:name>
    <gml:name codeSpace="urn:eureca:cooling-system">From manual parameters</gml:name>
    <gen:doubleAttribute name="SC generation efficiency [-]"><gen:value>2.7</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SC distribution efficiency [-]"><gen:value>0.97</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SC emission efficiency [-]"><gen:value>0.75</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SC regulation efficiency [-]"><gen:value>1.0</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SC emission convective fraction [-]"><gen:value>1.0</gen:value></gen:doubleAttribute>
    <gen:doubleAttribute name="SC emission target temperature [°C]"><gen:value>12</gen:value></gen:doubleAttribute>
    <gen:stringAttribute name="SC fuel"><gen:value>Electric</gen:value></gen:stringAttribute>
    <nrg3:installedPower uom="kW">8</nrg3:installedPower>
    <nrg3:deviceOperation>
      <nrg3:DeviceOperation>
        <nrg3:type>spaceCooling</nrg3:type>
      </nrg3:DeviceOperation>
    </nrg3:deviceOperation>
    <nrg3:heatSource>ambientAir</nrg3:heatSource>
  </nrg3:HeatPump>
</nrg3:device>
```

### The values of a heating plant

Every row is required, except the two COP rows. There are no defaults: if a value is missing, the run stops at the start. It does not say which value, so check your device against this table.

| Value | What it means | Where to write it | Unit | Example |
| --- | --- | --- | --- | --- |
| Generation efficiency | share of the fuel's energy that becomes heat | `gen:doubleAttribute`, name `SH generation efficiency [-]` | a plain number | 0.99 |
| Distribution efficiency | what is left after the losses in the pipes | `gen:doubleAttribute`, name `SH distribution efficiency [-]` | a plain number from 0 to 1 | 0.92 |
| Emission efficiency | what is left after the losses at the emitter | `gen:doubleAttribute`, name `SH emission efficiency [-]` | a plain number from 0 to 1 | 0.88 |
| Regulation efficiency | what is left after the losses of the control | `gen:doubleAttribute`, name `SH regulation efficiency [-]` | a plain number from 0 to 1 | 1.0 |
| Convective fraction | share of the heat that goes to the room air; the rest goes to the walls as radiation | `gen:doubleAttribute`, name `SH emission convective fraction [-]` | a plain number from 0 to 1 | 0.6 radiator, 1.0 fan coil, 0.35 radiant surface |
| Fuel | what the plant burns or uses | `gen:stringAttribute`, name `SH fuel` | one of these words: `Natural Gas` (also read without the space, `NaturalGas`), `Oil`, `Coal`, `Wood`, `Pellet`, `LPG`, `Gasoline`, `Electric`, `DH` (district heat) | Natural Gas |
| COP | only when the fuel is `Electric` | `gen:doubleAttribute`, name `SH COP [-]` | a plain number | 3.2 heat pump, 1 electric heater |
| Hot water: generation efficiency | the same four efficiencies, for the hot water | `gen:doubleAttribute`, name `DHW generation efficiency [-]` | a plain number | 0.99 |
| Hot water: distribution efficiency | | `gen:doubleAttribute`, name `DHW distribution efficiency [-]` | a plain number from 0 to 1 | 0.92 |
| Hot water: emission efficiency | | `gen:doubleAttribute`, name `DHW emission efficiency [-]` | a plain number from 0 to 1 | 0.88 |
| Hot water: regulation efficiency | | `gen:doubleAttribute`, name `DHW regulation efficiency [-]` | a plain number from 0 to 1 | 1.0 |
| Hot water: fuel | what heats the hot water | `gen:stringAttribute`, name `DHW fuel` | the same words as `SH fuel`, but not `Pellet` | Natural Gas |
| Hot water: COP | only when the hot water fuel is `Electric` | `gen:doubleAttribute`, name `DHW COP [-]` | a plain number | 3.2 |
| Name | a placeholder: EuReCa asks for it and never uses it | `gen:stringAttribute`, name `name` | any text, not empty | My own boiler |
| Description | a placeholder: EuReCa asks for it and never uses it | `gen:stringAttribute`, name `description` | any text, not empty | a gas boiler with radiators |
| Emission target temperature | the water temperature at the emitter. A placeholder: EuReCa asks for it and never uses it | `gen:doubleAttribute`, name `SH emission target temperature [°C]` | a number, in °C | 45 |

### The values of a cooling plant

Every row is required, with no defaults. There is no hot water part.

| Value | What it means | Where to write it | Unit | Example |
| --- | --- | --- | --- | --- |
| Generation efficiency | cooling delivered per unit of electricity, over the season | `gen:doubleAttribute`, name `SC generation efficiency [-]` | a plain number, above 1 | 2.7 chiller, 2.27 split |
| Distribution efficiency | what is left after the losses in the pipes | `gen:doubleAttribute`, name `SC distribution efficiency [-]` | a plain number from 0 to 1 | 0.97 |
| Emission efficiency | what is left after the losses at the emitter | `gen:doubleAttribute`, name `SC emission efficiency [-]` | a plain number from 0 to 1 | 0.75 fan coil, 0.78 radiant surface |
| Regulation efficiency | what is left after the losses of the control | `gen:doubleAttribute`, name `SC regulation efficiency [-]` | a plain number from 0 to 1 | 1.0 |
| Convective fraction | share of the cooling that acts on the room air; the rest acts on the walls | `gen:doubleAttribute`, name `SC emission convective fraction [-]` | a plain number from 0 to 1 | 1.0 fan coil or split, 0.35 radiant surface |
| Fuel | what the plant uses | `gen:stringAttribute`, name `SC fuel` | the word `Electric` | Electric |
| Emission target temperature | the water temperature at the emitter. A placeholder: EuReCa asks for it and never uses it | `gen:doubleAttribute`, name `SC emission target temperature [°C]` | a number, in °C | 12 |

### A sample to look at

EuReCa's ready plants (section 5) are written inside its own code, so their name is enough. `From manual parameters` is the door EuReCa leaves open for any other plant: you give its values yourself, as in the two tables above. For a hint of what such values look like, EuReCa has a sample file, `systems.xlsx`, with one example plant per row and the same value names. It is only a sample: the rules are the tables above.

Download: [systems.xlsx](https://github.com/BETALAB-team/EUReCA/raw/main/eureca_ubem/Input/systems.xlsx)

### Rules for your own plant

- **Units.** An efficiency is a plain number, not a percentage: write 0.92, not 92. A generic attribute has no `uom`. The `[-]` in its name means "no unit". The only value with a `uom` is the size, `installedPower` (`W` or `kW`).
- **`nominalEfficiency` is not read.** It is an ordinary field of the device: you may write it or leave it out. The efficiency EuReCa uses is the generic attribute `SH generation efficiency [-]` or `SC generation efficiency [-]`.
- **Names.** The generic attribute names are EuReCa's own names for these values. Copy them exactly, with the brackets.
- **Placeholders.** EuReCa asks for `name`, `description` and the emission target temperature, but it never uses them in its calculation. They must still be there, or the run stops. So write something simple: a short text, and any sensible number.
- **One overall efficiency.** EuReCa multiplies the four efficiencies into one number. If you only know one overall efficiency, write it as the generation efficiency and write 1.0 for the other three. The result is the same.
- **An electric heating plant.** With the fuel `Electric`, EuReCa divides by the generation efficiency and by the COP. So put the machine's efficiency in the COP and write 1.0 as the generation efficiency. A heat pump: generation efficiency 1.0, COP 3.2. An electric heater: generation efficiency 1.0, COP 1.
- **Fuel words.** Write each fuel exactly as one of the words in its table. Any other word is refused, for example `Gas` instead of `Natural Gas`.
- **Hot water and `Pellet`.** Do not write `Pellet` as `DHW fuel`: EuReCa does not count it, so we refuse it. `Pellet` works as `SH fuel`.
- **District cooling.** EuReCa also accepts `DH` as `SC fuel`, but our results report cooling as electricity only. So we read only `Electric`.
- **The namespace.** Declare the generics namespace once, on the top element of the file: `xmlns:gen="http://www.opengis.net/citygml/generics/2.0"`.
- **The order inside the device.** First the names, then the generic attributes, then the `nrg3` fields. The schema checks this order.
- **What a ready plant has and yours has not.** Your own plant has no electricity for its pumps and burner, and its efficiency does not change with its size.

## 4. What happens when something is wrong

| What is written | What happens | When |
| --- | --- | --- |
| no device, or a device without our `codeSpace` | it is not read; the plant comes from our run settings | |
| a `codeSpace` that does not match the operation type, for example the cooling `codeSpace` on a `spaceHeating` device | the device is not read | |
| a name that is not in EuReCa's list: a spelling mistake, or a cooling name under the heating `codeSpace` | the run stops and says EuReCa cannot build the plant | when the run starts |
| your own plant, with a value missing | the run stops and says EuReCa cannot build the plant; it does not say which value | when the run starts |
| `installedPower` in another unit than `W` or `kW` | the building is not converted; the reason is written to `_refused.json` | when we read the file |
| two devices with a EuReCa heating name on one building, or two with a cooling name | the building is not converted; the reason is written to `_refused.json` | when we read the file |
| your own plant, with a fuel word that is not in its table: `Gas` instead of `Natural Gas`, `Pellet` as `DHW fuel`, `DH` as `SC fuel` | the building is not converted; the reason is written to `_refused.json` | when we read the file |

## 5. The EuReCa names

Copy a name exactly, with its commas, spaces and capital letters. A name with commas has three parts: the machine, then `Centralized` (one plant for the building) or `Single` (one per dwelling), then what warms or cools the room.

### Heating: 52 names

The heating plant also heats the hot water.

| # | Exact name | Energy it uses |
| --- | --- | --- |
| 1 | `Condensing Gas Boiler, Centralized, Low Temp Radiator` | gas |
| 2 | `Condensing Gas Boiler, Centralized, High Temp Radiator` | gas |
| 3 | `Condensing Gas Boiler, Centralized, Fan coil` | gas |
| 4 | `Condensing Gas Boiler, Centralized, Radiant surface` | gas |
| 5 | `Condensing Gas Boiler, Single, Low Temp Radiator` | gas |
| 6 | `Condensing Gas Boiler, Single, High Temp Radiator` | gas |
| 7 | `Condensing Gas Boiler, Single, Fan coil` | gas |
| 8 | `Condensing Gas Boiler, Single, Radiant surface` | gas |
| 9 | `Traditional Gas Boiler, Centralized, Low Temp Radiator` | gas |
| 10 | `Traditional Gas Boiler, Centralized, High Temp Radiator` | gas |
| 11 | `Traditional Gas Boiler, Centralized, Fan coil` | gas |
| 12 | `Traditional Gas Boiler, Centralized, Radiant surface` | gas |
| 13 | `Traditional Gas Boiler, Single, Low Temp Radiator` | gas |
| 14 | `Traditional Gas Boiler, Single, High Temp Radiator` | gas |
| 15 | `Traditional Gas Boiler, Single, Fan coil` | gas |
| 16 | `Traditional Gas Boiler, Single, Radiant surface` | gas |
| 17 | `CondensingBoiler` | gas |
| 18 | `TraditionalBoiler` | gas |
| 19 | `Oil Boiler, Centralized, High Temp Radiator` | oil |
| 20 | `Oil Boiler, Single, High Temp Radiator` | oil |
| 21 | `Coal Heater, Centralized, High Temp Radiator` | coal |
| 22 | `Coal Heater, Single, High Temp Radiator` | coal |
| 23 | `Stove` | wood |
| 24 | `District Heating, Centralized, Low Temp Radiator` | district heat |
| 25 | `District Heating, Centralized, High Temp Radiator` | district heat |
| 26 | `District Heating, Centralized, Fan coil` | district heat |
| 27 | `District Heating, Centralized, Radiant surface` | district heat |
| 28 | `A-W Heat Pump, Centralized, Low Temp Radiator` | electricity |
| 29 | `A-W Heat Pump, Centralized, Fan coil` | electricity |
| 30 | `A-W Heat Pump, Centralized, Radiant surface` | electricity |
| 31 | `A-W Heat Pump, Single, Low Temp Radiator` | electricity |
| 32 | `A-W Heat Pump, Single, Fan coil` | electricity |
| 33 | `A-W Heat Pump, Single, Radiant surface` | electricity |
| 34 | `A-W HP Staffel, Centralized, Low Temp Radiator` | electricity |
| 35 | `A-W HP Staffel, Centralized, High Temp Radiator` | electricity |
| 36 | `A-W HP Staffel, Centralized, Fan coil` | electricity |
| 37 | `A-W HP Staffel, Centralized, Radiant surface` | electricity |
| 38 | `A-W HP Staffel, Single, Low Temp Radiator` | electricity |
| 39 | `A-W HP Staffel, Single, High Temp Radiator` | electricity |
| 40 | `A-W HP Staffel, Single, Fan coil` | electricity |
| 41 | `A-W HP Staffel, Single, Radiant surface` | electricity |
| 42 | `G-W HP Staffel, Centralized, Low Temp Radiator` | electricity |
| 43 | `G-W HP Staffel, Centralized, High Temp Radiator` | electricity |
| 44 | `G-W HP Staffel, Centralized, Fan coil` | electricity |
| 45 | `G-W HP Staffel, Centralized, Radiant surface` | electricity |
| 46 | `G-W HP Staffel, Single, Low Temp Radiator` | electricity |
| 47 | `G-W HP Staffel, Single, High Temp Radiator` | electricity |
| 48 | `G-W HP Staffel, Single, Fan coil` | electricity |
| 49 | `G-W HP Staffel, Single, Radiant surface` | electricity |
| 50 | `Electric Heater` | electricity |
| 51 | `IdealLoad` | none: no machine, the rooms still reach their setpoint |
| 52 | `From manual parameters` | the fuel you state: your own plant (section 3) |

- `A-W` is an air-to-water heat pump. `G-W` takes its heat from ground water.
- `A-W Heat Pump` has one fixed efficiency. `HP Staffel` works its efficiency out at every step, from the outdoor or ground temperature and the emitter.
- `CondensingBoiler` and `TraditionalBoiler` are detailed boiler models: their efficiency follows the load at every step.

### Cooling: 10 names

Every ready cooling plant uses electricity.

| # | Exact name | What it is |
| --- | --- | --- |
| 1 | `A-W chiller, Centralized, Fan coil` | air-to-water chiller, one plant for the building, fan coils |
| 2 | `A-W chiller, Centralized, Radiant surface` | the same, with cooled surfaces |
| 3 | `A-W chiller, Single, Fan coil` | one chiller per dwelling, fan coils |
| 4 | `A-W chiller, Single, Radiant surface` | one chiller per dwelling, cooled surfaces |
| 5 | `A-A split` | air-to-air split unit, one fixed efficiency |
| 6 | `SplitAirCooler` | split unit; the efficiency follows the load and the outdoor temperature |
| 7 | `ChillerAirtoWater` | chiller; the efficiency follows the load and the outdoor temperature |
| 8 | `SplitAirConditioner` | split unit; the efficiency follows the outdoor temperature |
| 9 | `IdealLoad` | no machine and no electricity; the rooms are still cooled |
| 10 | `From manual parameters` | your own plant (section 3) |

Names 6, 7 and 8 only work when the run has a weather file.
