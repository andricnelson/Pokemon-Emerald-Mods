import os
import json
import random

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_valid_maps_with_warps(map_groups_file, folder_path):
    map_groups = load_json(map_groups_file)
    valid_maps = {}

    for group in map_groups:
        if group.startswith("gMapGroup_"):
            for map_name in map_groups[group]:
                if "LittlerootTown" in map_name or "InsideOfTruck" in map_name:
                    continue

                map_path = os.path.join(folder_path, map_name, "map.json")
                if os.path.exists(map_path):
                    map_data = load_json(map_path)
                    warp_events = map_data.get("warp_events", [])
                    if warp_events:
                        formatted_map_name = map_data["id"]
                        valid_maps[formatted_map_name] = [i for i in range(len(warp_events))]

    return valid_maps

def get_adjacent_warps(warp_events):
    adjacent_groups = []
    visited = set()

    for i, warp in enumerate(warp_events):
        if i in visited:
            continue
        group = [i]
        for j in range(i + 1, len(warp_events)):
            if (warp_events[i]["y"] == warp_events[j]["y"] and abs(warp_events[i]["x"] - warp_events[j]["x"]) == 1) or \
               (warp_events[i].get("dest_map") == warp_events[j].get("dest_map")):
                group.append(j)
                visited.add(j)
        adjacent_groups.append(group)
    return adjacent_groups

def get_all_map_files(folder_path):
    maps = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file == "map.json":
                maps.append(os.path.join(root, file))
    return maps

def randomize_warps(folder_path, map_groups_file):
    valid_maps = get_valid_maps_with_warps(map_groups_file, folder_path)

    map_files = get_all_map_files(folder_path)

    for map_file in map_files:
        if "LittlerootTown" in map_file or "InsideOfTruck" in map_file:
            continue

        data = load_json(map_file)
        warp_events = data.get('warp_events', [])

        adjacent_groups = get_adjacent_warps(warp_events)

        for group in adjacent_groups:
            dest_map = random.choice(list(valid_maps.keys()))
            dest_warp_id = random.choice(valid_maps[dest_map])

            for index in group:
                warp_events[index]['dest_map'] = dest_map
                warp_events[index]['dest_warp_id'] = str(dest_warp_id)

        with open(map_file, 'w') as file:
            json.dump(data, file, indent=2)

randomize_warps(
    folder_path=r"C:\Users\andri\Documents\decomps\pokeemerald\data\maps",
    map_groups_file=r"C:\Users\andri\Documents\decomps\pokeemerald\data\maps\map_groups.json"
)
