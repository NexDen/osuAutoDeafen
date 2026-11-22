import json
import websocket
import pynput


preset_combos = {}
default_value = ""

old_file_hash = ""
new_file_hash = ""

def read_file():
    global preset_combos, default_value, old_file_hash, new_file_hash
    with open("maps.csv", "r+", encoding="utf-8") as f:

        content = f.read()
        f.seek(0)
        new_file_hash = hash(content)

        if new_file_hash != old_file_hash:
            print("updated file")
            lines = f.readlines()
            index = 0
            for line in lines:
                line = line.strip()
                if line.startswith("#"): continue
                if index == 0:
                    default_value = line
                else:
                    map_id = int(line.split(",")[0])
                    value = line.split()[1]
                    preset_combos[map_id] = value
                
                index += 1

        old_file_hash = new_file_hash


read_file() 
deafen_key = pynput.keyboard.Key.scroll_lock

has_deafen = False

keyboard = pynput.keyboard.Controller()

def on_message(ws, msg):
    global has_deafen

    read_file()

    data : dict = json.loads(msg)
    map_id = data["beatmap"]["id"]

    max_combo = data["beatmap"]["stats"]["maxCombo"]
    preset_combo = preset_combos.get(map_id, default_value)
    if preset_combo.endswith("p"):
        target_combo = max_combo * int(preset_combo.removesuffix("p")) / 100
    else:
        target_combo = int(preset_combo.removesuffix("c"))

    cur_combo = int(data["play"]["combo"]["current"])
    playing = data["state"]["number"] == 2
    if playing:
        if cur_combo > target_combo:
            if not has_deafen:
                has_deafen = True
                keyboard.press(deafen_key)
                keyboard.release(deafen_key)
       
        
    elif not playing:
        if has_deafen:
            has_deafen = False
            keyboard.press(deafen_key)
            keyboard.release(deafen_key)

    #print(f"{playing=}, {cur_combo=}, {target_combo=}")

ws = websocket.WebSocketApp("ws://127.0.0.1:24050/websocket/v2", on_message=on_message, on_error=lambda ws, e: print("error:", repr(e)))
ws.run_forever()
