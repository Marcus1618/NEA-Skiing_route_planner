import sqlite3
from ski_resorts import Ski_resorts, Ski_resort, Ski_node, Run

DATABASE_NAME = "ski_resorts.db"

def add_resort_to_database(ski_resort_object, new_resort_name):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            for node in ski_resort_object.resorts[new_resort_name].nodes.values():
                node_insertion = """INSERT INTO nodes (node_name, resort_name)
                                    VALUES (?,?);"""
                cursor.execute(node_insertion, [node.name, new_resort_name])
                select_node_id = "SELECT node_id FROM nodes WHERE node_name=? AND resort_name=?;"
                cursor.execute(select_node_id, [node.name, new_resort_name])
                node_id = cursor.fetchone()[0]
                for run in node.runs:
                    run_insertion = """INSERT INTO runs (node_id, end_node_id, run_length, opening, closing)
                                    VALUES (?,?,?,?,?);"""
                    cursor.execute(run_insertion, [node_id, run.name, run.length, run.opening, run.closing])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)

def sync_from_database(ski_resort_object):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            ski_resort_query = "SELECT resort_name FROM nodes;"
            cursor.execute(ski_resort_query)
            resort_names = set(cursor.fetchall())
            for resort in resort_names:
                ski_resort_object.add_resort(resort[0])
                node_query = "SELECT node_id, node_name FROM nodes WHERE resort_name=?;"
                cursor.execute(node_query, [resort[0]])
                nodes = cursor.fetchall()
                for node in nodes:
                    ski_resort_object.resorts[resort[0]].add_ski_node(node[1])
                    run_query = "SELECT * FROM runs WHERE node_id=?;"
                    cursor.execute(run_query, [node[0]])
                    runs = cursor.fetchall()
                    for run in runs:
                        ski_resort_object.resorts[resort[0]].nodes[node[1]].add_run(run[2], run[3], run[4], run[5])
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)
    return ski_resort_object