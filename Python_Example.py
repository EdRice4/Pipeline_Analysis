# Import the module
import subprocess

# Ask the user for input
host = raw_input("Enter a host to ping: ")	

# Set up the echo command and direct the output to a pipe
p1 = subprocess.Popen(['ping', '-c 2', host], stdout=subprocess.PIPE)

# Run the command
output = p1.communicate()[0]

print output
