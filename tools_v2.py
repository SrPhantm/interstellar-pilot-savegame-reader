from classes import (
    Save, Sector, Faction, SectorPatrolPath,
    SectorPatrolPathNode, FactionRelation, FactionOpinion, Unit, UnitShipTraderItem,
    DamageType, UnitModules, UnitModule_Factory, UnitModule_Modded)
import struct
import json


class DataConverter:
    def __init__(self):
        self.data = None
        self.position = 0

    def readVector3(self):
        return (self.readSingle(), self.readSingle(), self.readSingle())

    def readVector4(self):
        return (self.readSingle(), self.readSingle(), self.readSingle(), self.readSingle())

    def readSingle(self):
        raw = self.data[self.position:self.position+4]
        self.position += 4
        return struct.unpack('f', raw)[0]

    def readInt32(self):
        raw = self.data[self.position:self.position+4]
        self.position += 4
        return int.from_bytes(raw, 'little', signed=True)

    def readDouble(self):
        raw = self.data[self.position:self.position+8]
        self.position += 8
        return int.from_bytes(raw, 'little')

    def readBoolean(self):
        raw = self.data[self.position:self.position+1]
        self.position += 1
        return True if raw != b'\x00' else False

    def read7BitInt(self):
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
        
    def readString(self):
        lenght = self.read7BitInt()
        string = self.data[self.position:self.position+lenght]
        string = string.decode()
        self.position += lenght
        return string
    
    def readDamageType(self):
        damage_type = DamageType()
        damage_type.damage = self.readInt32()
        damage_type.mining_damage = self.readSingle()
        damage_type.sheild_damage_type = self.readInt32()
        return damage_type


class SaveReader(DataConverter):
    def __init__(self, data):
        self.save = Save()
        self.data = data
        self.position = 0

    def run(self):
        self.readHeader()
        self.save.seconds_elapsed = self.readDouble()
        self.readSectors()
        self.readFactions()
        self.readPatrolPaths()
        self.readFactionRelations()
        self.readFactionOpinions()
        self.readUnits()
        self.readUnitModules()
        self.readUnitModdedModules()
        self.readUnitCapacitorCharges()
        #print(self.save.__dict__)

    def readHeader(self):
        header = self.save.header

        header.version = {'major': self.readInt32(), 'minor': self.readInt32(), 'build': self.readInt32()}
        header.is_autosave = self.readBoolean()
        header.timestamp = self.readString()
        header.scenario_info_id = self.readInt32()
        header.global_save_number = self.readInt32()
        header.save_number = self.readInt32()
        header.have_player = self.readBoolean()
        if header.have_player:
            header.player_sector_name = self.readString()
            header.player_name = self.readString()
            header.credits = self.readInt32()

    def readSectors(self):
        count = self.readInt32()
        for _ in range(count):
            sector = Sector()
            sector.id = self.readInt32()
            sector.name = self.readString()
            sector.map_position = self.readVector3()
            sector.resource_name = self.readString()
            sector.description = self.readString()
            sector.gate_distance_multiplier = self.readSingle()
            sector.random_seed = self.readInt32()
            sector.position = self.readVector3()
            sector.background_rotation = self.readVector3()
            sector.light_rotation = self.readVector3()
            self.save.sectors.append(sector)

    def readFactions(self):
        count = self.readInt32()
        for _ in range(count):
            faction = Faction()
            faction.id = self.readInt32()
            faction.has_generated_name = self.readBoolean()
            if faction.has_generated_name:
                faction.generated_name_id = self.readInt32()
                faction.generated_suffix_id = self.readInt32()
            else:
                faction.has_custom_name = self.readBoolean()
                if faction.has_custom_name:
                    faction.custom_name = self.readString()
                    faction.custom_short_name = self.readString()
            
            faction.credits = self.readInt32()
            faction.description = self.readString()
            faction.is_civilian = self.readBoolean()
            faction.faction_type = self.readInt32() # Convert to string when possible
            faction.aggression = self.readSingle()
            faction.virtue = self.readSingle()
            faction.greed = self.readSingle()
            faction.trade_efficiency = self.readSingle()
            faction.dynamic_relations = self.readBoolean()
            faction.show_jobs_boards = self.readBoolean()
            faction.create_jobs = self.readBoolean()
            faction.requisition_point_multiplier = self.readSingle()
            faction.destory_when_no_units = self.readBoolean()
            faction.min_npc_combat_efficiency = self.readSingle()
            faction.max_npc_combat_efficiency = self.readSingle()
            faction.additional_rp_provision = self.readInt32()
            faction.trade_illegal_goods = self.readBoolean()
            faction.spawn_time = self.readDouble()
            faction.highest_ever_networth = self.readInt32()
            faction.has_ai_settings = self.readBoolean()
            if faction.has_ai_settings:
                faction.custom_settings.prefer_single_ship = self.readBoolean()
                faction.custom_settings.repair_ships = self.readBoolean()
                faction.custom_settings.upgrade_ships = self.readBoolean()
                faction.custom_settings.repair_min_hull_damage = self.readSingle()
                faction.custom_settings.repair_min_credits_before_repair = self.readInt32()
                faction.custom_settings.preference_to_place_bounty = self.readSingle()
                faction.custom_settings.large_ship_preference = self.readSingle()
                faction.custom_settings.daily_income = self.readInt32()
                faction.custom_settings.hostile_with_all = self.readBoolean()
                faction.custom_settings.min_fleet_unit_count = self.readInt32()
                faction.custom_settings.max_fleet_unit_count = self.readInt32()
                faction.custom_settings.offensive_stance = self.readSingle()
                faction.custom_settings.allow_other_factions_to_use_docks = self.readBoolean()
                faction.custom_settings.preference_to_build_turrents = self.readSingle()
                faction.custom_settings.preference_to_build_stations = self.readSingle()
                faction.custom_settings.ignore_stations_credit_reserve = self.readBoolean()

            faction.has_stats = self.readBoolean()
            if faction.has_stats:
                faction.stats.total_ships_claimed = self.readInt32()
                faction.stats.units_destoryed_by_class_id = self.readFactionStatsUnitCounts()
                faction.stats.units_lost_by_class_id = self.readFactionStatsUnitCounts()
                faction.stats.scratchcards_scratched = self.readInt32()
                faction.stats.highest_scratchcard_win = self.readInt32()
            
            excluded_sector_count = self.readInt32()
            for _ in range(excluded_sector_count):
                faction.autopilot_excluded_sectors.append(self.readInt32())

            self.save.factions.append(faction)

    def readFactionStatsUnitCounts(self):
        count = self.readInt32()
        items = []
        for _ in range(count):
            items.append((self.readInt32(), self.readInt32()))
        return items

    def readPatrolPaths(self):
        count = self.readInt32()
        for _ in range(count):
            path = SectorPatrolPath()
            path.id = self.readInt32()
            path.sector = self.readInt32()
            path.is_loop = self.readBoolean()

            node_count = self.readInt32()
            for _ in range(node_count):
                node = SectorPatrolPathNode()
                node.position = self.readVector3()
                node.order = self.readInt32()
                path.nodes.append(node)

            self.save.patrol_paths.append(path)

    def readFactionRelations(self):
        count = self.readInt32()
        for _ in range(count):
            faction_id = self.readInt32()
            faction_relations = []

            relations_count = self.readInt32()
            for _ in range(relations_count):
                relation = FactionRelation()
                relation.faction_id = faction_id
                relation.other_faction_id = self.readInt32()
                relation.permanent_peace = self.readBoolean()
                relation.restrict_hostility_timeout = self.readBoolean()
                relation.neutrality = self.readInt32()
                relation.hostility_end_time = self.readDouble()
                relation.recent_damage_received = self.readSingle()
                faction_relations.append(relation)

            for i, faction in enumerate(self.save.factions):
                if faction.id == faction_id:
                    self.save.factions[i].relations = faction_relations
    
    def readFactionOpinions(self):
        count = self.readInt32()
        for _ in range(count):
            faction_id = self.readInt32()

            faction_opinion = FactionOpinion()
            faction_opinion.other_faction_id = self.readInt32()
            faction_opinion.opinion = self.readSingle()

            for i, faction in enumerate(self.save.factions):
                if faction.id == faction_id:
                    self.save.factions[i].opinions.append(faction_opinion)

    def readUnits(self):
        with open('GameIDs/Unit.json') as f:
            unit_classes = json.load(f)
        with open('GameIDs/Cargo.json') as f:
            cargo_classes = json.load(f)

        count = self.readInt32()
        for _ in range(count):
            unit = Unit()
            unit.id = self.readInt32()
            unit.class_id = self.readInt32()
            unit.getClassNameByID(unit_classes)
            unit.sector_id = self.readInt32()
            unit.position = self.readVector3()
            unit.rotation = self.readVector4()
            unit.faction_id = self.readInt32()
            unit.rp_provision = self.readInt32()

            unit.has_cargo = self.readBoolean()
            if unit.has_cargo:
                unit.cargo_data.class_id = self.readInt32()
                unit.cargo_data.getClassNameByID(cargo_classes)
                unit.cargo_data.quantity = self.readInt32()
                unit.cargo_data.expires = self.readBoolean()
                unit.cargo_data.expirytime = self.readDouble()

            unit.has_debris = self.readBoolean()
            if unit.has_debris:
                unit.debris_data.quantity = self.readInt32()
                unit.debris_data.expires = self.readBoolean()
                unit.debris_data.expirytime = self.readDouble()
                unit.related_unit_class_id = self.readInt32()
            
            unit.has_ship_trader = self.readBoolean()
            if unit.has_ship_trader:
                item_count = self.readInt32()
                for _ in range(item_count):
                    item = UnitShipTraderItem()
                    item.sell_multiplier = self.readSingle()
                    item.unit_class_id = self.readInt32()
                    unit.ship_trader_data.append(item)

            if unit.class_name.startswith('Projectile_'):
                unit.projectile_data.source_unit = self.readInt32()
                unit.projectile_data.target_unit = self.readInt32()
                unit.projectile_data.fire_time = self.readDouble()
                unit.projectile_data.remaining_movement = self.readSingle()
                unit.projectile_data.damage_type = self.readDamageType()

            self.save.units.append(unit)

    def readNamedUnits(self):
        count = self.readInt32()
        for _ in range(count):
            unit_id = self.readInt32()
            unit_name = self.readString()

        for i, unit in enumerate(self.save.units):
                if unit.id == unit_id:
                    self.save.units[i].name = unit_name

    def readUnitModules(self):
        count = self.readInt32()
        for _ in range(count):
            unit_id = self.readInt32()
            modules = UnitModules()
            modules.ship_name_index = self.readInt32()
            if modules.ship_name_index == -1:
                modules.custom_ship_name = self.readString()
            
            modules.cargo_capacity = self.readSingle()
            modules.has_factory = self.readBoolean()
            if modules.has_factory:
                factory_count = self.readInt32()
                for _ in range(factory_count):
                    item = UnitModule_Factory()
                    item.state = self.readInt32()
                    print(self.data[self.position:self.position+30])
                    item.production_elapsed = self.readSingle()
                    modules.factory_data.append(item)

            for i, unit in enumerate(self.save.units):
                if unit.id == unit_id:
                    self.save.units[i].component_unit_data = modules

    def readUnitModdedModules(self):
        count = self.readInt32()
        for _ in range(count):
            unit_id = self.readInt32()
            module = UnitModule_Modded()
            module.bay_id = self.readInt32()
            module.component_class_id = self.readInt32()

            for i, unit in enumerate(self.save.units):
                if unit.id == unit_id:
                    self.save.units[i].modded_modules.append(module)

    def readUnitCapacitorCharges(self):
        count = self.readInt32()
        for _ in range(count):
            unit_id = self.readInt32()
            charge = self.readSingle()
        
        for i, unit in enumerate(self.save.units):
                if unit.id == unit_id:
                    self.save.units[i].capacitor_charge = charge
    