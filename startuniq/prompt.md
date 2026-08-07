AI prompts, used in creating the scripts.

## startuniq.py:
### Original
Create python script startuniq.py.
It should start as 
    startuniq.py -s RemoteHost Program

It should check that no Program is running on Remote host.
If Program is running, the script should display warning dialog and exit.
If Program is not running, then it should be launched using ssh connection to the host.

### Update
In startuniq.py:
If Program is already running display dialog instead of warning.
Dialog shoul have a button Kill. If it is pressed then the remote program should be terminated.

