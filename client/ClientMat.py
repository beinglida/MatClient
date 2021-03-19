import sys
import threading
import grpc
import sys
from pathlib import Path
import time
import os
import random
import numpy as np
from functools import partial
import json
import zipfile
import pandas as pd

_current_root = str(Path(__file__).resolve().parents[1])
sys.path.append(_current_root)
sys.path.append('.')

ISTESTING = False
import contest.mat_pb2 as dealer_pb2
import contest.mat_pb2_grpc as rpc
from lib.simple_logger import simple_logger
from lib.utils import *


f = open("keys.txt", "a+")


class Client(object):
    def __init__(self, username: str, key: str, logger, address='47.102.204.214', port=9500, question_path='D:/Question-client/'):
        self.username = username
        # create a gRPC channel + stub
        self.address = address
        self.port = port
        self.question_path = question_path
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.MatStub(channel)

        self._lock = threading.Lock()
        self._decision_so_far = []  # history of the decision info from the server
        self._is_started = True     # control heartbeat
        self._new_response = []     # response list from the server
        self._new_request = []      # request list waiting to send to the server

        self.init_capital = -1
        self.logger = logger

        if self.logger is None:
            self.logger = simple_logger()

        self.stoped = False

        self.key = key
        self.logger.info('self.key is inited to ' + self.key)

        self.cond = threading.Condition()
        self.heart_beat_interval = 0.1

        self.question_dict = {}
        self.keys_file = {}
        self.init_questions()

        self.login(self.username, self.key)  # 这里是阻塞的，不登录无法进行游戏

        self._updater = threading.Thread(target=self.run)  # 维持heartbeat
        self._updater.setDaemon(True)
        self._updater.start()

        self._updater2 = threading.Thread(target=self.start)  # 维持通信处理
        self._updater2.setDaemon(True)
        self._updater2.start()

    def __del__(self):
        self._is_started = False

    def login(self, user_id, user_pin):
        while True:
            try:
                request = dealer_pb2.LoginRequest()
                request.user_id = user_id
                request.user_pin = user_pin
                self.logger.info('waiting for connect')
                response = self.conn.login(request)

                if response:
                    if response.success:
                        self.init_capital = response.init_capital
                        self.logger.info('login success')
                        return
                    else:
                        self.logger.info('login failed.' + response.reason)
                        time.sleep(3)

            except grpc.RpcError as error:
                self.logger.info('login failed. will retry one second later')
                time.sleep(1)

    def client_reset(self, username: str, logger):
        self.username = username
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(self.address + ':' + str(self.port))
        self.conn = rpc.MatStub(channel)

        self._decision_so_far = []  # history of the decision info from the server
        self._new_response = []     # response list from the server
        self._new_request = []      # request list waiting to send to the server
        self.init_capital = -1
        self.stoped = False

    def chat_with_server(self):
        while True:
            self.cond.acquire()
            while True:
                while len(self._new_request) != 0:
                    # yield a resquest from the request list to the server
                    msg = self._new_request.pop(0)
                    yield msg
                self.cond.wait()
            self.cond.release()

    def add_request(self, msg):
        self.cond.acquire()
        self._new_request.append(msg)
        self.cond.notify()
        self.cond.release()

    def run(self):
        """
        有一个很大的作用是，定期监听需要获得的消息
        """
        while self._is_started:
            # heartbeat
            msg = dealer_pb2.ActionRequest(user_id=self.username, user_pin=self.key,
                                           msg_type=dealer_pb2.ActionRequest.HeartBeat)
            self.add_request(msg)

            time.sleep(self.heart_beat_interval)
            if self.stoped:
                self.client_reset(self.username, self.logger)
        return

    def init_questions(self):
        question_files = os.listdir(self.question_path)
        question_files = [q for q in question_files if q[0]=='Q']
        question_files.sort(key=lambda x: int(x[2:-4]))
        question_name = [qf[:-4] for qf in question_files]
        question_num = [i+1 for i in range(len(question_name))]  # 从1开始计数而不是0
        self.question_dict = dict(zip(question_num, question_name))
        self.keys_file = dict(zip(question_num, ['']*len(question_name)))

    def start(self):
        '''
        处理从server发回的消息
        '''
        self.logger.info('start run')
        responses = self.conn.GameStream(self.chat_with_server())
        for res in responses:
            print(res.game_info)
            game_info = json.loads(res.game_info)

            if res.msg_type == dealer_pb2.ActionResponse.ResponseInfo:
                self.logger.info(game_info['info'])

            if res.msg_type == dealer_pb2.ActionResponse.StateInit:
                # server asking for a decision from the client
                self.logger.info('game init')
                # ******************************************************************************

            elif res.msg_type == dealer_pb2.ActionResponse.ResponseAsk:
                """
                密码
                """
                f.write(game_info["question_key"] + "\n")
                f.flush()

                self.logger.info('question %d key is %s' % (game_info['question_num'], game_info['question_key']))
                self.keys_file[game_info['question_num']] = game_info['question_key']

            elif res.msg_type == dealer_pb2.ActionResponse.ResponseAnswer:  # 询问是否准备好
                self.logger.info('question %d score is %s' % (game_info['question_num'], game_info['question_score']))

    def main(self):
        self.logger.info('run main')
        for num_, name_ in self.question_dict.items():
            # 申请密钥
            game_info = {'question_num': num_}
            msg = dealer_pb2.ActionRequest(user_id=self.username, user_pin=self.key,
                                           msg_type=dealer_pb2.ActionRequest.RequestAsk,
                                           game_info=json.dumps(game_info, cls=NpEncoder, ensure_ascii=False))
            self.add_request(msg)

            # 等待密钥
            while self.keys_file[num_] == '':
                time.sleep(0.1)


            file_key = self.keys_file[num_]

            # 解压并计算，自行实现，这里给一个全0demo
            shape_range = [100, 200, 300, 500, 1000, 2000, 3000, 5000, 8000, 10000]
            k = [[0]*shape_range[num_-1]]

            # 提交答案
            game_info = {
                'question_num': num_,  # num_为题号
                'answer': k,           # k为1*n的list或ndarray
            }
            msg = dealer_pb2.ActionRequest(user_id=self.username, user_pin=self.key,
                                           msg_type=dealer_pb2.ActionRequest.RequestAnswer,
                                           game_info=json.dumps(game_info, cls=NpEncoder, ensure_ascii=False))
            self.add_request(msg)

            time.sleep(5)  # necessary, unchanged


if __name__ == '__main__':
    username = 'test1'
    key_ = 'ogrsnrlotm'
    logger = simple_logger()

    c = Client(username, key_, logger)
    c.main()


