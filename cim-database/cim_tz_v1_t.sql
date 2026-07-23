/* Tables */
CREATE TABLE PROJECT_SCENARIO (
    project_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    project_boundary INTEGER NOT NULL,
    project_name INTEGER NOT NULL,
    project_center INTEGER NOT NULL,
    cencus_boundary INTEGER NOT NULL,
    grid_id INTEGER NOT NULL,
    project_crs INTEGER NOT NULL,
    PRIMARY KEY (project_id, scenario_id)
);
CREATE TABLE BUILDING (
    building_id INTEGER NOT NULL,
    LoD INTEGER NOT NULL,
    footprint INTEGER NOT NULL,
    cm_footprint INTEGER NOT NULL,
    PRIMARY KEY (building_id, LoD)
);
CREATE TABLE THERMAL_ZONE (
    tz_id INTEGER NOT NULL,
    tz_solid INTEGER NOT NULL,
    PRIMARY KEY (tz_id)
);
CREATE TABLE ENVELOPE_COMPONENT (
    nvlp_cmpnt_id INTEGER NOT NULL,
    threeD_geo INTEGER NOT NULL,
    PRIMARY KEY (nvlp_cmpnt_id)
);
CREATE TABLE BUILDING_PROPERTIES (
    PROJECT_SCENARIO_project_id INTEGER NOT NULL,
    PROJECT_SCENARIO_scenario_id INTEGER NOT NULL,
    BUILDING_building_id INTEGER NOT NULL,
    BUILDING_LoD INTEGER NOT NULL,
    height INTEGER NOT NULL,
    z_value INTEGER NOT NULL,
    area INTEGER NOT NULL,
    volume INTEGER NOT NULL,
    year_of_construction INTEGER NOT NULL,
    n_family INTEGER NOT NULL,
    n_people INTEGER NOT NULL,
    building_main_usage INTEGER NOT NULL,
    cm_height INTEGER NOT NULL,
    cm_year_construction INTEGER NOT NULL,
    tabula_year INTEGER NOT NULL,
    tabula_class INTEGER NOT NULL,
    tabula_archetype_code INTEGER NOT NULL,
    PRIMARY KEY (PROJECT_SCENARIO_project_id, PROJECT_SCENARIO_scenario_id, BUILDING_building_id, BUILDING_LoD),
    FOREIGN KEY (PROJECT_SCENARIO_project_id, PROJECT_SCENARIO_scenario_id) REFERENCES PROJECT_SCENARIO (project_id, scenario_id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
    FOREIGN KEY (BUILDING_building_id, BUILDING_LoD) REFERENCES BUILDING (building_id, LoD)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);
CREATE TABLE TZ_PROPS (
    BUILDING_building_id INTEGER NOT NULL,
    BUILDING_LoD INTEGER NOT NULL,
    THERMAL_ZONE_tz_id INTEGER NOT NULL,
    energy_sys INTEGER NOT NULL,
    nvlp_efficiency INTEGER NOT NULL,
    inflation_ratio INTEGER NOT NULL,
    internal_gain_equipments INTEGER NOT NULL,
    internal_gain_people INTEGER NOT NULL,
    setpoint INTEGER NOT NULL,
    DHW INTEGER NOT NULL,
    PRIMARY KEY (BUILDING_building_id, BUILDING_LoD, THERMAL_ZONE_tz_id),
    FOREIGN KEY (BUILDING_building_id, BUILDING_LoD) REFERENCES BUILDING (building_id, LoD)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
    FOREIGN KEY (THERMAL_ZONE_tz_id) REFERENCES THERMAL_ZONE (tz_id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);
CREATE TABLE NVLP_PROPS (
    BUILDING_building_id INTEGER NOT NULL,
    BUILDING_LoD INTEGER NOT NULL,
    ENVELOPE_COMPONENT_nvlp_cmpnt_id INTEGER NOT NULL,
    total_thickness_m INTEGER NOT NULL,
    area_m2 INTEGER NOT NULL,
    u_value INTEGER NOT NULL,
    layers_list INTEGER NOT NULL,
    component_type INTEGER NOT NULL,
    storey_label INTEGER NOT NULL,
    tabula_archetype_code INTEGER NOT NULL,
    tabula_construction_code INTEGER NOT NULL,
    n_layers INTEGER NOT NULL,
    u_value_best INTEGER NOT NULL,
    y_internal INTEGER NOT NULL,
    y_external INTEGER NOT NULL,
    u_periodic INTEGER NOT NULL,
    azimuth INTEGER NOT NULL,
    inclination_tilt INTEGER NOT NULL,
    boundary_condition INTEGER NOT NULL,
    w2w_ratio INTEGER NOT NULL,
    g_value INTEGER NOT NULL,
    PRIMARY KEY (BUILDING_building_id, BUILDING_LoD, ENVELOPE_COMPONENT_nvlp_cmpnt_id),
    FOREIGN KEY (BUILDING_building_id, BUILDING_LoD) REFERENCES BUILDING (building_id, LoD)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
    FOREIGN KEY (ENVELOPE_COMPONENT_nvlp_cmpnt_id) REFERENCES ENVELOPE_COMPONENT (nvlp_cmpnt_id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);