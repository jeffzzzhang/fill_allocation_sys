import time
import json
import random
import logging
import threading
import concurrent.futures 
import redis
import requests
from constants import constants as cnst

def fill_server():
    """
    Mimic fill server - send fill info at a random gap
    """
    while True:
        logging.info("fill server: START")
        logging.info(f"""fill server: about to generate fills""")
        fills = generate_fills()
        logging.info("fill server: fills generated")
        tmp = post_requests(fills)
        print('tmp=',tmp)
        # logging.info('DEBUG: tmp = ', tmp)
        if str(tmp).startswith('20'):
            logging.info("fill server: request sending SUCCESSFULLY")
        else:
            logging.info("fill server: request sending FAILED")

        pause_random = random.uniform(1,10)
        logging.info(f"""fill server: suspending in next {pause_random} seconds""")
        time.sleep(pause_random) 
        logging.info("fill server: END")

def generate_fills():
    # generate new fills
    stock_pool = ['stock_01', 'stock_02', 'stock_03', 'stock_04', 'stock_05', \
                  'stock_06', 'stock_07', 'stock_08', 'stock_09', 'stock_10']
    stock = random.sample(stock_pool,1)[0]
    price = random.randint(10,50)
    quantity = random.randint(20,40)
    results = {'stock_ticker': stock, 'price': price, 'quantity': quantity}
    return results

def post_requests(fi, url=cnst.url_ctrl_server):
    # post to controller server by default
    try:
        if isinstance(fi, dict):
            tmp = requests.post(url=url, data=fi)
        elif isinstance(fi, str):
            # json type
            tmp = requests.post(url=url, json=fi)
        res = tmp.status_code
        tmp.close()
        return res # tmp.status_code
    except:
        return '999'

def aum_server():
    """
    Mimic aum server - send split info at a 30-seconde gap
    """
    while True:
        logging.info("aum server: START")
        logging.info("aum server: about to generate new split")
        # generate_accounts.delay()
        new_split = generate_split()
        logging.info("aum server: new split generated")
        tmp = post_requests(new_split)
        # logging.info('AUM_SERVER DEBUG: tmp = ', tmp)
        if str(tmp).startswith('20'):
            logging.info("aum server: request sending SUCCESSFULLY")
        else:
            logging.info("aum server: request sending FAILED")

        pause_gap = 30
        logging.info(f"""aum server: suspending in next {pause_gap} seconds""") 
        time.sleep(pause_gap)

def generate_split():
    '''
    generate accounts split. Assume there are 5 accounts.
    Algorithm: randomly generate 5 numbers and assign them to the 5 accounts,
               then calculate the ratio of the  number to the sume, which is used as the 
               position for each account
    '''
    acc_pool = ['account1', 'account2', 'account3', 'account4', 'account5']
    quota_list = [random.randint(0,10) for i in range(5)]
    tmp_sum = sum(quota_list)
    quota_list = [term/tmp_sum for term in quota_list]
    acc_quota = dict(zip(acc_pool, quota_list))
    return acc_quota
 
def controller_server_pp():
    """
    Mimic part of controller server, i.e., position processing and posting to position server
    """
    # at startup, clear queue
    redis_pool = redis.ConnectionPool(host=cnst.queue_ip, port=cnst.queue_port)
    """
    with redis.Redis(connection_pool= redis_pool) as conn:
        conn.ltrim(cnst.queue_name, 1, 0)
    """
    # originally, positions in each account are equal, and no position in any account
    positions = {'account1': 0.2, 'account2': 0.2, 'account3': 0.2, \
                 'account4': 0.2, 'account5': 0.2}
    account_info = {'account1': {}, 'account2': {},'account3': {},\
                 'account4': {},'account5': {}} # the info to be sent to position server
    # 
    while True:
        logging.info("controller server: START")
        # process messages in queue and update position info in accounts
        with redis.Redis(connection_pool=redis_pool) as conn:
            while conn.llen(cnst.queue_name) > 0:
                msg = json.loads(conn.rpop(cnst.queue_name).decode())
                # two types of msg, i.e., from fill server and AUM server
                if any(['account' in term for term in msg.keys()]):
                    positions.update(msg)
                    print(positions)
                    logging.info('controller server: Split info received from AUM and updated')
                    continue
                # deal with accounts: 
                # Data structure for the results is ACCOUNT_INFO, as {'accountn': {'stock_name1': quantity, ...}}
                # msg as {stock_ticker: <string out of 10 possibilities>, price: <random positive price>, quantity: <random quantity>}
                stock_ticker = msg['stock_ticker']
                # get the existing values
                st_in_acc = [term.get(stock_ticker,0) for term in account_info.values()]
                rmn_qntt = float(msg['quantity']) # remaining quantity
                if sum(st_in_acc) == 0:
                    # start assigning new positions to each accounts
                    for acc in sorted(account_info.keys()):
                        ap = round(float(positions[acc])*float(msg['quantity'])) # account position
                        account_info[acc][stock_ticker] = min(ap, rmn_qntt)
                        rmn_qntt -= ap
                        if rmn_qntt <= 0:
                            break
                else:
                    # assign new quantity to existing positions
                    total_qntt = float(msg['quantity']) + sum(st_in_acc)
                    logging.info(f"""total quantity: {total_qntt}""")
                    for acc in sorted(account_info.keys()):
                        if account_info[acc][stock_ticker]/(sum(st_in_acc)+float(msg['quantity'])) >= float(positions[acc]):
                            # position in this specific accnt is enough
                            continue 
                        else:
                            gap = round(total_qntt*float(positions[acc])) - account_info[acc][stock_ticker]
                            account_info[acc][stock_ticker] += min(gap, rmn_qntt)
                            rmn_qntt -= gap
                            if rmn_qntt <= 0:
                                # then no more quantity to be allocated to remaining accounts
                                break

                if rmn_qntt > 0:
                    # check whether there are remaining quantity which not allocated, if so, assign to the last account
                    logging.info('Still remaining after allocation, assign it to the last account.')
                    sp_acc = sorted(account_info.keys())[-1]
                    account_info[sp_acc][stock_ticker] += rmn_qntt
                    rmn_qntt = 0
        # post results to position server
        logging.info("controller server: to send information to position server")
        tmp = post_requests(json.dumps(account_info), cnst.url_posi_server)
        if str(tmp).startswith('20'):
            logging.info("controller server: request sending SUCCESSFULLY")
        else:
            logging.info("controller server: request sending FAILED")
        # 10-second waiting/blocking
        pause_controller = 10
        logging.info(f"""controller server: suspending in next {pause_controller} seconds""")
        time.sleep(pause_controller) 
        logging.info("controller server: END")

if __name__ == '__main__':
    # register()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO) #, datefmt="%H:%M:%S.%f"
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(controller_server_pp)
        executor.submit(fill_server)
        executor.submit(aum_server)
    """
    ts = [threading.Thread(target=controller_server_pp),
          threading.Thread(target=fill_server), #, args=()),
          threading.Thread(target=aum_server)]
    for i in ts:
        i.start()
    