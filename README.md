
## Problem Description
The controller receives trade fills from the fill servers in the following format at random intervals, there are only 10 different stocks available:
{stock ticker: <string out of 10 possibilities>, price: <random positive price>, quantity: <random quantity>}f
The controller receives random account splits from the AUM server at 30 second intervals.
{account1: <random percentage>, account2: <random percentage>, …, accountn: <random percentage>} 
The percentages should add up to 100%
The job of the controller is to keep track of positions held by each account, as new fills come in it tries to divide the stocks (in whole stocks) so that each account has an overall position that matches the split from the AUM server as closely as possible, i.e., each account is allocated a number of stocks so that the overall value of the fills they have is as closely proportional to their AUM percentage as possible. Previous trade fills cannot be rearranged after they have been allocated.
It should report the new overall positions to the position server at 10 second intervals, the position server should then print out the new positions/values.

## Solutions
For control server and position server, API is built with Python Flask. Control server and position server use port 9998 and 9999.

In the backend of control server, a message queue is adopted to save tasks from fill server and AUM server. Every time the control server is called with a POST method, the message in the request is pushed into MQ. A worker of control server fetch messages from queue every 10 seconds and conducts corresponding task, i.e., update fill and position in each account and post to position server.

About the fill server, AUM server and worker of control server, I simply launched 3 threads for them and perform related work based on their predefined time gap.

Redis list is adopted as the message queue, given that it is thread-safe. 

Docker is used as well.

Data structure in the request sent by controller server is as `{'accountn': {'stock1': quantity1, 'stock2': quantity2}}`.

## Manual
Simply run `docker-compose up` to build images and containers, and launch services. Here is a snapshoot of running results. 

## Files
* `app_position.py`: the entry function of the position server, by running `python app_position.py` to launch the server.
* `app_controller.py`: the entry function of the controller server, `python app_controller.py` to launch the server.
* `server_simulator.py`: simulating 1) fill server, 2) AUM server, and 3) worker of controller server. Fill server generates new fills at a random gap and post to controller server. AUM server conducts similar task, at a fixed time gap, though. Worker of controller server periodically check  message queue to conduct fill and position update.
* `constants.py`: some constants frequently called.
* `~/images/`: directory for architecture diagram and a snapshot.
* `Dockerfile_ctrl/post/server_simulator`: Dockerfiles for each function
* `docker-compose.yml`: docker compose file
