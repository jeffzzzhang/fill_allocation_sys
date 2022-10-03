
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

Here is the architecture diagram.
![System architecture](https://github.com/jeffzzzhang/fill_allocation_sys/blob/main/images/Screen%20Shot%202022-10-03%20at%203.19.37%20AM.png)

## Manual
Simply run `docker-compose up` to build images and containers, and launch services. 

Here is a snapshoot of running results. 
![Running snapshot](https://github.com/jeffzzzhang/fill_allocation_sys/blob/main/images/Screen%20Shot%202022-10-03%20at%202.24.47%20AM.png)

And also the content printed by position server at a specific moment
```
{'account1': {'stock_07': 930.0, 'stock_05': 941.0, 'stock_02': 1175.0, 'stock_03': 843.0, 
'stock_08': 1022.0, 'stock_01': 1143.0, 'stock_10': 1000.0, 'stock_04': 1060.0, 'stock_06': 1132.0, 
'stock_09': 1014.0}, 'account2': {'stock_07': 1184.0, 'stock_05': 955.0, 'stock_02': 1143.0, 
'stock_03': 864.0, 'stock_08': 1151.0, 'stock_01': 1109.0, 'stock_10': 999.0, 'stock_04': 929.0, 
'stock_06': 1062.0, 'stock_09': 829.0}, 'account3': {'stock_07': 1011.0, 'stock_05': 849.0, 
'stock_02': 955.0, 'stock_03': 790.0, 'stock_08': 887.0, 'stock_01': 1001.0, 'stock_10': 950.0, 
'stock_04': 940.0, 'stock_06': 772.0, 'stock_09': 830.0}, 'account4': {'stock_07': 705.0, 
'stock_05': 542.0, 'stock_02': 735.0, 'stock_03': 653.0, 'stock_08': 726.0, 'stock_01': 706.0, 
'stock_10': 779.0, 'stock_04': 709.0, 'stock_06': 555.0, 'stock_09': 589.0}, 
'account5': {'stock_07': 195.0, 'stock_05': 153.0, 'stock_02': 219.0, 'stock_03': 108.0, 
'stock_08': 293.0, 'stock_01': 153.0, 'stock_10': 164.0, 'stock_04': 205.0, 'stock_06': 267.0, 
'stock_09': 278.0}}
```

## Files
* `app_position.py`: the entry function of the position server, by running `python app_position.py` to launch the server.
* `app_controller.py`: the entry function of the controller server, `python app_controller.py` to launch the server.
* `server_simulator.py`: simulating 1) fill server, 2) AUM server, and 3) worker of controller server. Fill server generates new fills at a random gap and post to controller server. AUM server conducts similar task, at a fixed time gap, though. Worker of controller server periodically check  message queue to conduct fill and position update.
* `constants.py`: some constants frequently called.
* `~/images/`: directory for architecture diagram and a snapshot.
* `Dockerfile_ctrl/post/server_simulator`: Dockerfiles for each function
* `docker-compose.yml`: docker compose file
