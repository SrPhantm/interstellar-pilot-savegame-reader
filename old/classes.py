from json import dumps

class BaseClass:
    def __init__(self):
        pass
    
    def getJSON(self):
        return dumps(self.__dict__, indent=2)

class GameObject(BaseClass):
    def __init__(self):
        self.class_id = None
        self.class_name = None

    def getClassNameByID(self, classes):
        for i in classes:
            if classes[i] == self.class_id:
                self.class_name = i

class Save(BaseClass):
    def __init__(self):
        self.header = Header()
        self.seconds_elapsed = None
        self.sectors = []
        self.factions = []
        self.patrol_paths = []
        self.units = []

class Header(BaseClass):
    def __init__(self):
        self.version = None
        self.is_autosave = None
        self.timestamp = None
        self.scenario_info_id = None
        self.global_save_number = None
        self.save_number = None
        self.have_player = None
        self.player_sector_name = None
        self.player_name = None
        self.credits = None

class Sector(BaseClass):
    def __init__(self):
        self.id = None
        self.name = None
        self.map_position = None
        self.resource_name = None
        self.description = None
        self.gate_distance_multiplier = None
        self.random_seed = None
        self.position = None
        self.background_rotation = None
        self.light_rotation = None

class Faction(BaseClass):
    def __init__(self):
        self.id = None
        self.has_generated_name = None
        self.generated_name_id = None
        self.generated_suffix_id = None
        self.has_custom_name = None
        self.custom_name = None
        self.custom_short_name = None
        self.credits = None
        self.description = None
        self.is_civilian = None
        self.faction_type = None
        self.aggression = None
        self.virtue = None
        self.greed = None
        self.trade_efficiency = None
        self.dynamic_relations = None
        self.show_jobs_boards = None
        self.create_jobs = None
        self.requisition_point_multiplier = None
        self.destory_when_no_units = None
        self.min_npc_combat_efficiency = None
        self.max_npc_combat_efficiency = None
        self.additional_rp_provision = None
        self.trade_illegal_goods = None
        self.spawn_time = None
        self.highest_ever_networth = None
        self.has_ai_settings = None
        self.custom_settings = FactionCustomSettings()
        self.has_stats = None
        self.stats = FactionStats()
        self.autopilot_excluded_sectors = []
        self.relations = []
        self.opinions = []

    def getJSON(self):
        info = self.__dict__
        info['custom_settings'] = info['custom_settings'].__dict__
        info['stats'] = info['stats'].__dict__
        return dumps(info, indent=2)

class FactionCustomSettings(BaseClass):
        def __init__(self):
            self.prefer_single_ship = None
            self.repair_ships = None
            self.upgrade_ships = None
            self.repair_min_hull_damage = None
            self.repair_min_credits_before_repair = None
            self.preference_to_place_bounty = None
            self.large_ship_preference = None
            self.daily_income = None
            self.hostile_with_all = None
            self.min_fleet_unit_count = None
            self.max_fleet_unit_count = None
            self.offensive_stance = None
            self.allow_other_factions_to_use_docks = None
            self.preference_to_build_turrents = None
            self.preference_to_build_stations = None
            self.ignore_stations_credit_reserve = None

class FactionStats(BaseClass):
    def __init__(self):
        self.total_ships_claimed = None
        self.units_destoryed_by_class_id = None
        self.units_lost_by_class_id = None
        self.scratchcards_scratched = None
        self.highest_scratchcard_win = None

class SectorPatrolPath(BaseClass):
    def __init__(self):
        self.id = None
        self.sector = None
        self.is_loop = None
        self.nodes = []

    def getJSON(self):
        info = self.__dict__
        info['nodes'] = [i.__dict__ for i in info['nodes']]
        return dumps(info, indent=2)
        
class SectorPatrolPathNode(BaseClass):
    def __init__(self):
        self.position = None
        self.order = None

class FactionRelation(BaseClass):
    def __init__(self):
        self.faction_id = None
        self.other_faction_id = None
        self.permanent_peace = None
        self.restrict_hostility_timeout = None
        self.neutrality = None
        self.hostility_end_time = None
        self.recent_damage_received = None

class FactionOpinion(BaseClass):
    def __init__(self):
        self.faction_id = None
        self.other_faction_id = None
        self.opinion = None

class Unit(GameObject):
    def __init__(self):
        self.name = None
        self.id = None
        self.class_id = None
        self.class_name = None
        self.sector_id = None
        self.position = None
        self.rotation = None
        self.faction_id = None
        self.rp_provision = None
        self.has_cargo = None
        self.cargo_data = UnitCargo()
        self.has_debris = None
        self.debris_data = UnitDebris()
        self.has_ship_trader = None
        self.ship_trader_data = []
        self.has_projectile = None
        self.projectile_data = UnitProjectile()
        self.component_unit_data = UnitModules()

    def getJSON(self):
        info = self.__dict__
        info['cargo_data'] = info['cargo_data'].__dict__
        info['debris_data'] = info['debris_data'].__dict__
        info['projectile_data'] = info['projectile_data'].__dict__
        info['projectile_data']['damage_type'] = info['projectile_data']['damage_type'].__dict__
        return dumps(info, indent=2)

class UnitCargo(GameObject):
    def __init__(self):
        self.class_id = None
        self.class_name = None
        self.quantity = None
        self.expires = None
        self.expirytime = None

class UnitDebris(BaseClass):
    def __init__(self):
        self.quantity = None
        self.expires = None
        self.expirytime = None
        self.related_unit_class_id = None

class UnitShipTraderItem(BaseClass):
    def __init__(self):
        self.sell_multiplier = None
        self.unit_class_id = None

class UnitProjectile(BaseClass):
    def __init__(self):
        self.source_unit = None
        self.target_unit = None
        self.fire_time = None
        self.remaining_movement = None
        self.damage_type = DamageType()

class UnitModules(BaseClass):
    def __init__(self):
        self.ship_name_index = None
        self.custom_ship_name = None
        self.cargo_capacity = None
        self.has_factory = None
        self.factory_data = []
        self.is_under_construction = None
        self.construction_progress = None
        self.station_unit_class_number = None
        self.modded_modules = []
        self.capacitor_charge = None


class UnitModule_Factory(BaseClass):
    def __init__(self):
        self.state = None
        self.production_elapsed = None

class UnitModule_Modded(BaseClass):
    def __init__(self):
        self.bay_id = None
        self.component_class_id = None
        self.component_class = None


class DamageType(BaseClass):
    def __init__(self):
        self.damage = None
        self.mining_damage = None
        self.sheild_damage_type = None