import json
import re

m3u_file = "lista.m3u"
json_file = "channels.json"

channels = []
stream_id = 1

with open(m3u_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i in range(len(lines)):
    line = lines[i].strip()

    if line.startswith("#EXTINF"):

        name = line.split(",")[-1]

        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        group_match = re.search(r'group-title="([^"]*)"', line)

        logo = logo_match.group(1) if logo_match else ""
        group = group_match.group(1) if group_match else "Outros"

        url = lines[i+1].strip()

        channel = {
            "id": stream_id,
            "name": name,
            "logo": logo,
            "group": group,
            "url": url
        }

        channels.append(channel)

        stream_id += 1

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(channels, f, indent=2, ensure_ascii=False)

print("Conversão concluída. channels.json criado.")