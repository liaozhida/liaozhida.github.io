# -*- coding: utf-8 -*-

import urllib
import os,sys





path = os.path.abspath(os.path.join(sys.path[0], 'bloglist/segment.bl' ))
file = open(path, 'a')
file.write('\r\n'+'eshi ')

ss = '/Users/zhidaliao/Desktop/zhida_blog/_posts/运维 & 主机 & 系统搭建/2015-10-22-Jenkins系统搭建及常见操作.md'
print ss.split('/')[len(ss.split('/'))-1]