from TLDBaseViz import *


def load_info(filename='mybases.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    bases = data[BASES]
    edges = data[CONNECTIONS]
    return bases, edges


def icon_info():
    """
    :return:
    >>> info = icon_info()
    >>> info['bear']
    bear:bear:bring:29.38:False
    """
    icon_info = {}
    for i in ICONS:
        icon_info[i.key] = i
    return icon_info


def loot_info(filename='loottables.json', round_to=4, loot_table = 'Loot4'):
    """
    Use loottables.json to add features to the template.
    :return: dictionary of {location name : feature to add}
    >>> adds = loot_info()
    >>> greym = adds['Greymother']
    >>> len(greym) > 5
    True
    >>> '?matches/1.0' in greym
    True
    >>> '?saltbag/1.0' in adds['PVFarmhouse']
    True
    >>> '?maglens/1.0' in adds['CampOffice'] and '?saltbag/.3' in adds['CampOffice']
    True
    >>> '?saltbag/.75' in adds['RuralStore']
    True
    """
    data = {}
    with open(filename, 'r') as f:
        data = json.load(f)
    per_item = data['ByTotal']

    bases = {}

    loots = data[loot_table]
    for region in loots:
        for thing in loots[region]:
            n = len(loots[region][thing])
            prob = round(1  / n, round_to)
            for pot_loc in loots[region][thing]:
                loc = pot_loc
                #print(region, thing, pot_loc, n)
                if loc not in bases:
                    bases[loc] = []
                bases[loc].append(TOFIND + thing + PROBABILITY_DELIM + str(prob))

    for thing in per_item:
        entry = per_item[thing]
        locs = entry['locations']
        n = len(locs)
        if 'total' in entry:
            n = entry['total']
        #print(thing, n, 'total' in entry)

        for pot_loc in locs:
            loc = pot_loc
            if PROBABILITY_DELIM in loc:
                loc = pot_loc.split(PROBABILITY_DELIM)[0]
                prob = pot_loc.split(PROBABILITY_DELIM)[1]
            else:
                prob = round(n / len(locs), round_to)

            if loc not in bases:
                bases[loc] = []
            bases[loc].append(TOFIND + entry['key'] + PROBABILITY_DELIM + str(prob))

    return bases


def merge_in_adds(adds, bases):
    """
    Merge in to-add information
    :param adds:
    :param bases:
    :return:
    >>> fname = 'mybases.json'
    >>> adds = loot_info()
    >>> bases, colours = process_input(fname, to_print=False)
    >>> merge_in_adds(adds, bases)
    >>> bases['CampOffice'].features[-1] == adds['CampOffice']
    True
    >>> bases, colours = process_input(fname, to_print=False)
    >>> rb = reset_bases(bases)
    >>> merge_in_adds(adds, rb)
    >>> '?saltbag/.3' in rb['CampOffice']['features'][-1]
    True
    """
    for b in adds:
        if b in bases:
            if type(bases[b]) == BaseLocation:
                bases[b].features.append(adds[b])
                #print(bases[b].features)
            else:
                bases[b]['features'].append(', '.join(adds[b]))
                #print('type', )
        else:
            print('Warning:', b, "not in bases, can't add", adds[b])


def reset_bases(bases):
    """
    Reset the bases to default states.
    :param bases:
    :return: dict of dict for JSON output
    >>> bases, colours = process_input('tests/testinput.json', to_print=False)
    >>> rb = reset_bases(bases)
    """
    data = {}
    for b in bases:
        bob = bases[b]

        info = {}
        info[REGION] = bob.region
        info[COORDS] = bob.coords
        info[CUSTOMIZABLE] = bob.customizable
        info[LOADING] = bob.loading
        info[INDOORS] = bob.indoors
        info[CABINFEVERRISK] = bob.cabinfeverrisk

        info[EXPLORED] = False

        features = []
        for c in bob.features:
            for f in c:
                # reset all caches and transmitters
                if f.name in [ 'cache', 'transmitter', 'mementobox']:
                    features.append(TOPREPARE + f.name)
                elif f.name in ['climb']:
                    if f.status == ACTUAL:
                        if f.name not in ','.join(bob.removed):
                            features.append(f.name)
                elif f.name not in MOVABLES:
                    if f.status == ACTUAL:
                        if TODO_TYPES[f.name] in [BRING, TOBRING] and f.material != MOVED:
                            feat = f.name
                            if feat in CONTAINERS :
                                feat = TOFIND + feat
                            if f.qty > 1:
                                feat = feat + QTY_MARKER + str(f.qty)
                            if f.probability != 1:
                                feat = feat + PROBABILITY_DELIM + str(f.probability)
                            features.append(feat)

        for c in bob.removed:
            line = c.split(',')
            for f in line:
                if f.startswith(TOMAKE) or f.startswith(TOPREPARE):
                    feat = f.strip()
                else:
                    feat = TOFIND + f.strip()
                if len(feat) > 1:
                    features.append(feat)
                    #print(b, feat)

        info[FEATURES] = features #[','.join(features)]


        data[b] = info
        #print(b, info)
    return data


def cleanup_features(bases):
    """

    :param bases:
    :return:
    >>> bases, colours = process_input('tests/testinput.json', to_print=False)
    >>> rb = reset_bases(bases)
    >>> bases = cleanup_features(rb)
    >>> bases['Quonset']['explored']
    False
    >>> bases['Quonset']['features'][0]
    'bear,deer,wolf'
    """
    icons = icon_info()
    for b in bases:
        #print(b, bases[b][FEATURES])
        # TODO do the features in legend order?
        features = []
        curr_line = []
        last_feat = ''
        for f in bases[b][FEATURES]:
            feat_name = f.replace(TOFIND,'').replace(TOMAKE,'').replace(TOPREPARE,'')
            qty = 1
            if QTY_MARKER in feat_name:
                qty = feat_name.split(QTY_MARKER)[1]
                feat_name = feat_name.split(QTY_MARKER)[0]
            if PROBABILITY_DELIM in feat_name:
                feat_name = feat_name.split(PROBABILITY_DELIM)[0]

            add_as = f
            if qty != 1:
                add_as = f + QTY_MARKER + str(qty)
            if last_feat == '':
                last_feat = feat_name
            if icons[feat_name].theme != icons[last_feat].theme:
                featline = ','.join(curr_line)
                features.append(featline)
                #print('Featureline', featline, f)
                curr_line = [add_as]
            else:
                curr_line.append(add_as)
            last_feat = feat_name
            #print('Feature', f, type(f))
        if curr_line:
            features.append(','.join(curr_line))

        bases[b][FEATURES] = features
    return bases


def reset_edges(edges):
    """
    Reset the edges to default states.
    :param edges:
    :return: list of lists for JSON output
    >>> b, e, r = parse_input('tests/testinput.json')
    >>> edges = parse_edges(e)
    >>> reset_edges(edges)
    [['Hibernia', 'north', 'top,left', 'BrokenBridge', 'bottom,left', 'path'], ['Hibernia', 'south', 'bottom,left', 'Riken', 'top,left', 'default'], ['Hibernia', 'west', 'top,left', 'No5Mine', 'bottom,right', 'path'], ['Riken', 'east', 'top,right', 'LittleIsland', 'top,left', 'default'], ['No5Mine', 'west', 'bottom,left', 'No3Mine', 'top,right', 'path'], ['No3Mine', 'west', 'top,left', 'Harris', 'top,right', 'default'], ['Harris', 'west', 'top,left', 'CommuterCar', 'top,right', 'path'], ['CommuterCar', 'west', 'top,left', 'Misanthrope', 'top,right', 'default'], ['Misanthrope', 'west', 'top,left', 'JMFishHut', 'top,right', 'default'], ['Misanthrope', 'north', 'top,left', 'QMFishHut', 'bottom,left', 'default'], ['JMFishHut', 'west', 'top, left', 'Jackrabbit', 'top,right', 'default'], ['QMFishHut', 'west', 'top,left', 'MidFishHuts', 'top,right', 'default'], ['QMFishHut', 'north', 'top,left', 'Quonset', 'bottom,left', 'default'], ['Jackrabbit', 'north', 'top,left', 'JFFishHut', 'bottom,left', 'default'], ['Jackrabbit', 'north', 'top,right', 'MidFishHuts', 'bottom,left', 'default'], ['JFFishHut', 'east', 'top,right', 'MidFishHuts', 'top,left', 'default'], ['Quonset', 'west', 'top,left', 'LowerMine', 'bottom,right', 'path'], ['LowerMine', 'north', 'top,left', 'UpperMine', 'bottom,left', 'path'], ['UpperMine', 'west', 'top,left', 'MTFarm', 'bottom,right', 'default']]
    """
    seen = []
    connections = []
    connec = '---'
    for source in edges:
        for sink in edges[source]:
            key = source + connec + sink

            if key not in seen:
                cob = edges[source][sink]
                dir = cob.direction
                source_corner = cob.source_corner
                sink_corner = cob.sink_corner
                path_type = cob.kind
                if not path_type in ['default', 'fake', 'oneway', 'path']:
                    path_type = 'default'
                row = [source, dir, source_corner, sink, sink_corner, path_type]
                connections.append(row)
                seen.append(key)
                rev_seen = sink + connec + source
                seen.append(rev_seen)
                #print(row )

    return connections


def print_template(bases, edges, outname='output/template.json'):
    """

    :param filename:
    :return:
    >>> fname = 'mybases.json'
    >>> b, e, r = parse_input(fname)
    >>> edges = parse_edges(e)
    >>> edges = reset_edges(edges)
    >>> bases, colours = process_input(fname, to_print=False)
    >>> bases['Climb(BI)'] #  needs to be reset
    -
    Climb(BI)
    -
    [climb:actual:base]
    -
    >>> adds = loot_info()
    >>> rb = reset_bases(bases)
    >>> rb['PVFarmhouse']['explored']
    False
    >>> rb['Climb(BI)']['features']
    ['*climb']
    >>> rb['Climb(OSS-BP)']['features']
    ['climb']
    >>> merge_in_adds(adds, rb)
    >>> bases = cleanup_features(rb)
    >>> print_template(bases, edges)
    """
    data = {}
    data[BASES] = bases
    data[CONNECTIONS] = edges
    pretty_json = json.dumps(data, indent=4, separators=(',', ': '))
    with open(outname, 'w') as outfile:
        print(pretty_json, file=outfile)


def generate_template(input='mybases.json', output='templates/loot1.json', loot_table='Loot1'):
    """

    :param input:
    :param output:
    :param loot_table:
    :return:
    >>> #generate_template()
    """
    b, e, r = parse_input(input)
    edges = parse_edges(e)
    edges = reset_edges(edges)
    bases, colours = process_input(input, to_print=False)
    adds = loot_info(loot_table=loot_table)
    rb = reset_bases(bases)
    merge_in_adds(adds, rb)
    bases = cleanup_features(rb)
    print_template(bases, edges, outname=output)
    print(output)
    draw_bases_regionally_and_together(output, region_folder='templates/')


def average_loottables():
    """

    :return:
    >>> average_loottables()
    """
    for i in [1,2,3,4]:
        print('Loot Table', i)
        generate_template(loot_table=f'Loot{i}', output=f'templates/loot{i}.json')


if __name__ == '__main__':
    doctest.testmod()