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

TOOLS = 'tools'
WOODWORKING = 'woodworking'
QUALITY_TOOLS = 'quality'
HAMMER = 'hammer'
HACKSAW = 'hacksaw'
PRYBAR = 'prybar'
LANTERN = 'lantern'

STOVE = 'stove'
POTBELLY = 'potbelly'
GRILL = 'grill'
RANGE = 'range'
NOSTOVE = 'nostove'
STOVE_LST = [POTBELLY, GRILL, RANGE]
STOVE_TYPES = {0: NOSTOVE, 1:POTBELLY, 2:GRILL, 6:RANGE}

FEATURES = 'features'
CUSTOMIZABLE = 'customizable'
LOADING = 'loading'
CONNECTIONS = 'connections'
INDOORS = 'indoors'
EMPTY = 'empty'

SOUTH = 'south'
NORTH = 'north'
EAST = 'east'
WEST = 'west'

# the colours provided
COLOURS = 'colours'
BASE = 'base'
BASE_BG = 'basebg'
FIR = 'fir'
CEDAR = 'cedar'
BRING = 'bring'
TAKE = 'take'

# assets
ASSETS = {BEAR_BED:'bearbed.svg', BED:'bed.svg',
          FORGE:'forge.svg',  MILL_MACH:'milling.svg',
          FURN_BENCH:'furnbench.svg', WORK_BENCH:'workbench.svg',
          TRUNK:'trunk.svg', CURING_BOX:'curing.svg',
          COOKPOT:'cookpot.svg', SKILLET:'skillet.svg',
          POTBELLY:'potbelly.svg', GRILL:'grill.svg', RANGE:'range.svg',
          HACKSAW:'hacksaw.svg', QUALITY_TOOLS:'toolbox.svg', LANTERN:'lantern.svg', PRYBAR:'prybar.svg',
          WOODWORKING:'woodworking.svg', HAMMER:'hammer.svg',
          SUITCASE:'suitcase.svg',
          RADIO:'radio.svg', TRADER:'trader.svg',
          BEAR:'bear.svg',WOLF:'wolf.svg',POISON_WOLF:"poisonwolf.svg",
          DEER:'deer.svg',RABBIT:'rabbit.svg',PTARMIGAN:'ptarmigan.svg',
          MOOSE:'moose.svg',TIMBERWOLF:'timberwolf.svg',
          SALT:'salt.svg', BEACHCOMBING:'beachcombing.svg', COAL:'coal.svg', FISH:'fish.svg',
          BIRCH:'birch.svg',
          EMPTY:'empty.svg'
          }

TODO_TYPES = {WORK_BENCH:CEDAR, FURN_BENCH:CEDAR, BEAR_BED:FIR,
              CURING_BOX:FIR, TRUNK:FIR,
              COOKPOT:BRING, SKILLET:BRING, SUITCASE:BRING,
              QUALITY_TOOLS:BRING, HAMMER:BRING, HACKSAW:BRING, LANTERN:BRING
              }