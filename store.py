#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import *
import crawlLagou

client = MongoClient()
db = client['result']
col = db['lagou']

def storage():
	browser = getFirefoxBrowser()
	for cid in range(22708, 22710+1):
		if col.find_one({"cid": cid}) == None:
			info = crawLagou.getCompanyInfo(cid, browser) # return dict
			if info.cid != -1 and info.total != 0 :
				col.insert(info)
				# salary = getPosition(cid, browser) # return array
				# for item in salary:
				# 	col.update({"cid": cid}, {"$push", {"salary": item}})

