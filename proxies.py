#!/usr/local/bin/python3
# coding: utf-8

# Twitter_DL - twittdl.py
# 07/26/2023 16:52
#

__author__ = "SanujaNS <sanuja.senaviratne@gmail.com>"

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