#!/usr/bin/env python
# -*- coding: japanese.euc-jp -*-

# kabuAPI: Application Programmer Interface for Stock Trading 
# Copyright (C) 2007 kabuAPI Project (http://sourceforge.jp/projects/kabuapi/)
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#############################################
# CONFIGURATION START
# type the keys in hankaku letters between "".
#############################################
uid =            "00000000"  
passwd =         "00000000"
torihiki_ansho = "00000000"
#############################################
# CONFIGURATION END
#############################################



import urllib
import urllib2
import urlparse
import re
import string





gmpath = ""

# todo: how to give POST request 
entranceurl = "https://www.deal.matsui.co.jp/ITS/login/MemberLogin.jsp"
loggedin = 0 # if 1, logged in

entrancereq = urllib2.Request(entranceurl)

def remcomma(string):
    def strappend(str1, str2):
        return str1 + str2
    return reduce(strappend, string.split(','))

def sjis2u(string):
    return unicode(string, "shift_jis")

def sjislines2unicode(lines):
    return map(sjis2u, lines)

def entrancedata():
    page = urllib2.urlopen(entrancereq)
    return sjis2u(page.read())

#

def is_under_maintanance(udata):
    return re.compile(maintain).search(udata) is not None

maintain = u'メンテナンスを行っています'

def under_maint():
    return is_under_maintanance(entrancedata())

#

host = "www.deal.matsui.co.jp"
scheme = "https://"

def home():
    global gmpath
    if gmpath == "":
        login()
    else:
        data = gmdata()
        path = gmdata2home(data)
        movetopath(path) # in this, set gmpath

# interface

def buy(code, num, price):
    return order(code, num, price, 13)

def sell(code, num, price):
    return order(code, num, price, 111)

def yoryoku():
    home()
    lm, ct = movetopath(gmdata2sisan(gmdata()))
    result = ctdata2yoryoku(ctdata(ct))
    home()
    return result

def whatIhave():
    home()
    lm, ct = movetopath(gmdata2stock(gmdata()))
    sellpath = findsellpath(ctdata(lm))
    lm, ct = movetopath(sellpath)
    return havedatal2lst(ctdatal(ct))

#

def havedatal2lst(datal):
    result = []
    nextlinehassomething = False
    for line in datal:
        if line[:4] == "<BR>":
            code = int(re.compile("[0-9]+").search(line).group())
            nextlinehassomething = True
        elif nextlinehassomething:
            num = int(remcomma(re.compile("[0-9,]+").search(line).group()))
            result.append((code, num))
            nextlinehassomething = False
    return result

#

def order(code, num, price, BorS):
    if num == 0: return True
    home()
    lm, ct = movetopath(gmdata2stock(gmdata()))
    data = ctdata(lm)
    path = formaction(data)
    url = scheme + host + path
    dic = dict([("prmDscr", str(code))])
    req = urllib2.Request(url)
    req.add_data(urllib.urlencode(dic))
    formpage = urllib2.urlopen(req)
    data = formpage.read()
    nextpath = formaction(data)
    dic = dict([("commitFlg", "true"), ("dscrCD", dscrCD(data)), ("marketCDInfo", marketCD(data)), ("tradeKbn", str(BorS)), ("spAccKbn", "1"), ("marketCDOrder", marketCD(data)), ("orderNominal", str(num)), ("orderPrc", str(price)), ("execCondCD", "0"), ("validDt", "0"), ("tyukakuButton.x", "4"), ("tyukakuButton.y", "4")])
    req = urllib2.Request(scheme + host + nextpath, urllib.urlencode(dic))
    formpage.close()
    formpage = urllib2.urlopen(req)
    data = formpage.read()
    nextpath = formaction(data)
    dic = dict([("pinNo", torihiki_ansho)])
    req = urllib2.Request(scheme + host + nextpath, urllib.urlencode(dic))
    formpage.close()
    formpage = urllib2.urlopen(req)
    data = formpage.read()
    formpage.close()
    if re.compile(u"ご注文を受付けました").search(unicode(data, "shift_jis")) is None:
        return False
    else: return True

    

def ctdata(ct):
    url = scheme + host + ct
    page = urllib2.urlopen(url)
    data = page.read()
    page.close()
    return data

def ctdatal(ct):
    url = scheme + host + ct
    page = urllib2.urlopen(url)
    datal = page.readlines()
    page.close()
    return datal

def ctdata2yoryoku(ctdata):
    data = re.compile("#genbutu[^\n]*\n[^\n]*\n").search(ctdata).group()
    data = re.compile("bgcolor.*D>").search(data).group()
    data = data[18:-7]
    return int(remcomma(data))


#
def gmdata2home(gmdata):
    reg = re.compile("\"/ITS/frame/FraHomeAnnounce[^\"]+?\"")
    st = reg.search(gmdata).group()
    st= st[1:-1]
    return st

def gmdata2anything(gmdata,searchstring):
    try:
        st = re.compile(searchstring).search(gmdata).group()
    except TypeError:
        print gmdata
    st = st[1:-1]
    return st

def findsellpath(lmdata):
    return gmdata2anything(lmdata, "\"/ITS/frame/FraStkSell.jsp[^\"]+?\"")

def gmdata2sisan(gmdata):
    return gmdata2anything(gmdata, "\"/ITS/frame/FraAstSpare.jsp[^\"]+?\"")

def gmdata2stock(gmdata):
    return gmdata2anything(gmdata, "\"/ITS/frame/FraStkOrder.jsp[^\"]+?\"")

def movetopath(path):
    global gmpath
    page = urllib2.urlopen(scheme + host + path)
    data = page.read()
    page.close()
    gm = dataname2src(data, "GM")
    lm = dataname2src(data, "LM")
    ct = dataname2src(data, "CT")
    gmpath = gm
    return (lm, ct)

def login():
    global gmpath
    if under_maint():
        return -1
    elif gmpath != "":
        print "login:", "already logged in"
        return -1
    else:
        action = "/servlet/ITS/login/MemberLoginEnter"
        url = scheme + host + action
        req = urllib2.Request(url)
        dic = dict([("attrFromJsp", "/ITS/login/MemberLogin.jsp"), ("clientCD", uid), ("passwd", passwd), ("easyTradeFlg", "0")])
        req.add_data(urllib.urlencode(dic))
        page = urllib2.urlopen(req)
        data = page.read()
        page.close()
        gm = dataname2src(data, "GM")
        lm = dataname2src(data, "LM")
        gmpath = gm

def gmdata():
    global gmpath
    url = scheme + host + gmpath
    req = urllib2.Request(url)
    page = urllib2.urlopen(req)
    data = page.read()
    page.close()
    return data

def logout():
    global gmpath
    data = gmdata()
    logout = gmdata2logout(data)
    page = urllib2.urlopen(scheme + host + logout)
#    print "logged out, header says:"
#    print page.info()
    gmpath = ""
    page.close()

def gmdata2logout(gmdata):
    reg = re.compile("\"/ITS/login/Logou[^\"]+?\"")
    st = reg.search(gmdata).group()
    st= st[1:-1]
#    print "logoutpath:", st
    return st

def dataname2src(data, name):
    regre = re.compile("<[A-Z]+.+?name=\"" + name + "\".+?src=\"[^\"]+\"")
    match = regre.search(data)
    if(match is None):
        print "no", name, "found in the data"
    else:
        st = match.group()
        ind = string.find(st, "src")
        return st[ind+5:-1]

#
def formaction(data):
    return re.compile("action=\"[^\"]+").search(data).group()[8:]

def dscrCD(data):
    data = re.compile("name=\"dscrCD\".value=\"[0-9]+\"").search(data).group()[21:-1]
#    print "dscrCD:", data
    return data

def marketCD(data):
#    print "marketCD"
    data = re.compile("<SELECT name=\"marketCDInfo\".*?</SELECT>", re.S).search(data).group()
#    print "phase 1", data
    data = re.compile("value=.+selected").search(data).group()
#    print "phase 2", data
    data = data[7:-10]
#    print "phase 3", data
    return data
