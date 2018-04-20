import os
import re

def read_palette():
    palette_num = 0
    palettes = []
    try:
        palette_file = open(os.path.join(os.path.dirname(__file__), "Palettes.txt"))
        for line in palette_file.readlines():
            if re.match('##', line, re.I) is not None:
                pass
            if (re.match('##', line, re.I) is None and len(line.strip()) != 0):
                palettes.append({line.split(':')[0].strip() : re.findall(r'"(#\w+)"', line, re.I)})
                palette_num += 1         
    except IOError:
        pass
    return palettes

