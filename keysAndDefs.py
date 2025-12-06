from utils import *

BASES = 'bases'
ACTUAL = 'actual'
PLANNED = 'planned'
REMOVE = 'remove'
NEARBY = 'nearby'

BENCHES = 'benches'
WORK_BENCH = 'workbench'
FURN_BENCH = 'furniture'
FORGE = 'forge'
MILL_MACH = 'milling'
BEAR_BED = 'bearbed'
BED = 'bed'
RADIO = 'radio'
TRADER = 'trader'

RABBIT = 'rabbit'
PTARMIGAN = 'ptarmigan'
DEER = 'deer'
WOLF = 'wolf'
POISON_WOLF = 'poisonwolf'
TIMBERWOLF = 'timberwolf'
BEAR = 'bear'
MOOSE = 'moose'
FISH = 'fish'
SALT = 'salt'
BIRCH = 'birch'
COAL = 'coal'
BEACHCOMBING = 'beachcombing'

COOKPOT = 'cookpot'
SKILLET = 'skillet'
CURING_BOX = 'curing'
TRUNK = 'trunk'
SUITCASE = 'suitcase'
ROCK_CACHE = 'rockcache'

TOOLS = 'tools'
WOODWORKING = 'woodworking'
QUALITY_TOOLS = 'quality'
SIMPLE_TOOLS = 'simple'
HAMMER = 'hammer'
HACKSAW = 'hacksaw'
PRYBAR = 'prybar'
LANTERN = 'lantern'
VICE = 'vice'

DISTRESS_PISTOL = 'distress'
DISTRESS_PISTOL_AMMO = 'dpammo'

STOVE = 'stove'
POTBELLY = 'potbelly'
GRILL = 'grill'
RANGE = 'range'
NOSTOVE = 'nostove'
STOVE_LST = [POTBELLY, GRILL, RANGE]
STOVE_TYPES = {0: NOSTOVE, 1:POTBELLY, 2:GRILL, 6:RANGE}

MAGLENS = 'maglens'
MATCHES = 'matches'
FIRESTRIKER = 'firestriker'
BEDROLL = 'bedroll'

FEATURES = 'features'
CUSTOMIZABLE = 'customizable'
LOADING = 'loading'
CONNECTIONS = 'connections'
INDOORS = 'indoors'
EMPTY = 'empty'
EXPLORED = 'explored'
CABINFEVERRISK = 'cabinfeverrisk'

SOUTH = 'south'
NORTH = 'north'
EAST = 'east'
WEST = 'west'
BOTTOM = 'bottom'
TOP= 'top'
LEFT = 'left'
RIGHT = 'right'
REVERSE = {SOUTH:NORTH, NORTH:SOUTH, EAST:WEST, WEST:EAST, BOTTOM:TOP, TOP:BOTTOM, LEFT:RIGHT, RIGHT:LEFT}

# the colours provided
COLOURS = 'colours'
BASE = 'base'
BASE_BG = 'basebg'
FIR = 'fir'
CEDAR = 'cedar'
STONE = 'rock'
BRING = 'bring'
TAKE = 'take'
DESTROY = 'destroy'

# assets
ASSETS = {BEAR_BED:'bearbed.svg', BED:'bed.svg',
          FORGE:'forge.svg',  MILL_MACH:'milling.svg',
          FURN_BENCH:'furnbench.svg', WORK_BENCH:'workbench.svg',
          TRUNK:'trunk.svg', CURING_BOX:'curing.svg',
          COOKPOT:'cookpot.svg', SKILLET:'skillet.svg',
          POTBELLY:'potbelly.svg', GRILL:'grill.svg', RANGE:'range.svg',
          HACKSAW:'hacksaw.svg', QUALITY_TOOLS:'qualitytools.svg', SIMPLE_TOOLS:'simpletools.svg',
          LANTERN:'lantern.svg', PRYBAR:'prybar.svg',
          WOODWORKING:'woodworking.svg', HAMMER:'hammer.svg',
          SUITCASE:'suitcase.svg', VICE:'vice.svg',
          RADIO:'radio.svg', TRADER:'trader.svg',
          BEAR:'bear.svg',WOLF:'wolf.svg',POISON_WOLF:"poisonwolf.svg",
          DEER:'deer.svg',RABBIT:'rabbit.svg',PTARMIGAN:'ptarmigan.svg',
          MOOSE:'moose.svg',TIMBERWOLF:'timberwolf.svg',
          SALT:'salt.svg', BEACHCOMBING:'beachcombing.svg', COAL:'coal.svg', FISH:'fish.svg',
          BIRCH:'birch.svg', ROCK_CACHE:"rockcache.svg",
          EMPTY:'empty.svg',
          MAGLENS:'maglens.svg', MATCHES:'matches.svg', FIRESTRIKER:"firestriker.svg",
          DISTRESS_PISTOL:'distresspistol.svg', DISTRESS_PISTOL_AMMO:"pistolammo.svg",
          BEDROLL:'bedroll.svg'
          }

MOVABLES = [CURING_BOX, COOKPOT, SKILLET, HACKSAW, QUALITY_TOOLS, SIMPLE_TOOLS,
            LANTERN, PRYBAR, WOODWORKING, HAMMER, SUITCASE, VICE,
            BEDROLL,MATCHES,FIRESTRIKER,MAGLENS, DISTRESS_PISTOL, DISTRESS_PISTOL_AMMO]

TODO_TYPES = {WORK_BENCH:CEDAR, FURN_BENCH:CEDAR, BEAR_BED:FIR, BED:FIR,
              CURING_BOX:FIR, TRUNK:FIR,
              ROCK_CACHE:STONE,
              COOKPOT:BRING, SKILLET:BRING, SUITCASE:BRING,
              QUALITY_TOOLS:BRING, HAMMER:BRING, HACKSAW:BRING, LANTERN:BRING
              }

CHARCOAL = 'charcoal'
CATTAIL = 'cattail'
TINDER = 'tinder'
ROAD = 'road'
RAIL = 'rail'
PATH = 'path'
TODO = 'todo'
PAINT = 'paint'
MIXED = 'mixed'
ONEWAY = 'oneway'

DASHSTYLE = {TODO:'1,2',
             CHARCOAL:'2,1',
             CATTAIL:'6,2',
             TINDER:'4,2',
             PAINT: '7,4',
             MIXED: '4,2,2,2', # '1,3,2',
             ROAD:'',
             RAIL:'',
             PATH : '',
             ONEWAY: '1,1',
             }

OUTDOOR_OPACITY = 0.25
FONTFAM = 'Arial'

CORN_X = 1
CORN_Y = 0
BIGNUM = 100000

ORDERING = {BED: BED, BEAR_BED: "bear hide bed",
            WORK_BENCH: WORK_BENCH, FURN_BENCH: "furniture workbench", FORGE: FORGE, MILL_MACH: "milling machine",
            RADIO: "trader radio", TRADER: "trade drop-box",
            POTBELLY: "1-slot stove", GRILL: "2-slot stove", RANGE: "6-slot stove",
            COOKPOT: COOKPOT, SKILLET: SKILLET,
            LANTERN: LANTERN, QUALITY_TOOLS: "quality tools", SIMPLE_TOOLS: 'simple tools',
            HACKSAW: HACKSAW, HAMMER: "heavy hammer", PRYBAR: PRYBAR, WOODWORKING: "woodworking tools",
            TRUNK: "rustic trunk", SUITCASE: "suitcase", ROCK_CACHE: "rock cache",
            CURING_BOX: "curing box", VICE: 'workbench vice',
            SALT: "salt deposit", COAL: "coal", BEACHCOMBING: "beachcombing", BIRCH: "birch bark",
            BEAR: BEAR, MOOSE: MOOSE, DEER: DEER, WOLF: WOLF, POISON_WOLF: 'poisoned wolf', TIMBERWOLF: TIMBERWOLF,
            RABBIT: RABBIT, PTARMIGAN: PTARMIGAN, FISH: 'fishing',
            MAGLENS:MAGLENS, FIRESTRIKER:FIRESTRIKER, MATCHES:MATCHES,
            DISTRESS_PISTOL:DISTRESS_PISTOL, DISTRESS_PISTOL_AMMO:"distress pistol ammo",
            BEDROLL:'bedroll (cloth)'
            }