import sqlite3
import pandas
from skyfield.api import Loader
from telescope.lib.cache_helper import cache_path

skyfield_resource_path = cache_path() / "skyfield"
skyfield_resource_path.mkdir(parents=True, exist_ok=True)
load = Loader(skyfield_resource_path)
load('de421.bsp')

connection = sqlite3.connect(cache_path() / "targets.db")

cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS solarsystem_objects")

cursor.execute("CREATE TABLE solarsystem_objects(" 
               "pk INTEGER PRIMARY KEY AUTOINCREMENT," 
               "favorite INTEGER," 
               "name TEXT," 
               "ephemeris_key TEXT)")

# JPL Ephemeris de421 keys
de421 = [
    ["Mercury", "Mercury"],
    ["Venus", "Venus"],
    ["Earth", "Earth"],
    ["Moon", "The Moon"],
    ["Mars", "Mars"],
    ["Jupiter Barycenter", "Jupiter"],
    ["Saturn Barycenter", "Saturn"],
    ["Uranus Barycenter", "Uranus"],
    ["Neptune Barycenter", "Neptune"],
    ["Pluto Barycenter", "Pluto"],
    ["Sun", "The Sun",],
]

for key in de421:
    data = (False, key[1], key[0])
    cursor.execute("INSERT INTO solarsystem_objects (favorite, name, ephemeris_key) VALUES (?, ?, ?)", data)

connection.commit()


# Handle creation of Messier objects table

cursor.execute("DROP TABLE IF EXISTS messier_objects")

cursor.execute("CREATE TABLE messier_objects("
               "pk INTEGER PRIMARY KEY AUTOINCREMENT,"
               "favorite INTEGER,"
               "m TEXT,"
               "alt_name TEXT,"
               "ra REAL,"
               "dec REAL,"
               "dist REAL)")

df = pandas.read_csv("./data_sources/messier_catalog.tsv", sep="\t")


def parse_ra(ra):
    s = ra.split("h")
    h = float(s[0]) * 360.0 / 24.0
    m = float(s[1].replace("m", "")) * 15.0 / 60.0
    return h + m


def parse_dec(dec):
    is_negative = dec.startswith("-")
    s = dec.split("°")
    deg = float(s[0])
    m = float(s[1]) / 60.0

    return deg + m * (-1.0 if is_negative else 1.0)


for index, row in df.iterrows():
    favorited = False
    m = row["M"]
    alt_name = row["NGC"] if "NGC" not in row["NGC"] else ' '.join(row["NGC"].split(' ')[2:])

    if alt_name == '':
        alt_name = f"Messier {m[1:]}"

    ra = parse_ra(row["RA"])
    dec = parse_dec(row["DEC"])
    dist = float(row["DIST (ly)"].replace(",", ""))

    data = (favorited, m, alt_name, ra, dec, dist)

    cursor.execute(
        "INSERT INTO messier_objects (favorite, m, alt_name, ra, dec, dist) " \
        "VALUES (?, ?, ?, ?, ?, ?)",
        data)

connection.commit()

# Handle creation of star table

cursor.execute("DROP TABLE IF EXISTS stars")

cursor.execute("CREATE TABLE stars("
               "pk INTEGER PRIMARY KEY AUTOINCREMENT,"
               "favorite INTEGER,"
               "name TEXT,"
               "ra REAL,"
               "dec REAL)")

df = pandas.read_csv("./data_sources/IAU-CSN.tsv", sep="\t")


for index, row in df.iterrows():
    favorited = False
    name = row["Name/ASCII"]
    ra = row["RA(J2000)"]
    dec = row["Dec(J2000)"]

    data = (favorited, name, ra, dec)

    cursor.execute(
        "INSERT INTO stars (favorite, name, ra, dec) "
        "VALUES (?, ?, ?, ?)",
        data)

connection.commit()
