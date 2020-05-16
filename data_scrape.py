#!/usr/bin/env 

import json 
import requests
import urllib3
import csv
import itertools 
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

types = {1: "normal", 2: "fighting", 3: "flying", 4 : "poison", 5: "ground", 6: "rock", 7: "bug",
        8 : "ghost", 9: "steel", 10 : "fire", 11 : "water", 12 : "grass", 13 : "electric" , 14 : "psychic",
        15 : "ice", 16 : "dragon", 17 : "dark", 18 : "fairy"}

type_list = list(types.values())


def base_stat():
    num = 1
    with open("base_stat.txt", "w") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_NONE, escapechar = '\\')
        while (num <= 151):
            poke_id = str(num)
            url = "https://pokeapi.co/api/v2/pokemon/" + poke_id
            data = requests.get(url).json()
            stats = data["stats"]
            speed = stats[0]["base_stat"]
            sp_def = stats[1]["base_stat"]
            sp_atk = stats[2]["base_stat"]
            defense = stats[3]["base_stat"]
            attack = stats[4]["base_stat"]
            base_hp = stats[5]["base_stat"]
            str_res = f"insert into base_stat(poke_id, base_health, base_attack, base_defense, base_special_attack, base_special_defense, base_speed) values ({poke_id}, {base_hp}, {attack}, {defense}, {sp_atk}, {sp_def}, {speed})"
            writer.writerow([str_res])
            num += 1 
    out.close()
    return 

    
def poke_info():
    num = 1 
    with open("pinfo.txt", "w") as out:
        writer = csv.writer(out)
        while (num <= 151):
            poke_id = str(num)
            url = "https://pokeapi.co/api/v2/pokemon/" + poke_id
            data = requests.get(url).json()
            species_url = "https://pokeapi.co/api/v2/pokemon-species/" + poke_id
            spec_data = requests.get(species_url).json()
            name = data["name"]
            height = data["height"]/10  ## PokeAPI has height improperly multipled by 10 so need to correct it to get meters 
            weight = data["weight"]/10  ## PokeAPI has weight improperly multiplied by 10 so need to correct it to get kilograms
            catch_rate = spec_data["capture_rate"] 
            level_rate = spec_data["growth_rate"]["name"]
            stat_url = "https://pokeapi.co/api/v2/pokemon/" + poke_id
            stat_data = requests.get(stat_url).json()
            stats = stat_data["stats"]
            speed = stats[0]["base_stat"]
            sp_def = stats[1]["base_stat"] 
            sp_atk = stats[2]["base_stat"]
            defense = stats[3]["base_stat"]
            attack = stats[4]["base_stat"]
            base_hp = stats[5]["base_stat"] 

            str_res = f"insert into pokemon(poke_id,poke_name, poke_height, poke_weight, poke_catch_rate, poke_level_rate, base_health, base_attack, base_defense, base_special_attack, base_special_defense, base_speed) VALUES ({poke_id}, '{name}', {height}, {weight}, {catch_rate}, '{level_rate}',{base_hp}, {attack}, {defense}, {sp_atk}, {sp_def}, {speed})"

            writer.writerow([str_res])
            num +=1 
    out.close()
    return 


def dual_types():
    finals = [list((perm)) for perm in itertools.permutations(type_list ,2)]
    for mono in type_list[::-1]:        # add the monotypes to the beginning of list 
        sing = [str(mono)]
        finals.insert(0,sing)

    no_dups = []                        ## start to store the permutations into new list--this time with no duplicates 
    for item in finals:
        if len(item) == 1: 
            no_dups.append(item)
        else: 
            check = [item[1], item[0]]  #check if duplicate--would look like a reverse of types (e..g (rock, ice) is the same as (ice, rock))
            if check not in no_dups:
                no_dups.append(item)

    type_ids = {}                       # assign an id for each combination of type a pokemon can have  
    for key,val in enumerate(no_dups):
        type_ids[key] = val

    return type_ids                     # return the dictionary where a unique ID maps to a specific pokemon type (~170 possible type pairings)

# need to write "insert into..." statements for the types  
# plan: generate all the unique 170 type_ids with associated names 
def get_types(option=False):
    #all_types = dual_types()
    all_types = type_list
    match_type_name_id = []   ## to store the type ids and type names. The type names will be stored in a list for easy seach+match in the has_types function 
    weakness = get_type_weakness() 
    with open("types_and_weaknesses.txt", "w") as out: 
        writer = csv.writer(out) 
        for key, val in all_types.items():
            type_str_format = "" 
            if len(val) == 1: 
                type_str_format = "'" + val[0] + "'"
                match_type_name_id.append([key,[val[0]]])

            if (len(val) == 2): 
                type_str_format = "'" + val[0] + "/" + val[1] + "'" 
                match_type_name_id.append([key,[val[0], val[1]]])
            if (option == True): 
                str_res = f"insert into ptype(ptype_id, ptype_name, weak_against_normal, weak_against_fighting, weak_against_flying, weak_against_poison, weak_against_ground, weak_against_rock, weak_against_bug, weak_against_ghost, weak_against_steel, weak_against_fire, weak_against_water, weak_against_grass, weak_against_electric, weak_against_psychic, weak_against_ice, weak_against_dragon, weak_against_dark, weak_against_fairy) values ({key}, {type_str_format}, {weakness[key]});" 
                writer.writerow([str_res]) 
        out.close()
    return match_type_name_id


# now need to get all the 150 pokemon with their poke_ids and match their poke_id with the generated names associated to a type_id 
def has_types():
    match_type_name_id = get_types() 
    num = 1
    with open("has_types.txt", "w") as out: 
        writer = csv.writer(out)
        while (num <= 151):
            poke_id = str(num) 
            url = "https://pokeapi.co/api/v2/pokemon/" + poke_id
            data = requests.get(url).json()
            first = data["types"][0]["type"]["name"] 
            curr_types = [first]  
            if (len(data["types"]) >1 ):   
                    second = data["types"][1]["type"]["name"] 
                    curr_types.append(second) 
            for val in match_type_name_id:   ## match_type_name_id has the type_id and type_name for each entry now need to match with each of the 151 pokemon 
                if (len(curr_types) > 1):
                    if (curr_types[0] in val[1]) and (curr_types[1] in val[1]):
                        str_res = f"insert into has_types(poke_id, type_id) values ({num}, {val[0]});" 
                else: 
                    if (curr_types[0] in val[1]) and (len(val[1]) == 1):
                        str_res = f"insert into has_types(poke_id, type_id) values ({num}, {val[0]});" 
            writer.writerow([str_res])
            num += 1 
        out.close()
    return 


# need to get both types, if exist, of a pokemon and find out all the "double damage from" values 
# this way we can append all the weaknesses that pokemon could be weak to. The values will be populated for a simple 
# boolean table that will record whether a pokemon is weak to it or not. 
def get_type_weakness():
    poke_type_count = 0
    type_ids = dual_types()                   # use the dual_types() function to get the dictionary of all possible combination of types  (170 possible types)
    tot_str_res = {} 
    while (poke_type_count != len(type_ids.keys())):
        poke_type_name = type_ids[poke_type_count]  # use the type_ids dict to get the list containing the type name 
        current_types = [i for i in poke_type_name]
        weaknesses = [] 
        for ptype in current_types:
            url = "https://pokeapi.co/api/v2/type/" + ptype
            type_data = requests.get(url).json()
            for item in type_data["damage_relations"]["double_damage_from"]:  # the pokeapi has a cascading dict-list structure so need to keep drilling down
                weak = item["name"] 
                if weak in poke_type_name and weak not in ('dragon', 'ghost'): # can't have a dual type be weak against itself. Dragon and Ghost types are the exceptions
                    pass 
                else:
                    weaknesses.append(weak)  ## get the weakness string name to our weaknesses list for all the items 
        weak_bools = {}  # create the boolean array that will store the weaknesses as a 1 if weak to, 0 if otherwise 
        for name in type_list:
            weak_bools[name] = False
        for weakness in weaknesses:
            if weakness in weak_bools.keys():
                weak_bools[weakness] = True
        weak_bool_string = ""
        for name,val in weak_bools.items():
            intermediary = f"weak_bools['{name}']"
            if name != 'fairy':  # fairy, the last item, shouldn't have a comma
                last = ","
            weak_bool_string += (intermediary + last ) 
        bool_res = eval(weak_bool_string)
        bool_res = re.sub(r'[\(\)]', '', str(bool_res))
        str_res = f"insert into type_weak_to_attack_type(ptype_id, weak_against_normal, weak_against_fighting, weak_against_flying, weak_against_poison, weak_against_ground,\
        weak_against_rock, weak_against_bug, weak_against_ghost, weak_against_steel, weak_against_fire, weak_against_water, weak_against_grass, weak_against_electric,\
        weak_against_psychic, weak_against_ice, weak_against_dragon, weak_against_dark, weak_against_fairy) values ({poke_type_count}, {bool_res});"
        tot_str_res[poke_type_count] = bool_res
        poke_type_count += 1
    return tot_str_res 



def get_moves(): 
    url = "https://pokeapi.co/api/v2/generation/1"
    data = requests.get(url).json()
    moves = data["moves"] 
    with open("pokemon_moves.txt", "w") as out:
        writer = csv.writer(out)
        move_id = 0 
        for move in moves:
            move_name = move["name"] 
            move_url = move["url"] 
            move_data = requests.get(move_url).json() 
            move_accuracy = move_data["accuracy"] 
            move_pp = move_data["pp"] 
            move_power = move_data["power"] 
            move_type = move_data["type"]["name"]  
            move_category = move_data["damage_class"]["name"] 
            move_description = move_data["flavor_text_entries"][-3]["flavor_text"].replace("\n", " ") 
            move_description = f"'{move_description}'"
            str_res = f"insert into move(move_id, move_name, move_description, move_type, move_category, move_pp, move_power) values into ({move_id}, '{move_name}', {move_description}, '{move_type}','{move_category}', {move_pp}, {move_power})"
            writer.writerow([str_res])
            move_id += 1 
        out.close() 
    return 


def has_move():
    move_url = "https://pokeapi.co/api/v2/generation/1"
    move_data = requests.get(move_url).json()
    moves = move_data["moves"]
    move_id_name = {} 
    for move_id in range(len(moves)):  ## zero-indexed here but the API starts off at 1 with their moves
        move_id_name[move_id] = moves[move_id]["name"] 

    with open("has_moves.txt", "w") as out:
        num = 1 
        writer = csv.writer(out)
        while (num <= 151):
            pokemon_url = "https://pokeapi.co/api/v2/pokemon/" + str(num)
            pokemon_data = requests.get(pokemon_url).json()
            pokemon_moves = pokemon_data['moves'] 
            for i in range(len(pokemon_moves)):
                info_string = json.dumps(pokemon_data['moves'][i])
                if 'red-blue' in info_string:
                    info = list(pokemon_moves[i].values())
                    name = info[0]["name"]
                    for key, val in move_id_name.items():
                        if name == val:
                            str_res = f"insert into has_move(poke_id, move_id) values ({num}, {key})" 
                            writer.writerow([str_res])
            num += 1
    out.close() 
    return 

# generate the statements for the weak entity set. Need to iterate through each poke_id and find out which of the pokemon had evolutions
def evolution():
    with open("evolutions3.txt", "w") as out: 
        writer = csv.writer(out) 
        num = 1
        while (num <= 151):
            poke_id = str(num) 
            evol_url = "https://pokeapi.co/api/v2/pokemon-species/" + poke_id 
            data = requests.get(evol_url).json()
            evolve_from = data["evolves_from_species"]   # get the pokemon that evolves into the current poke_id identiied pokemon (predecessor) 
            if (evolve_from != None):  ## if there is a predecessor 
                predecessor_url = evolve_from["url"] 
                evolve_from_id = re.findall(r'\d{1,3}', predecessor_url)[1]  ## regex match to get the pokemon id 

                if (int(evolve_from_id) > 150):   # some pokemon have pre-evolutions in later generations so the API will yield those results as well. Can't have them for a generation 1 only DB 
                    pass
                else:
                    str_res = f"insert into evolution (poke_id, evolution_id) values ({evolve_from_id}, {poke_id});"  # in our DB we only want our records to show pokemon and what they evolve to so we \
                    writer.writerow([str_res])
            num += 1 
    out.close()


    return 

def description():
    with open("descriptions.txt", "w") as out:
        writer = csv.writer(out) 
        for num in range(1,152):
            poke_id = str(num)
            url = "https://pokeapi.co/api/v2/pokemon-species/" + poke_id 
            data = requests.get(url).json()
            flv_len = len(data["flavor_text_entries"])
            entry_num = 0 
            red_pokedex = "" 
            firered_pokedex = "" 
            yellow_pokedex = "" 
            while (entry_num < flv_len):
                entry = data["flavor_text_entries"][entry_num] 
                if entry["version"]["name"] == "red":
                    red_pokedex = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                if entry["version"]["name"] == "firered":
                    firered_pokedex = entry["flavor_text"].replace("\n", " ").replace("\f", " ") 
                if entry["version"]["name"] == "yellow":
                    yellow_pokedex = entry["flavor_text"].replace("\n", " ").replace("\f", " ") 
                entry_num += 1 
            red_res = f"insert into description (poke_id, pokedex_entry) values ({poke_id}, \"{red_pokedex}\");" 
            firered_res = f"insert into description (poke_id, pokedex_entry) values ({poke_id}, \"{firered_pokedex}\");"
            yellow_res = f"insert into description (poke_id, pokedex_entry) values ({poke_id}, \"{yellow_pokedex}\");"
            writer.writerow([red_res])
            writer.writerow([firered_res])
            writer.writerow([yellow_res])

    out.close()
    return 

def egg_group(): 
    url = "https://pokeapi.co/api/v2/egg-group/"
    data = requests.get(url).json()
    egg_dict = {} 
    with open("egg_group.txt", "w") as out:
        writer = csv.writer(out) 
        eggs = data["results"]    ## returns a list of dicts -- need to get the name of each egg 
        count = 0 
        for egg_type in eggs:
            name = egg_type["name"] 
            str_res = f"insert into egg_group(egg_group_id, egg_group_name) values ({count}, \'{name}\');"
            writer.writerow([str_res]) 
            egg_dict[name] = count
            count += 1 
    out.close()

    return egg_dict

def part_of_egg_group():
    with open("part_of_egg_group.txt", "w") as out:
        writer = csv.writer(out) 
        egg_dict = egg_group()
        for num in range(1,152):
            poke_id = str(num) 
            url = "https://pokeapi.co/api/v2/pokemon-species/" + poke_id 
            data = requests.get(url).json()
            egg_groups = data["egg_groups"] 
            for egg_g in egg_groups: 
                egg_name = egg_g["name"] 
                egg_key = egg_dict[egg_name] 
                str_res = f"insert into part_of_egg_group(poke_id, egg_group_id) values ({num}, {egg_key});"
                writer.writerow([str_res])
    out.close()
    return 


def ailments():
    ailment_dict = {}
    with open("ailments.txt", "w") as out: 
        writer = csv.writer(out) 
        url = "https://pokeapi.co/api/v2/move-ailment/" 
        data = requests.get(url).json()
        ailments = data["results"]
        count = 0
        for entry in range(len(ailments)):
            name = ailments[entry]["name"] 
            if (name == "none" ):  
                str_res = f"insert into ailments(ailment_id, ailment_name) values (-1, \'Damage\');"
            else:
                str_res = f"insert into ailments(ailment_id, ailment_name) values ({count}, \'{name}\');"
                ailment_dict[name] = count 
                count += 1 
            writer.writerow([str_res])
    out.close() 
    return ailment_dict 

def causes_ailment():
    ailment_dict = ailments()
    with open("causes_ailment.txt", "w") as out:
        writer = csv.writer(out) 
        for num in range(0,165): # all 165 moves 
            move_id = str(num+1) ## need to offset by 1 because the URLs for the moves start off at 1 but need to keep the zero-indexing because has_moves and all_moves already use zero-indexing 
            url = "https://pokeapi.co/api/v2/move/" + move_id 
            data = requests.get(url).json()
            meta = data["meta"] 
            ailment = meta["ailment"]["name"]
            if ailment == "none" or ailment == "unknown":
                str_res = f"insert into causes_ailment (move_id, ailment_id) values ({num}, -1);"
                writer.writerow([str_res])
            elif (ailment == "burn" or ailment == "confusion" or ailment == "poison"):
                str_res = f"insert into causes_ailment (move_id, ailment_id) values ({num}, -1);"
                writer.writerow([str_res])
                str_res = f"insert into causes_ailment (move_id, ailment_id) values ({num}, {ailment_dict[ailment]});" 
                writer.writerow([str_res])
            else: 
                str_res = f"insert into causes_ailment (move_id, ailment_id) values ({num}, {ailment_dict[ailment]});" 
                writer.writerow([str_res])
    out.close()

    return 

def habitat():
    url = "https://pokeapi.co/api/v2/pokemon-habitat/"
    data = requests.get(url).json()
    habitat_dict = {} 
    with open("habitat.txt", "w") as out:
        writer = csv.writer(out) 
        results = data["results"] 
        count = 0 
        for result in results:
            name = result["name"] 
            str_res = f"insert into habitats (habitat_id, habitat_name) values ({count}, \'{name}\');"
            writer.writerow([str_res]) 
            habitat_dict[name] = count 
            count += 1 
    out.close() 
    return habitat_dict 

def lives_in():
    habitat_dict = habitat()
    with open("lives_in.txt", "w") as out:
        writer = csv.writer(out) 
        for area in habitat_dict.values():
            url = "https://pokeapi.co/api/v2/pokemon-habitat/" + str(area+1)
            data = requests.get(url).json() 
            pokemon = [poke for poke in data["pokemon_species"]]
            for poke in pokemon:
                url = poke["url"] 
                poke_id = int(re.findall(r'\d{1,3}', url)[1])
                if poke_id <= 151: 
                    str_res = f"insert into lives_in (poke_id, habitat_id) values ({poke_id}, {area});"
                    writer.writerow([str_res])

    out.close() 

    return 




def main():
#    get_type_weakness()
#    poke_info()
#    base_stat()
#    get_types(True)
#    has_types()
#    get_moves()
#    has_move()
#    evolution()
#    description()
#    egg_group()
#    part_of_egg_group() 
#    ailments()
#    causes_ailment() 
    habitat()
    lives_in()
    print("hi")

if __name__ == '__main__':
    main()
