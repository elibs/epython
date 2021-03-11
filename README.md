# EPython

The purpose of this library is to provide helper abstractions on top of well known libraries.
The idea is to harden existing technologies and build easy-to-use wrappers for incorporation 
in test or production python code.

## Overrides

There are instances when retry logic needs to be tweaked to make tests more performant, or 
more hardened. For this purpose, there are environmental variables that can be set to change 
the retry behavior. 

Below are the current overrides that are available:

Env Variable | Default | Description
------------ | ------- | -------------
EPYTHON_LOG_LEVEL | INFO | Control the epython logging level
EPYTHON_LOG_FILE | None | Set this to have all epython output logging to a file
EPYTHON_SSH_KEY | None | Private SSH key to use
EPYTHON_SSH_RETRIES | 3 | The number of times to retry an ssh login operation
EPYTHON_SSH_RETRY_INTERVAL | 5 | The time to wait before a new ssh attempt
