#!/usr/local/bin/python3
# coding: utf-8

#
# Copyright 2021 SanujaNS under the terms of the Apache License 2.0
# license found at https://github.com/SanujaNS/SN_Twi_DL/blob/main/LICENSE
# Twitter_DL - proxies.py
# August 28, 2023 2:25
#

__author__ = "SanujaNS <sanujas@sanuja.biz>"

class Proxies:

    _hostname = None
    _port= None
    __proxy_list = []

    def load_proxy_list(self):
        try:
            with open('./proxy.txt') as f:
                self.__proxy_list = f.readlines()
            self.trim_values()
            return self.__proxy_list
        except NameError:
            print(NameError)
    
    def trim_values(self):
        try:
            for i in range(0, len(self.__proxy_list)):
                self.__proxy_list[i] = self.__proxy_list[i].strip()
        except NameError:
            print(NameError)