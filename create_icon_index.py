
import os

icon_dir = "dashboard-icons-main/svg"
index_file = "icon_index.txt"

with open(index_file, "w") as f:
    for icon_file in os.listdir(icon_dir):
        if icon_file.endswith(".svg"):
            f.write(f"{icon_file}\n")

