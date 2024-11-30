from glob import glob
python = glob('*.py')

lines = 0
for file in python:
    with open(file) as f:
        lines += sum([line.strip() != "" and not line.startswith('#') for line in f]) 

print("{} code lines in {} files.".format(lines, len(python)))