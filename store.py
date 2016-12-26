#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import *
import crawlLagou

client = MongoClient()
db = client['result']
col = db['lagou']

encodeName = "gb18030"

def storage():
	for cid in range(22708, 160999+1):
		if col.find_one({"cid": cid}) == None:
			info = crawlLagou.getCompanyInfo(cid) # return dict
			# if info['cid'] != -1 and info['total'] != 0 :
			if info['cid'] != -1:
				info = mongoEncoding(info)
				col.insert(info)
				# salary = getPosition(cid, browser) # return array
				# for item in salary:
				# 	col.update({"cid": cid}, {"$push", {"salary": item}})

def mongoEncoding(obj):
	for item in obj:
		if isinstance(obj[item], str):
			obj[item] = obj[item].decode(encodeName).encode("utf-8")
	return obj

storage()