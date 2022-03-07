#!/usr/bin/env python3


from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)
    """
    nodes_data = read_osm_data(nodes_filename)
    ways_data = read_osm_data(ways_filename)
    #intiializes dictionary of nodes containing neighbor id to speed limit dictionary
    node_info = {
        #'id1': {'neighbors': [(neighbor id, speed limit)  ,   ],  'location': ( 'lat'  , 'lon' ) } 
    }
    nodes_id = set()

    #Retrieves valid nodes from way
    for way in ways_data:
        if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            speed_limit = 0
             #checks for speed limit
            if 'maxspeed_mph' in way['tags']:
                speed_limit = way['tags']['maxspeed_mph']
            else:
                highway_type = way['tags']['highway']
                speed_limit = DEFAULT_SPEED_LIMIT_MPH[highway_type]
            for index in range(len(way['nodes'])):
                if str(way['nodes'][index]) not in node_info:
                    node_info[str(way['nodes'][index])] = {'neighbors': [], 'location': tuple()} #initiates the dictionary only once
                    nodes_id.add(way['nodes'][index]) #adds node id to the set of node ids
                    #checks if way is oneway
                if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes':
                    if index < len(way['nodes'])-1: #appends neighbors for one way
                        node_info[str(way['nodes'][index])]['neighbors'].append((way['nodes'][index+1], speed_limit))
                else:
                    if index < len(way['nodes'])-1: #appends neighbors in increasing order
                        node_info[str(way['nodes'][index])]['neighbors'].append((way['nodes'][index+1], speed_limit))
                    if index - 1 >= 0: #appends neighbors in decreasing order
                        node_info[str(way['nodes'][index])]['neighbors'].append((way['nodes'][index-1], speed_limit))

    #find relevant node information and latitude/longitude and adds to the dictionary representation
    for node in nodes_data:
        if node['id'] in nodes_id:
            node_info[str(node['id'])]['location'] = (node['lat'], node['lon'])

    return node_info

def find_short_path_nodes(map_rep, node1, node2, speed_check = False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    #base case where we start at the end goal
    if node1 == node2:
        return [node1]
    
    #current node, distance traveled
    agenda = [(node1, 0, [node1])]
    expanded = set()

    while agenda:
        #finds shortest distance in agenda
        
        min_cost = min(agenda, key = lambda x: x[1])
        agenda.remove(min_cost)
        index = 0
        #checks if current node is in visited set, if it is, go on to next node
        if min_cost[0] not in expanded:
            expanded.add(min_cost[0])
        else:
            continue
        
        #checks if smallest cost has been found
        if min_cost[0] == node2:
            return min_cost[2]
        #Gets location of current node
        current_lat = map_rep[str(min_cost[0])]['location'][0]
        current_lon = map_rep[str(min_cost[0])]['location'][1]
        for neighbors in map_rep[str(min_cost[0])]['neighbors']:
            if neighbors[0] not in expanded:
                #gets location of neighbor node
                neighbor_lat = map_rep[str(neighbors[0])]['location'][0]
                neighbor_lon = map_rep[str(neighbors[0])]['location'][1]
                #gets distance between current and neighbor node
                distance = great_circle_distance((current_lat, current_lon), (neighbor_lat, neighbor_lon))
                if speed_check == True:
                    distance = distance/neighbors[1]
                agenda.append((neighbors[0], min_cost[1] + distance, min_cost[2] + [neighbors[0]]))
    return None

    
    


def find_short_path(map_rep, loc1, loc2, with_fast = False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    dist1 = 1000000000000000
    dist2= 10000000000000000

    for i in map_rep:
        if dist1 > great_circle_distance(map_rep[i]['location'],loc1):
            node_one = i
            dist1 = great_circle_distance(map_rep[i]['location'],loc1)
        if dist2 > great_circle_distance(map_rep[i]['location'],loc2):
            node_two = i
            dist2 = great_circle_distance(map_rep[i]['location'],loc2)
    path = find_short_path_nodes(map_rep,int(node_one),int(node_two),with_fast)
    if path != None:
        return [map_rep[str(i)]['location'] for i in path]
    return None

    
   
def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    return find_short_path(map_rep,loc1,loc2,True)
    


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    # nodes_cambridge = read_osm_data('resources/cambridge.nodes')
    # ways_cambridge = read_osm_data('resources/cambridge.ways')
    # nodes_midwest = read_osm_data('resources/midwest.nodes')
    # ways_midwest = read_osm_data('resources/midwest.ways')   
    #print(next(data)) 
    # for node in nodes_data:
    #     if 'name' in node['tags'] and node['tags']['name'] == '77 Massachusetts Ave':
    #         #print (node['id'])
    # count = 0
    # nodes_set = set()
    # for way in ways_cambridge: 
    #     if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes':
    #         print(way['tags'])
    #     if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
    #         for node in way['nodes']:
    #                 nodes_set.add(node)
    # #print(len(nodes_set))
    # distance = great_circle_distance((42.363745, -71.100999) , (42.361283, -71.239677))
    
    lat1 = 0
    lon1 = 0
    lat2 = 0
    lon2 = 0
    # for node in nodes_midwest:
    #     if node['id'] == 233941454:
    #         lat1 = node['lat']
    #         lon1 = node['lon']
    #     elif node['id'] == 233947199:
    #         lat2 = node['lat']
    #         lon2 = node['lon']    
    # print(great_circle_distance((lat1, lon1), (lat2, lon2)))
    # list_of_id = []
    # for way in ways_midwest:
    #     if way['id'] == 21705939:
    #         for id in (way['nodes']):
    #             list_of_id.append(id)
    #         else:
    #             continue
    #         break
    # distance = 0
    # list_of_nodes = []
    # for id in list_of_id:
    #     for node in nodes_midwest:
    #         if node['id'] == id:
    #             list_of_nodes.append(node)
    #             break
    # for index in range(len(list_of_nodes)-1):
    #     distance += great_circle_distance((list_of_nodes[index]['lat'] , list_of_nodes[index]['lon'] ),  (list_of_nodes[index+1]['lat']  ,  list_of_nodes[index+1]['lon'] )   )
    # print(distance)
    map = (build_internal_representation('resources/mit.nodes', 'resources/mit.ways'))
    loc1 = (42.355, -71.1009) # New House
    loc2 = (42.3612, -71.092) # 34-501
    print(find_short_path(map,loc1,loc2))

