import sqlite3
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run

DATABASE_NAME = "ski_resorts.db"

##############################################
# GROUP A Skill: Cross-table parameterised SQL
##############################################
def add_resort_to_database(ski_resort_object, new_resort_name): #Adds a newly created ski resort into the database
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            for node in ski_resort_object.resorts[new_resort_name].nodes.values(): #Inserts the nodes of the ski resort into the database
                node_insertion = """INSERT INTO nodes (node_name, resort_name, altitude, node_type, ski_park_length, amenity_type)
                                    VALUES (?,?,?,?,?,?);"""
                cursor.execute(node_insertion, [node.name, new_resort_name, node.altitude, node.node_type, node.length, node.amenity_type])
            for node in ski_resort_object.resorts[new_resort_name].nodes.values(): #Inserts the runs of the ski resort into the database
                select_node_id = "SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?;"
                cursor.execute(select_node_id, [node.name, new_resort_name])
                node_id = cursor.fetchone()[0]
                for run in node.runs:
                    end_node_id_select = "SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?;"
                    cursor.execute(end_node_id_select, [run.name, new_resort_name])
                    end_node_id = cursor.fetchone()[0]
                    run_insertion = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing, lift, difficulty, lift_type)
                                    VALUES (?,?,?,?,?,?,?,?);"""
                    cursor.execute(run_insertion, [node_id, end_node_id, run.length, run.opening, run.closing, run.lift, run.difficulty, run.lift_type])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)

def sync_from_database(ski_resort_object): #Copies the ski resorts from the database to a local data structure of the ski resorts as objects
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            ski_resort_query = "SELECT resort_name FROM nodes;"
            cursor.execute(ski_resort_query)
            resort_names = set(cursor.fetchall())
            for resort in resort_names: #Adds the ski resorts to the local data structure
                ski_resort_object.add_resort(resort[0])
                node_query = "SELECT node_id, node_name, altitude, node_type, ski_park_length, amenity_type FROM nodes WHERE resort_name=?;"
                cursor.execute(node_query, [resort[0]])
                nodes = cursor.fetchall()
                for node in nodes: #Adds the nodes of the ski resort to the local data structure
                    node_type = node[3]
                    if node_type == "Ski lift station":
                        ski_resort_object.resorts[resort[0]].add_ski_node(node[1],node[2])
                    elif node_type == "Amenity":
                        ski_resort_object.resorts[resort[0]].add_amenity(node[1],node[2],node[5])
                    elif node_type == "Ski park":
                        ski_resort_object.resorts[resort[0]].add_ski_park(node[1],node[2],node[4])                    
                    run_query = "SELECT * FROM runs WHERE node_id=?;"
                    cursor.execute(run_query, [node[0]])
                    runs = cursor.fetchall()
                    for run in runs: #Adds the runs of the ski resort to the local data structure
                        end_node_name_select = "SELECT node_name FROM nodes WHERE node_id=?;"
                        cursor.execute(end_node_name_select, [run[2]])
                        end_node_name = cursor.fetchone()[0]
                        ski_resort_object.resorts[resort[0]].nodes[node[1]].add_run(end_node_name, run[3], run[4], run[5], run[6], run[7], run[8])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)
    return ski_resort_object