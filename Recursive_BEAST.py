with open("primate-thisisatest-tn93.log", "r") as log_file:
	data = data.readlines()
	data = [line.spllit() for line in data if line[:1] != '#']
	data = zip(*data)