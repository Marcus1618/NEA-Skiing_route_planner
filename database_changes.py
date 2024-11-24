import sqlite3
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run

DATABASE_NAME = "ski_resorts.db"

def sync_to_database(ski_resort_object, updating_resort_name):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            #check if ski_resort_name is already in database
            ski_resort_query = "SELECT ski_resort_name FROM ski_resorts;"
            cursor.execute(ski_resort_query)
            pre_existing_resorts = cursor.fetchall()
            if updating_resort_name not in pre_existing_resorts:
                ski_resort_record = "INSERT INTO ski_resorts(ski_resort_name) VALUES (?);"
                cursor.execute(ski_resort_record, [updating_resort_name])
                ski_resort_creation = f"CREATE TABLE IF NOT EXISTS {updating_resort_name} (node_name TEXT PRIMARY KEY, ski_resort_name TEXT);"
                cursor.execute(ski_resort_creation)
                for node in ski_resort_object.resorts[updating_resort_name].nodes.values():
                    node_insertion = f"INSERT INTO {updating_resort_name} (node_name, ski_resort_name) VALUES (?, ?);"
                    cursor.execute(node_insertion, [node.name, updating_resort_name])
                    node_creation = f"CREATE TABLE IF NOT EXISTS {node.name} (run_ID INTEGER PRIMARY KEY,node_name TEXT, end_node TEXT, run_length INTEGER, opening TEXT, closing TEXT);"
                    cursor.execute(node_creation)
                    for i,run in enumerate(node.runs):
                        run_insertion = f"INSERT INTO {node.name} (run_ID, node_name, end_node, run_length, opening, closing) VALUES (?, ?, ?, ?, ?, ?);"
                        cursor.execute(run_insertion, [i, node.name, run.name, run.length, run.opening, run.closing])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)

def sync_from_database(ski_resort_object):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            ski_resort_query = "SELECT ski_resort_name FROM ski_resorts;"
            cursor.execute(ski_resort_query)
            pre_existing_resorts = cursor.fetchall()
            for resort in pre_existing_resorts:
                ski_resort_object.add_resort(resort[0])
                node_query = "SELECT node_name FROM ?;"
                cursor.execute(node_query, [resort[0]])
                nodes = cursor.fetchall()
                for node in nodes:
                    ski_resort_object.resorts[resort[0]].add_ski_node(node[0])
                    run_query = "SELECT * FROM ?;"
                    cursor.execute(run_query, [node[0]])
                    runs = cursor.fetchall()
                    for run in runs:
                        ski_resort_object.resorts[resort[0]].nodes[node[0]].add_run(run[1], run[3], run[4], run[5])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)
    return ski_resort_object