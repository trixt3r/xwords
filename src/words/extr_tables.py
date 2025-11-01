from bs4 import BeautifulSoup
import requests
import re

#extraction des isotopes stables a partir de la page wikipedia
# WIKTIONARY_ZIM = "wiktionary_fr_all_maxi_2024-06"

# http://192.168.1.13:8080/content/wikipedia_fr_all_nopic_2025-09/Nickel
BASE_URL=f"http://192.168.1.13:8080/content/wikipedia_fr_all_nopic_2025-09/"
# w = "Nickel"
# page = requests.get(f"{BASE_URL}{w}")
#     # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)





def extract_table_new(table,except_rows=lambda row: False):
    def _is_html_element(el):
        return hasattr(el, "name") and el.name is not None
    result = []
    rows = table.find("thead")
    if rows:
        #TODO
        pass
    
    rows = table.find("tbody")
    if not rows:
        rows = table

    for row in rows.children:
        if not _is_html_element(row) or except_rows(row):
            continue
        if not row.name == "tr":
            raise Exception(f"Expected tr element, got {row.name}")
        
        children = list()
        for cell in row.children:
            if not _is_html_element(cell):
                continue
            if cell.name in ["th", "td"]:
                inner_table = cell.find("table")
                if inner_table:
                    children.append(extract_table_new(inner_table))
                else:
                    t = cell.get_text()
                    if len(t)>0:
                        children.append(t)
        if len(children)>0:
            if len(children)==2:
                result.append((children[0], children[1]))
            result.append(children)
    return result





#detects periodic table in infobox, in order to skip it
def check_chemicals_row(row):
    table = row.find("table")
    if table:
        t = table.find_all("tr")[-1].text
        if "Tableau complet" in t:
            return True
    return False

def extract_isotopes(chemical_element:str):
    print(f"Extracting isotopes for {chemical_element}")
    page = requests.get(f"{BASE_URL}{chemical_element}")
    html_content = page.content
    soup = BeautifulSoup(html_content, "html.parser")

    infobox = soup.find("table", class_="infobox_v2")
    result = extract_table_new(infobox,check_chemicals_row  )
    print(len(result))

    isotopes_index = [i for i,r in enumerate(result) if "Isotopes les plus stables" in r]
    isotopes_table = None
    if len(isotopes_index)==1:
        isotopes_index = isotopes_index[0]
        isotopes_table = result[isotopes_index + 1][0]
        return isotopes_table

# elements_list=["Hydrogène", "Hélium", "Lithium", "Béryllium", "Bore", "Carbone", "Azote", "Oxygène", "Fluor", "Néon","Sodium", "Magnésium", "Aluminium", "Silicium", "Phosphore", "Soufre", "Chlore", "Argon", "Potassium", "Calcium", "Scandium", "Titane", "Vanadium", "Chrome", "Manganèse", "Fer", "Cobalt", "Nickel", "Cuivre", "Zinc", "Gallium", "Germanium", "Arsenic", "Sélénium", "Brome", "Krypton", "Rubidium", "Strontium", "Yttrium", "Zirconium", "Niobium", "Molybdène", "Technétium", "Ruthénium", "Rhodium", "Palladium", "Argent", "Cadmium", "Indium", "Étain", "Antimoine", "Tellure", "Iode", "Xénon", "Césium", "Baryum", "Lanthane", "Cérium", "Praséodyme", "Néodyme", "Prométhium", "Samarium", "Europium", "Gadolinium", "Terbium", "Dysprosium", "Holmium", "Erbium", "Thulium", "Ytterbium", "Lutécium", "Hafnium", ("Tantale","Tantale_(chimie)"), "Tungstène", "Rhénium", "Osmium", "Iridium", "Platine", "Or", "Mercure", "Thallium", "Plomb", "Bismuth", "Polonium", "Astate", "Radon",  ]
elements_list=["Hydrogène", "Hélium", "Lithium", "Béryllium", "Bore", "Carbone", "Azote", "Oxygène", "Fluor", "Néon","Sodium", "Magnésium", "Aluminium", "Silicium", "Phosphore", "Soufre", "Chlore", "Argon", "Potassium", "Calcium", "Scandium", "Titane", "Vanadium", "Chrome", "Manganèse", "Fer", "Cobalt", "Nickel", "Cuivre", "Zinc", "Gallium", "Germanium", "Arsenic", "Sélénium", "Brome", "Krypton", "Rubidium", "Strontium", "Yttrium", "Zirconium", "Niobium", "Molybdène", "Technétium", "Ruthénium", "Rhodium", "Palladium", "Argent", "Cadmium", "Indium", "Étain", "Antimoine", "Tellure", "Iode", "Xénon"]

isotopes_tables = {elt: extract_isotopes(elt)[2:] for elt in elements_list}
iso_nickel=extract_isotopes("Nickel")
iso_aluminium=extract_isotopes("Aluminium")
stability = {elt:isotopes[2:] for elt,isotopes in isotopes_tables.items()}

def parse_isotope_row(row):
    isotope_info = {"nb_mass":None,"ratio":"","stable":None}
    label = ""
    if row[0].startswith("[n 1]") or row[0].startswith("[n 2]"):
        row[0] = row[0][6:].strip()
    m = re.match(r'(\d+)\s*', row[0])
    
    if m:
        isotope_info["nb_mass"] = int(m.group(0))
        # capture any trailing text after the mass number
        label = row[0][m.end():].strip()
        if label:
            isotope_info["label"] = label
    else:
        raise Exception(f"Could not parse mass number from {row[0]}")
    if "syn" in row[1] or "trace" in row[1].lower() or "ppm" in row[1]:
        #NOTE peut-etre il y a qd mm un ratio
        isotope_info["ratio"] = 0.0
    else:
        ratio_match = re.search(r'([\d.,]+)\s*%', row[1].replace(" ","").replace("\xa0",""))
        if ratio_match:
            ratio_str = ratio_match.group(1).replace(',', '.')
            isotope_info["ratio"] = float(ratio_str) / 100.0
        else:
            print(f"Could not find ratio in {label} {row[1]}")
            raise Exception(f"Could not parse ratio from {label} {row[1]}")
    if "stable" in row[-1]:
        isotope_info["stable"] = True
    else:
        isotope_info["stable"] = False
    return isotope_info

parsed = {elt:[parse_isotope_row(r) for r in table] for elt,table in isotopes_tables.items()}
stables = {elt:[iso for iso in isotopes if iso["stable"]] for elt,isotopes in parsed.items()}
unstables = {elt:[iso for iso in isotopes if not iso["stable"]] for elt,isotopes in parsed.items()}
ratios = {e:sum([r["ratio"] for r in rows]) for e,rows in parsed.items()}

primes_list = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199]

{elt:[iso for iso in rows if iso["nb_mass"] in primes_list] for elt,rows in parsed.items()}

    
# ok=None
# for th in infobox.find_all("th"):
#     if th.text.strip()=="Isotopes les plus stables":
#         print(th.text)
#         elt = th.parent
#         while elt is not None and elt.name != "table":
#             elt = elt.find_next_sibling("tr")
#             table = elt.find("td").find("table")
#             if table is not None:
#                 elt = table
