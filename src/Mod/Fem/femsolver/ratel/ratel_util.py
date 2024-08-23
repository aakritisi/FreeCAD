import subprocess
from platform import system

def get_location(name):
    if system() in ("Linux", "Darwin"):
        command = "find / -type d -name '" + name + "' -exec test -d \"{}/.git\" \\; -print 2>/dev/null"
    elif system() == "Windows":
        command = "for /d /r C:\\ %%d in (" + name + ") do if exist \"%%d\\.git\" echo %%d"
    else:
        command = "find / -type d -name '" + name + "' -exec test -d \"{}/.git\" \\; -print 2>/dev/null"
    
    # Execute the command using Popen
    with subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    ) as process:
        # Capture the output and errors
        output, errors = process.communicate()

    # Decode the output and errors from bytes to string
    output = output.decode('utf-8').strip()
    errors = errors.decode('utf-8')
    
    # Print the results
    if output:
        return output, ""
    elif errors:
        return "", errors