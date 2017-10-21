import json

def jsonTokv():
	file = open('zhihu_cookies', 'r')
	try:
		cookies = json.load(file)
		# print len(cookies)
	except ValueError,e:
		print 'cache-cookie is None'
	
	
	cookiesStr = ''
	for key in cookies:
		cookiesStr += key+'='+cookies[key]+';'
	print cookiesStr[0:-1]
	return cookiesStr[0:-1]
	
	
	
jsonTokv();