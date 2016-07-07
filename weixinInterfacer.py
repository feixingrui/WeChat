# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib
import urllib2
import re
import json
import random
from lxml import etree
import xml.etree.ElementTree as etree

def timetime():
	return time.strftime("%y%m%d",time.localtime(time.time()))

def youdao(word):
	qword = urllib2.quote(word)
	baseurl = r'http://fanyi.youdao.com/openapi.do?keyfrom=ACCESS_TOKEN&key=KEY&type=data&doctype=json&version=1.1&q='
	url = baseurl+qword
	resp = urllib2.urlopen(url)
	fanyi = json.loads(resp.read())
	if fanyi['errorCode'] == 0:        
		if 'basic' in fanyi.keys():
			trans = u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),';'.join(fanyi['web'][0]['value']))
			return trans
		else:
			trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
			return trans
	elif fanyi['errorCode'] == 20:
		return u'对不起，要翻译的文本过长'
	elif fanyi['errorCode'] == 30:
		return u'对不起，无法进行有效的翻译'
	elif fanyi['errorCode'] == 40:
		return u'对不起，不支持的语言类型'
	else:
		return u'对不起，您输入的单词%s无法翻译,请检查拼写' %word
    
def douban_movie(name):
	search_name = urllib2.quote(name)
	search_base_url = r'https://api.douban.com/v2/movie/search?count=1&q='
	search_url = search_base_url+search_name
	resp1 = urllib2.urlopen(search_url)
	search_json = json.loads(resp1.read())#search之后的json
	search_total = search_json['total']
	if search_total == 0:
		result = [u'暂无查询结果']
		return result
	else:
		result = ['','','','','']
		movie_name = result[1] = search_json["subjects"][0]["original_title"]#电影名字
		movie_directors = search_json["subjects"][0]["directors"][0]["name"]#导演
		movie_casts = search_json["subjects"][0]["casts"][0]["name"]#主演
		movie_average = search_json["subjects"][0]["rating"]["average"]#豆瓣评分   
		movie_id = search_json["subjects"][0]["id"]#电影id
		result[3] = search_json["subjects"][0]["images"]["large"]#电影海报
		subject_url = r'https://api.douban.com/v2/movie/subject/'+movie_id
		resp2 = urllib2.urlopen(subject_url)
		subject_json = json.loads(resp2.read())#电影条目的json
		movie_summary = subject_json["summary"]#电影简介
		result[2] = movie_summary[:54]+'......'#电影描述
		movie_detail_url = result[4] = subject_json["mobile_url"]#移动端详情页
		result[0] = u'【%s】\n导演：%s\n主演：%s等\n豆瓣评分：%s/10\n简介：\n%s\n\n去豆瓣电影查看详情：\n%s'%(movie_name,movie_directors,movie_casts,movie_average,movie_summary,movie_detail_url)
		return result

def faceplusplus(url):
	trans = {'Male':u'男','Female':u'女','Asian':u'亚洲人','White':u'白种人','Black':u'黑人','None':u'没戴','Dark':u'墨镜','Normal':u'戴了'}
	baseurl = r'http://apicn.faceplusplus.com/v2/detection/detect?api_key=KEY&api_secret=SECRET&attribute=gender,age,race,smiling,glass,pose&url='
	final_url = baseurl + url
	resp = urllib2.urlopen(final_url)
	face = json.loads(resp.read())
	if face['face'] == []:
		return u'不好意思，没有检测到人脸；\n或者您的图片太大，请上传小于1M的图片～'
	else:
		gender = face['face'][0]['attribute']['gender']['value']
		gender = trans[gender]
		gender_confidence = face['face'][0]['attribute']['gender']['confidence']
		age = face['face'][0]['attribute']['age']['value']
		age_range = face['face'][0]['attribute']['age']['range']
		race = face['face'][0]['attribute']['race']['value']
		race = trans[race]
		race_confidence = face['face'][0]['attribute']['race']['confidence']
		smiling = face['face'][0]['attribute']['smiling']['value']
		glass = face['face'][0]['attribute']['glass']['value']
		glass = trans[glass]
		glass_confidence = face['face'][0]['attribute']['glass']['confidence']
		return u'性别：%s（置信度%.2f％）\n年龄：%s(±%d)岁\n人种：%s(置信度%.2f％)\n微笑得分：%.2f（满分100）\n眼镜：%s（置信度%.2f％）\n' %(gender,gender_confidence,age,age_range,race,race_confidence,smiling,glass,glass_confidence)

def Turing(info,userid):
	baseurl = r'http://www.tuling123.com/openapi/api?key=KEY'
	final_url = baseurl + '&info=' + info + '&userid=' + userid
	resp = urllib2.urlopen(final_url)
	tuling = json.loads(resp.read())
	if tuling['code'] == 100000:
		return tuling['text']
    
def getCYBNews(url):
	page = urllib2.urlopen(url)
	html = page.read().decode('utf-8')
	reg = r'<a target="_blank" href="(.+/20%s/.+.html)" class="item-title">' %(timetime())
	#reg = r'<a target="_blank" href="(.+/20160424/.+.html)" class="item-title">'
	newsre = re.compile(reg)
	newslist = re.findall(newsre,html)
	i = 1
	news = ''
	for n in newslist:
		sub_page = urllib2.urlopen(n)
		sub_html = sub_page.read().decode('utf-8')
		sub_reg = r'<h1 class="article-tit">(.{1,50})</h1>'
		sub_newsre = re.compile(sub_reg)
		sub_newslist = re.findall(sub_newsre,sub_html)
		if not len(sub_newslist):
			continue
		news += '%d.%s\n \n' %(i,sub_newslist[0])
		i += 1
		if i%5 == 1:
			news = news + '----------------------\n \n'
	news = u'早安！\n每天早晨拥抱你，真好～\n \n----------------------\n▼\n \n' + news
	return news
        
    
class WeixinInterface:
 
	def __init__(self):
		self.app_root = os.path.dirname(__file__)
		self.templates_root = os.path.join(self.app_root, 'templates')
		self.render = web.template.render(self.templates_root)
 
	def GET(self):
        #获取输入参数
		data = web.input()
		signature=data.signature
		timestamp=data.timestamp
		nonce=data.nonce
		echostr=data.echostr
        #自己的token
		token="TOKEN" #这里改写你在微信公众平台里输入的token
        #字典序排序
		list=[token,timestamp,nonce]
		list.sort()
		sha1=hashlib.sha1()
		map(sha1.update,list)
		hashcode=sha1.hexdigest()
        #sha1加密算法
        #如果是来自微信的请求，则回复echostr
		if hashcode == signature:
			return echostr
      
	def POST(self):        
		str_xml = web.data() #获得post来的数据
		xml = etree.fromstring(str_xml)#进行XML解析
        #以下三行为公用，其它的最好放入相应if下，不然可能会发生错误
		msgType=xml.find("MsgType").text
		fromUser=xml.find("FromUserName").text
		toUser=xml.find("ToUserName").text
		#mc = pylibmc.Client()
		#return self.render.reply_text(fromUser,toUser,int(time.time()),u"我是一只小鹦鹉，您刚才说的是："+content)
		
        #以下是欢迎信息
        #之前之所以总是不行
        #是因为把content = xml.find("Content").text放在了这段前面
        #可能会导致把事件推送读成content从而使event失效
		if msgType == "event":
			mscontent = xml.find("Event").text
			if mscontent == "subscribe":
				replayText = u"你好，欢迎关注~[胜利]\n我是主人费费制作的机器人费小瑞，很高兴认识你！[亲亲]\n回复help可以查看我的使用说明书呦~[呲牙]"
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
		
		
        #关键词设置
		if msgType == 'text':
			content = xml.find("Content").text
            
			#图文测试
			if 'tw' in content:
				title = u'这里是标题'
				description = u'这里是描述'
				picurl = r'http://picture.feixingrui.com/20151209ycc/1.png'
				url = r'http://mp.weixin.qq.com/s?__biz=MzA3NTUxMjQyNA==&mid=211672722&idx=1&sn=54fc6a2102d644d9fa6cc7ada8817f34#rd'
				return self.render.reply_pictext(fromUser,toUser,int(time.time()),title,description,picurl,url)
            #翻译
			if content[:2].lower() == 'fy':
				content = content[2:]
				if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
				Nword = youdao(content)
				return self.render.reply_text(fromUser,toUser,int(time.time()),Nword)
			#电影简介
			if content[:2].lower() == 'dy':
				content = content[2:]
				if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
				movie = douban_movie(content)
				return self.render.reply_text(fromUser,toUser,int(time.time()),movie[0])
            #电影影讯
			if content[:2].lower() == 'yx':
				content = content[2:]
				if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
				movie = douban_movie(content)
				return self.render.reply_pictext(fromUser,toUser,int(time.time()),movie[1],movie[2],movie[3],movie[4])
            #电影海报
			if content[:2].lower() == 'hb':
				content = content[2:]
				if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
				movie = douban_movie(content)
				movie[1] = u'【%s】电影海报' %movie[1]
				movie[2] = u'点击详情查看大图'
				return self.render.reply_pictext(fromUser,toUser,int(time.time()),movie[1],movie[2],movie[3],movie[3])
			#新闻快讯
			if content[:2].lower() == 'xw':
				content = content[2:]
				if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
				news = getCYBNews('http://www.cyzone.cn/category/8/')
				news = news + u'来自创业邦'
				return self.render.reply_text(fromUser,toUser,int(time.time()),news)
            #帮助
			if content.lower() == "help":
				replayText = u'费小瑞的使用说明：\n\n★翻译功能\nfy+需要翻译的文本\n\n★查看电影评分\ndy+电影名称\n\n★查看影讯\nyx+电影名称\n\n★听我为你选的歌\n回复m\n\n★人脸识别\n发一张小于1M的图片\n'
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
			
            #音乐
			if content.lower() == 'm':
				musicList = [
                             [r'http://wx.feixingrui.com/feixiaorui/music/ALittleLove.mp3',u'A Little Love',u'冯曦妤'],
                             [r'http://wx.feixingrui.com/feixiaorui/music/RiverFlowsInYou.mp3',u'River Flows In You',u'李闰珉'],
                             [r'http://wx.feixingrui.com/feixiaorui/music/canon.mp3',u'卡农',u'纯音乐']
                             ]
				music = random.choice(musicList)
				musicurl = music[0]
				musictitle = music[1]
				musicdes = music[2]                
				return self.render.reply_music(fromUser,toUser,int(time.time()),musictitle,musicdes,musicurl)

			#图灵机器人
			if type(content).__name__ == "unicode":
					content = content.encode("UTF-8")
			turing_reply = Turing(content,'123')
			return self.render.reply_text(fromUser,toUser,int(time.time()),turing_reply)
        
        
		#face++
		if msgType == 'image':
			url = xml.find("PicUrl").text
			face_result = faceplusplus(url)
			return self.render.reply_text(fromUser,toUser,int(time.time()),face_result)
        
        #语音识别
		if msgType == 'voice':
			content = xml.find("Recognition").text
			content = u'您说的是：' + content
			return self.render.reply_text(fromUser,toUser,int(time.time()),content)

        
        
        #防止出现'无法提供服务'字样
		return self.render.reply_text(fromUser,toUser,int(time.time()),u"请输入help来获取我的操作指南，解锁更多玩法！[胜利]\n我是费小瑞，您刚才说的是："+content)
    
    
    
    

    
    
