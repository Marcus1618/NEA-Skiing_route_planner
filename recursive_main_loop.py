adjacent_nodes = self._ski_resort[chosen_node.name].runs
priorities = []

for node in adjacent_nodes:
    value = 0
    values = []
    temp_time_elapsed = time_elapsed + node.length
    adjacent_nodes_1 = self._ski_resort[node.name].runs
    self._ski_resort_object.increment_time(node.length)

    for node_1 in adjacent_nodes_1:
        value1 = value + 0
        temp_time_elapsed1 = temp_time_elapsed + node_1.length
        adjacent_nodes_2 = self._ski_resort[node_1.name].runs
        self._ski_resort_object.increment_time(node_1.length)

        for node_2 in adjacent_nodes_2:
            value2 = value1 + 0
            temp_time_elapsed2 = temp_time_elapsed1 + node_2.length
            times,prev = self._djikstras_traversal(node_2.name)
            time_from_start = times[self._start]
            time_value = 0
            time_value = self._length - temp_time_elapsed2 - time_from_start
            if time_value < 0:
                values.append(time_value)
            else:
                values.append(value2)
        self._ski_resort_object.decrement_time(node_1.length)
    self._ski_resort_object.decrement_time(node.length)
    priorities.append(max(values))

#Recursive definition
find_priorities = []
adjacent_nodes = self._ski_resort[chosen_node.name].runs
count = 0
temp_time_elapsed = time_elapsed
value = 0
priorities = find_values(adjacent_nodes,count,temp_time_elapsed, find_priorities, value)

def find_values(adjacent_nodes,count,temp_time_elapsed, priorities, value):
    if count >= 2:
        values = []
        for node_1 in adjacent_nodes:
            temp_time_elapsed += node_1.length
            times, prev = self._djikstras_traversal(node_1.name)
            time_from_start = times[self._start]
            time_value = 0
            time_value = self._length - temp_time_elapsed - time_from_start
            node_value = get_value()
            value += node_value
            if time_value < 0:
                values.append(time_value)
            else:
                values.append(value)
            temp_time_elapsed -= node_1.length
            value -= get_value()
        count -= 1
    for node in adjacent_nodes:
        if count == 0:
            priorities.append(max(values))
        count += 1
        temp_time_elapsed += node.length
        self._ski_resort_object.increment_time(node.length)
        node_value = get_value()
        value += node_value
        find_values(self._ski_resort[node.name].runs, count, temp_time_elapsed, priorities, value)
        value -= node_value
        self._ski_resort_object.decrement_time(node.length)
        temp_time_elapsed -= node.length

    return priorities