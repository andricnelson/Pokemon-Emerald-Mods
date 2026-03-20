import os
import json
import random

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def get_all_map_files(folder_path):
    maps = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file == "map.json":
                maps.append(os.path.join(root, file))
    return maps

def get_adjacent_warps(warp_events):
    adjacent_groups = []
    visited = set()

    for i, warp in enumerate(warp_events):
        if i in visited:
            continue
        group = [i]
        visited.add(i)

        for j in range(i + 1, len(warp_events)):
            if (warp_events[i]["y"] == warp_events[j]["y"] and abs(warp_events[i]["x"] - warp_events[j]["x"]) == 1) or \
               (warp_events[i]["x"] == warp_events[j]["x"] and abs(warp_events[i]["y"] - warp_events[j]["y"]) == 1):
                group.append(j)
                visited.add(j)

        adjacent_groups.append(group)
    return adjacent_groups


def collect_warps_by_group(folder_path, map_groups_file):
    map_groups = load_json(map_groups_file)
    towns_and_routes_warps = []
    indoor_warps = []

    for group_name, maps in map_groups.items():
        for map_name in maps:
            if "LittlerootTown" in map_name or "InsideOfTruck" in map_name:
                continue

            map_path = os.path.join(folder_path, map_name, "map.json")
            if os.path.exists(map_path):
                data = load_json(map_path)
                warp_events = data.get("warp_events", [])
                adjacent_groups = get_adjacent_warps(warp_events)

                if group_name == "gMapGroup_TownsAndRoutes":
                    for group in adjacent_groups:
                        towns_and_routes_warps.append({
                            "map": data["id"],
                            "warp_ids": group,
                            "file_path": map_path
                        })
                elif "gMapGroup_Indoor" in group_name:
                    for group in adjacent_groups:
                        indoor_warps.append({
                            "map": data["id"],
                            "warp_ids": group,
                            "file_path": map_path
                        })

    return towns_and_routes_warps, indoor_warps

def randomize_warps(folder_path, map_groups_file):
    towns_and_routes_warps, indoor_warps = collect_warps_by_group(folder_path, map_groups_file)
    used_warps = set()

    for warp in towns_and_routes_warps:
        if any((warp["map"], warp_id) in used_warps for warp_id in warp["warp_ids"]):
            continue

        if not indoor_warps:
            print("No indoor warps available for randomization.")
            break

        target_warp = random.choice(indoor_warps)
        indoor_warps.remove(target_warp)

        source_map_data = load_json(warp["file_path"])
        source_warp_events = source_map_data["warp_events"]
        for warp_id in warp["warp_ids"]:
            source_warp_events[warp_id]["dest_map"] = target_warp["map"]
            source_warp_events[warp_id]["dest_warp_id"] = str(target_warp["warp_ids"][0])
            used_warps.add((warp["map"], warp_id))

        save_json(warp["file_path"], source_map_data)

        target_map_data = load_json(target_warp["file_path"])
        target_warp_events = target_map_data["warp_events"]
        for warp_id in target_warp["warp_ids"]:
            target_warp_events[warp_id]["dest_map"] = warp["map"]
            target_warp_events[warp_id]["dest_warp_id"] = str(warp["warp_ids"][0])
            used_warps.add((target_warp["map"], warp_id))

        save_json(target_warp["file_path"], target_map_data)

    remaining_warps = towns_and_routes_warps + indoor_warps
    while remaining_warps:
        warp = remaining_warps.pop(0)
        if any((warp["map"], warp_id) in used_warps for warp_id in warp["warp_ids"]):
            continue

        if not remaining_warps:
            print("No more remaining warps available for randomization.")
            break

        target_warp = random.choice(remaining_warps)
        remaining_warps.remove(target_warp)

        source_map_data = load_json(warp["file_path"])
        source_warp_events = source_map_data["warp_events"]
        for warp_id in warp["warp_ids"]:
            source_warp_events[warp_id]["dest_map"] = target_warp["map"]
            source_warp_events[warp_id]["dest_warp_id"] = str(target_warp["warp_ids"][0])
            used_warps.add((warp["map"], warp_id))

        save_json(warp["file_path"], source_map_data)

        target_map_data = load_json(target_warp["file_path"])
        target_warp_events = target_map_data["warp_events"]
        for warp_id in target_warp["warp_ids"]:
            target_warp_events[warp_id]["dest_map"] = warp["map"]
            target_warp_events[warp_id]["dest_warp_id"] = str(warp["warp_ids"][0])
            used_warps.add((target_warp["map"], warp_id))

        save_json(target_warp["file_path"], target_map_data)

randomize_warps(
    folder_path=r"C:\Users\andri\Documents\decomps\pokeemerald\data\maps",
    map_groups_file=r"C:\Users\andri\Documents\decomps\pokeemerald\data\maps\map_groups.json"
)
