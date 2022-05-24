import struct


class Reader:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readVector3(self) -> tuple:
        return (self.readSingle(), self.readSingle(), self.readSingle())

    def readVector4(self) -> tuple:
        return (self.readSingle(), self.readSingle(), self.readSingle(), self.readSingle())

    def readSingle(self) -> int:
        raw = self.data[self.position:self.position+4]
        self.position += 4
        return struct.unpack('f', raw)[0]

    def readInt32(self) -> int:
        raw = self.data[self.position:self.position+4]
        self.position += 4
        return int.from_bytes(raw, 'little', signed=True)

    def readDouble(self) -> int:
        raw = self.data[self.position:self.position+8]
        self.position += 8
        return int.from_bytes(raw, 'little')

    def readBoolean(self) -> bool:
        raw = self.data[self.position:self.position+1]
        self.position += 1
        return True if raw != b'\x00' else False

    def read7BitInt(self) -> int:
        byte_list = []
        while len(byte_list) <= 5:
            byte = self.data[self.position:self.position+1]
            byte_list.insert(0, '{:08b}'.format(int(byte.hex(), 16)))
            self.position += 1
            if byte_list[0][0] == '0':
                break

        binary_number = ''
        for count, byte in enumerate(byte_list):
            byte = byte[1:]
            if count == 0:
                byte = byte.lstrip('0')
            binary_number += byte

        if binary_number != '':
            number = int(binary_number, 2)
        else:
            number = 0
        return number
        
    def readString(self) -> str:
        lenght = self.read7BitInt()
        string = self.data[self.position:self.position+lenght]
        string = string.decode()
        self.position += lenght
        return string

    def readByte(self) -> int:
        raw = self.data[self.position:self.position+1]
        self.position += 1
        return int.from_bytes(raw, 'little')

class SaveReader(Reader):
    def __init__(self, data):
        super().__init__(data)

    def readHeader(self) -> dict:
        header = {}
        header['version'] = f'{self.readInt32()}.{self.readInt32()}.{self.readInt32()}'
        header['autosave'] = self.readBoolean()
        header['timestamp'] = self.readString()
        header['scenario_info_id'] = self.readInt32()
        header['global_save_number'] = self.readInt32()
        header['save_number'] = self.readInt32()
        header['has_player'] = self.readBoolean()

        if header['has_player']:
            header['player_sector_name'] = self.readString()
            header['player_name'] = self.readString()
            header['credits'] = self.readInt32()
    
        return header

    def _readSector(self) -> dict:
        sector = {}
        sector['id'] = self.readInt32()
        sector['name'] = self.readString()
        sector['map_position'] = self.readVector3()
        sector['resource_name'] = self.readString()
        sector['description'] = self.readString()
        sector['gate_distance_multiplier'] = self.readSingle()
        sector['random_seed'] = self.readInt32()
        sector['position'] = self.readVector3()
        sector['background_rotation'] = self.readVector3()
        sector['light_rotation'] = self.readVector3()
        return sector

    def readSectors(self) -> list:
        sectors = []
        count = self.readInt32()
        for _ in range(count):
            sectors.append(self._readSector())
    
    def _readFactionAiSettings(self) -> dict:
        settings = {}
        settings['prefer_single_ship'] = self.readBoolean()
        settings['repair_ships'] = self.readBoolean()
        settings['upgrade_ships'] = self.readBoolean()
        settings['repair_min_hull_damage'] = self.readSingle()
        settings['repair_min_credits'] = self.readInt32()
        settings['preference_to_place_bounty'] = self.readSingle()
        settings['large_ship_preference'] = self.readSingle()
        settings['daily_income'] = self.readInt32()
        settings['hostile_with_all'] = self.readBoolean()
        settings['min_fleet_unit_count'] = self.readInt32()
        settings['max_fleet_unit_count'] = self.readInt32()
        settings['offensinve_stance'] = self.readSingle()
        settings['allow_other_factions_to_dock'] = self.readBoolean()
        settings['preference_to_build_turrents'] = self.readSingle()
        settings['preference_to_build_stations'] = self.readSingle()
        settings['ignore_stations_credit_reserve'] = self.readBoolean()
        return settings

    def _readFactionStatsUnitCounts(self) -> list:
        count = self.readInt32()
        items = []
        for _ in range(count):
            items.append((self.readInt32(), self.readInt32()))
        return items

    def _readFactionStats(self) -> dict:
        stats = {}
        stats['total_ships_claimed'] = self.readInt32()
        stats['units_destoryed_by_id'] = self._readFactionStatsUnitCounts()
        stats['units_lost_by_id'] = self._readFactionStatsUnitCounts()
        stats['scratchcards_scratched'] = self.readInt32()
        stats['highest_scratchcard_win'] = self.readInt32()

    def _readFaction(self) -> dict:
        faction = {}
        faction['id'] = self.readInt32()

        faction['has_generated_name'] = self.readBoolean()
        if faction['has_generated_name']:
            faction['generated_name_id'] = self.readInt32()
            faction['generated_suffix_id'] = self.readInt32()
        else:
            faction['has_custom_name'] = self.readBoolean()
            if faction['has_custom_name']:
                faction['custom_name'] = self.readString()
                faction['custom_short_name'] = self.readString()
        
        faction['credits'] = self.readInt32()
        faction['description'] = self.readString()
        faction['civilian'] = self.readBoolean()
        faction['type'] = self.readInt32()
        faction['aggression'] = self.readSingle()
        faction['virtue'] = self.readSingle()
        faction['greed'] = self.readSingle()
        faction['trade_efficiency'] = self.readSingle()
        faction['dynamic_relations'] = self.readBoolean()
        faction['show_job_boards'] = self.readBoolean()
        faction['create_jobs'] = self.readBoolean()
        faction['requisition_point_multiplier'] = self.readSingle()
        faction['destory_when_no_units'] = self.readBoolean()
        faction['min_npc_combat_efficiency'] = self.readSingle()
        faction['max_npc_combat_efficiency'] = self.readSingle()
        faction['additional_rp_provision'] = self.readInt32()
        faction['trade_illegal_goods'] = self.readBoolean()
        faction['spawn_time'] = self.readDouble()
        faction['highest_networth'] = self.readInt32()

        faction['has_ai_settings'] = self.readBoolean()
        if faction['has_ai_settings']:
            faction['ai_settings'] = self._readFactionAiSettings()

        faction['has_stats'] = self.readBoolean()
        if faction['has_stats']:
            faction['stats'] = self._readFactionStats()

        faction['excluded_sectors'] = []
        excluded_sector_count = self.readInt32()
        for _ in range(excluded_sector_count):
            faction['excluded_sectors'].append(self.readInt32())
        return faction

    def readFactions(self) -> list:
        factions = []
        count = self.readInt32()
        for _ in range(count):
            factions.append(self._readFaction())
        return factions

    def _readPatrolPathNode(self) -> dict:
        node = {}
        node['position'] = self.readVector3()
        node['order'] = self.readInt32()
        return node

    def _readPatrolPath(self) -> dict:
        path = {}
        path['id'] = self.readInt32()
        path['sector'] = self.readInt32()
        path['loop'] = self.readBoolean()
        path['nodes'] = []

        node_count = self.readInt32()
        for _ in range(node_count):
            path['nodes'].append(self._readPatrolPathNode())
        return path

    def readPatrolPaths(self) -> list:
        paths = []
        count = self.readInt32()
        for _ in range(count):
            paths.append(self._readPatrolPath())
        return paths

    def _readFactionRelation(self, faction_id) -> dict:
        relation = {}
        relation['faction'] = faction_id
        relation['other_faction'] = self.readInt32()
        relation['permanent_peace'] = self.readBoolean()
        relation['restrict_hostility_timeout'] = self.readBoolean()
        relation['neutrality'] = self.readInt32()
        relation['hostility_end_time'] = self.readDouble()
        relation['recent_damage_recieved'] = self.readSingle()
        return relation
    
    def readFactionRelations(self) -> list:
        relations = []
        count = self.readInt32()
        for _ in range(count):
            faction_id = self.readInt32()
            count = self.readInt32()
            for _ in range(count):
                relations.append(self._readFactionRelation(faction_id))
        return relations
    
    def _readFactionOpinion(self) -> dict:
        opinion = {}
        opinion['faction'] = self.readInt32()
        opinion['other_faction'] = self.readInt32()
        opinion['opinion'] = self.readSingle()
        return opinion

    def readFactionOpinions(self) -> list:
        opinions = []
        count = self.readInt32()
        for _ in range(count):
            opinions.append(self._readFactionOpinion())
        return opinions

    def _readUnitCargo(self):
        cargo = {}
        cargo['class'] = self.readInt32()
        cargo['quantity'] = self.readInt32()
        cargo['expires'] = self.readBoolean()
        cargo['expiry_time'] = self.readDouble()
        return cargo

    def _readShipTrader(self):
        ships = []
        count = self.readInt32()
        for _ in range(count):
            ship = {}
            ship['sell_multiplier'] = self.readSingle()
            ship['class'] = self.readInt32()
            ships.append(ship)
        return ships

    def _readDamageType(self):
        damage = {}
        damage['damage'] = self.readSingle()
        damage['mining_damage'] = self.readSingle()
        damage['sheild_damage_type'] = self.readInt32()
        return damage

    def _readProjectileData(self):
        projectile = {}
        projectile['source_unit'] = self.readInt32()
        projectile['target_unit'] = self.readInt32()
        projectile['fire_time'] = self.readDouble()
        projectile['remaining_movement'] = self.readSingle()
        projectile['damage_type'] = self._readDamageType()
        return projectile

    def _readUnit(self):
        unit = {}
        unit['id'] = self.readInt32()
        unit['class'] = self.readInt32()
        unit['sector'] = self.readInt32()
        unit['position'] = self.readVector3()
        unit['rotation'] = self.readVector4()
        unit['faction'] = self.readInt32()
        unit['rp_provision'] = self.readInt32()

        unit['is_cargo'] = self.readBoolean()
        if unit['is_cargo']:
            self._readUnitCargo()

        unit['is_debris'] = self.readBoolean()
        if unit['is_debris']:
            # Unused, this should never happen
            raise Exception('Invalid Data')
        
        unit['is_ship_trader'] = self.readBoolean()
        if unit['is_ship_trader']:
            unit['ship_trader_data'] = self._readShipTrader()

        projectile_ids = [30100, 30200, 30300, 30400, 29100, 30600, 29350, 30800, 30820, 30840, 30860, 30880, 30900, 30920, 30940, ]
        if unit['class'] in projectile_ids:
            unit['projectile_data'] = self._readProjectileData()
        
        return unit

    def _readUnits(self) -> list:
        units = []
        count = self.readInt32()
        for _ in range(count):
            units.append(self._readUnit())
        return units

    def _readUnitNames(self) -> list:
        units = []
        count = self.readInt32()
        for _ in range(count):
            unit = {}
            unit['unit_id'] = self.readInt32()
            unit['name'] = self.readString()
            units.append(unit)
        return units

    def _readUnitFactoryData(self) -> list:
        data = []
        count = self.readInt32()
        for _ in range(count):
            factory = {}
            factory['state'] = self.readInt32()
            factory['progress'] = self.readSingle()
            data.append(factory)
        return data

    def _readUnitComponentData(self) -> dict:
        component_data = {}
        component_data['unit_id'] = self.readInt32()
        component_data['ship_name_index'] = self.readInt32()
        if component_data['ship_name_index'] == -1:
            component_data['custom_ship_name'] = self.readString()
        
        component_data['cargo_capacity'] = self.readSingle()
        
        component_data['has_factory'] = self.readBoolean()
        if component_data['has_factory']:
            component_data['factories'] = self._readUnitFactoryData()

        component_data['under_construction'] = self.readBoolean()
        component_data['construction_progress'] = self.readSingle()
        component_data['station_class_number'] = self.readInt32()
        return component_data
    
    def _readAllUnitComponentData(self) -> dict:
        all_component_data = []
        count = self.readInt32()
        for _ in range(count):
            all_component_data.append(self._readUnitComponentData())
        return all_component_data

    def _readModdedComponents(self) -> dict:
        modded_components = []
        count = self.readInt32()
        for _ in range(count):
            component = {}
            component['unit_id'] = self.readInt32()
            component['bay_id'] = self.readInt32()
            component['component'] = self.readInt32()
            modded_components.append(component)
        return modded_components

    def _readCapacitorCharges(self) -> list:
        charges = []
        count = self.readInt32()
        for _ in range(count):
            charge = {}
            charge['unit_id'] = self.readInt32()
            charge['capacitor_charge'] = self.readSingle()
            charges.append(charge)
        return charges

    def _readCloakedUnits(self) -> list:
        units = []
        count = self.readInt32()
        for _ in range(count):
            units.append(self.readInt32())
        return units

    def _readPoweredDownComponents(self) -> list:
        components = []
        count = self.readInt32()
        for _ in range(count):
            component = {}
            component['unit_id'] = self.readInt32()
            component['bay_id'] = self.readInt32()
            components.append(component)
        return components

    def _readUnitEngineTrottles(self) -> list:
        trottles = []
        count = self.readInt32()
        for _ in range(count):
            trottle = {}
            trottle['unit_id'] = self.readInt32()
            trottle['trottle'] = self.readSingle()
            trottles.append(trottle)
        return trottles

    def _readUnitComponentCargo(self) -> list:
        cargos = []
        count = self.readInt32()
        for _ in range(count):
            unit_id = self.readInt32()
            count = self.readInt32()
            for _ in range(count):
                cargo = {}
                cargo['unit_id'] = unit_id
                cargo['class'] = self.readInt32()
                cargo['quantity'] = self.readInt32()
                cargos.append(cargo)
        return cargos

    def _readUnitShields(self) -> list:
        shields = []
        count = reader.readInt32()
        for _ in range(count):
            shield = {}
            shield['unit_id'] = self.readInt32()
            shield['data'] = []
            count = self.readByte()
            for _ in range(count):
                sheild_point = {}
                sheild_point['index'] = self.readByte()
                sheild_point['health'] = self.readSingle()
                shield['data'].append(sheild_point)
            shields.append(shield)
        return shields

    def _readUnitComponentHealth(self) -> list:
        healths = []
        count = self.readInt32()
        for _ in range(count):
            health = {}
            health['unit_id'] = self.readInt32()
            health['compontent_health'] = []
            count = self.readInt32()
            for _ in range(count):
                compontent = {}
                compontent['bay_id'] = self.readInt32()
                compontent['health'] = self.readSingle()
                health['compontent_health'].append(compontent)
            healths.append(health)
        return healths

    def _readActiveUnits(self) -> list:
        units = []
        count = self.readInt32()
        for _ in range(count):
            unit = {}
            unit['unit_id'] = self.readInt32()
            unit['active_data'] = {}
            unit['active_data']['velocity'] = self.readVector3(),
            unit['active_data']['currentTurn'] = self.readSingle()
            units.append(unit)
        return units

    def _readUnitHealth(self) -> list:
        units = []
        count = self.readInt32()
        for _ in range(count):
            health = {}
            health['unit_id'] = self.readInt32()
            health['destoryed'] = self.readBoolean()
            health['total_damage_recieved'] = self.readSingle()
            health['health'] = self.readSingle()
            units.append(health)
        return units

    def readAllUnitData(self) -> list:
        units = self._readUnits()
        
        for name in self._readUnitNames():
            for unit in units:
                if unit['id'] == name['unit_id']:
                    unit['name'] = name['name']
        
        for component in self._readAllUnitComponentData():
            for unit in units:
                if unit['id'] == component['unit_id']:
                    unit['component_data'] = component.copy()
                    del unit['component_data']['unit_id']
                    unit['component_data']['modded'] = []
                    unit['component_data']['offline'] = []
                    unit['component_data']['cargo'] = []

        for component in self._readModdedComponents():
            for unit in units:
                if unit['id'] == component['unit_id']:
                    base_component = component.copy()
                    del base_component['unit_id']
                    unit['component_data']['modded'].append(base_component)

        for capacitor in self._readCapacitorCharges():
            for unit in units:
                if unit['id'] == capacitor['unit_id']:
                    unit['component_data']['capacitor_charge'] = capacitor['capacitor_charge']

        for unit_id in self._readCloakedUnits():
            for unit in units:
                if unit['id'] == unit_id:
                    unit['component_data']['cloaked'] = True
        
        for component in self._readPoweredDownComponents():
            for unit in units:
                if unit['id'] == component['unit_id']:
                    unit['component_data']['offline'].append(component['bay_id'])

        for trottle in self._readUnitEngineTrottles():
            for unit in units:
                if unit['id'] == trottle['unit_id']:
                    unit['component_data']['trottle'] = trottle['trottle']

        for cargo in self._readUnitComponentCargo():
            for unit in units:
                if unit['id'] == cargo['unit_id']:
                    base_cargo = cargo.copy()
                    del base_cargo['unit_id']
                    unit['component_data']['cargo'].append(base_cargo)
        return units