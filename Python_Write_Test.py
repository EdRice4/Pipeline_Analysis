with open("garli.conf", "r+") as garli_conf:
	configuration = garli_conf.readlines()
	for value in configuration:
		if value.find("datafname") != -1:
			 configuration[value] = "datafname = sequencefile"
# with open("garli.conf", "w") as garli_conf:
	# garli_conf.writelines(new_text)
print configuration