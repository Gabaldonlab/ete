#!/usr/bin/python
import sys, os, random
from mod_python import Cookie

def generateHash():
    import sha, time
    return sha.new(str(time.time())).hexdigest()

def getCookie(req, key):
    cookies = Cookie.get_cookies(req)
    if cookies.has_key(key):
        return str(cookies[key]).split('=')[1]

def setCookie(req, key, value):
    cookie = Cookie.Cookie(key, value)
    Cookie.add_cookie(req, cookie)

class WebPlugin:
    def __init__(self, req, temp_folder='/var/tmp', hostname = '/'):
        if getCookie(req, 'sid'):
            self.sid = getCookie(req, 'sid')
        else:
            self.sid = generateHash()
            setCookie(req, 'sid', self.sid)
        self.tempFolder = temp_folder
        self.sessionFolder = os.path.join(self.tempFolder, self.sid)
        if not os.path.exists(self.sessionFolder):
            os.mkdir(self.sessionFolder)
            os.chmod(self.sessionFolder, 0777)
        self.hostname = hostname

    def publishTree(self, tree):
        TREE = open(os.path.join(self.sessionFolder, 'test.tree'), 'w')
        print >> TREE, tree
        treeid = 'test'
        return "<img src='"+self.hostname+"loader.gif?rnd="+str(random.random())+"' id='"+treeid+"' onClick=\"mapcheck(this,'"+treeid+"')\" onLoad=\"get_map(this, '"+treeid+"', '"+self.sid+"')\"><div id='scriptarea_"+treeid+"'></div>"

def form():
    return '''Input the tree in NW format and press DRAW<form name='tree_input' method='post' action='/index/tree'><textarea name='tree' style='width: 700px; height: 200px'>(Sce0008330:0.291009,Sce0012351:0.286238,((((((Sce0007182:0.007445,Sce0006845:0.000000)0.149440:0.000642,Sce0010258:0.435715)0.028000:0.000000,Sce0009286:0.000000)0.000000:0.000000,(Sce0008283:0.008074,(((Sce0011197:0.008115,((Sce0010685:0.000000,Sce0012157:0.000000)0.125038:0.000000,Sce0012332:0.016679)0.788000:0.008129)0.797000:0.008200,(Sce0009812:0.000000,Sce0010100:0.000000)0.849000:0.008096)0.000000:0.000000,((Sce0006682:0.000000,(Sce0009344:0.008122,Sce0008221:0.008223)0.000000:0.000000)0.000000:0.000000,Sce0008967:0.000000)0.000000:0.000000)0.789000:0.008262)0.821000:0.008102)0.724000:0.068767,(Sce0008579:0.000000,(Sce0010646:0.000000,((Sce0010257:0.444538,Sce0010729:0.000000)0.779000:0.008777,(((Sce0009863:0.000000,Sce0010508:0.016244)0.846000:0.008054,((Sce0012763:0.000000,Sce0013060:0.000000)0.125038:0.000000,Sce0011718:0.000000)0.000000:0.000000)0.000000:0.000000,Sce0007366:0.008050)0.974000:0.041297)0.730000:0.009072)0.959000:0.076159)0.548892:0.017476)0.999850:0.531965,(Sce0006923:0.579030,Sce0009628:0.371343)0.524000:0.080094)0.994000:0.272496);</textarea><br><input type='submit' value='DRAW'></form>'''









def hide_box(title, content, mode='block'):
        output = "<div style='border: 1px solid #777; padding: 4px; margin-top: 10px;'><div style='margin-top: -14px; position: absolute;'><span class='hide_box_title popup_bg'>" + title + "</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'block'\">Show</span><span class='popup_bg popup_interactor' onClick=\"this.parentNode.parentNode.childNodes[1].style.display = 'none'\">Hide</span></div><div style='padding-top: 4px; display: "+mode+"'>" + content + "</div></div>"
        return output

def treeimg(req=None, seqid=None, sid=None, rnd=None):
    # create image and map, return image, store the map
    from popen2 import Popen3

    # run tree generator as a separate process ( give as argument the work path and seqid )
    proc = Popen3("python /home/services/web/ivan.phylomedb.org/maketree.py " + str(sid) + " " + str(seqid))
    proc.tochild.close()
    add = '1'
    # read stduotput  =  image
    fromchild = proc.fromchild.readline()
    while add:
        add = proc.fromchild.readline()
        fromchild += add
    if req:
        req.content_type = 'image/png'
    return fromchild  #  send image with a header of image

###########################

def nwtree(req=None):
    if req:
        req.content_type = 'text/html'
    form = "Input the tree:<form name='listadd' method='post' action='http://ivan.phylomedb.org/ete2_server/nwtrees'><textarea name='tree' style='width: 700px; height: 200px'></textarea><br><input type='submit' value='Draw the tree'></form>"
    return form
    
def nwtrees(req=None):
    import cgi, cgitb; cgitb.enable()
    session_id = '123'
    seqid = 'usernw'
    form = cgi.FieldStorage()
    tree = form['tree'].value
    if req:
        req.content_type = 'text/html'
    return tree
    
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + str(session_id)
    if os.path.exists(THIS_SESSION_PATH):
        pass
    else:
        os.mkdir(THIS_SESSION_PATH)
    THIS_SESSION_PATH = TEMP_DIR_PATH
    # put tree in a file in temp session directory
    TREEFILE = open(THIS_SESSION_PATH + "/" + seqid + ".tree", "w")
    TREEFILE.write(tree)
    TREEFILE.close()
    # first show loader, then load big tree
    return "<img src='"+BASE_URL+"images/loader.gif?rnd="+str(random.random())+"' id='"+seqid+"' onClick=\"mapcheck(this,'"+seqid+"')\" onLoad=\"get_map(this, '"+seqid+"', '"+session_id+"')\"><div id='scriptarea_"+seqid+"'></div>"


############################

def tree(tree, seqid, session_id, host=None , port=None, req=None):
    import random
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + str(session_id)
    if os.path.exists(THIS_SESSION_PATH):
        pass
    else:
        os.mkdir(THIS_SESSION_PATH)
        os.chmod(THIS_SESSION_PATH, 0577)

    # put tree in a file in temp session directory
    TREEFILE = open(THIS_SESSION_PATH + "/" + seqid + ".tree", "w")
    TREEFILE.write(tree)
    TREEFILE.close()
    # first show loader, then load big tree
    return "<img src='"+BASE_URL+"images/loader.gif?rnd="+str(random.random())+"' id='"+seqid+"' onClick=\"mapcheck(this,'"+seqid+"')\" onLoad=\"get_map(this, '"+seqid+"', '"+session_id+"')\"><div id='scriptarea_"+seqid+"'></div>"


def getmap(req=None, seqid=None, sid=None):
    # read a map from a file or return alert
    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + sid
    if req:
        req.content_type = 'text/javascript'
    try:
        res = open(THIS_SESSION_PATH+"/"+seqid+".map")
    except IOError:
        return "alert('no map "+THIS_SESSION_PATH+"');"
    else:
        out = res.readline()
        os.remove(THIS_SESSION_PATH+"/"+seqid+".map")
        return out


def info(req=None, dbid=None):
    # requare any info about DB   id - translation tables can be used etc.
    import os, sys, MySQLdb, ete2
    if req:
        req.content_type = 'text/html'

    # prepare seq for popup window
    def split_code(code):
        output = "<table style='font-family: Courier New; font-size: 8pt;'>"
        c = 1
        for i in range(len(code)/10+1):
            if c == 1:
                output += "<tr>"
            output += "<td>" + code[i*10:(i+1)*10] + "</td>"
            if c == 4:
                output += "</tr>"
                c = 0
            c += 1
        if c == 1:
            output += "</table>"
        else:
            output += "</tr></table>"
        return output

    p = get_pointer()
    # get info about DB id
    info = p.get_seqid_info(dbid)
    close_p()
    # put information in nice boxes
    res =  hide_box('Name', info['name'])
    res += hide_box('Comments', info['comments'])
    res += hide_box('Sequence', split_code(info['seq']), mode='none') # mode='none' - hide the box content by default
    
    return res # return information in the popup menu


def addrule(req=None, seqid=None, itemid=None, rule=None, sid=None, unic='0', remove='0', clear='0'):

    THIS_SESSION_PATH = TEMP_DIR_PATH + '/' + sid
    
    # function add a rule to the rules file
    # 3 possible work modes:  ADD (add new rule if it doesn't exist), REMOVE (remove rule if it exists), UNIC (add rule, after delete the rule with a same key)
    # for every mode there is javascript function:     set_rule(),     rem_rule(),     unic_rule()
    # processing of the rules file located in the script maketree.py   during tree generation
    
    if req:
        req.content_type = 'text/plain'
    done = False
    rules = set()
    if clear == '1':
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        RULES.close()
    else:
        try:
            RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules")
        except IOError:
            pass
        else:
            for item in RULES:
                key, value = item.strip().split('\t')
                if remove == '1' and str(key) == str(rule) and str(value) == str(itemid):
                    pass
                elif unic == '1' and key == rule:
                    pass
                else:
                    rules.add(item.strip())

        if remove == '0':
            rules.add(rule + '\t' + str(itemid))
        
        RULES = open(THIS_SESSION_PATH+"/"+seqid+".rules", "w")
        sid
        for rule in rules:
            print >> RULES, rule
    
    return 1
