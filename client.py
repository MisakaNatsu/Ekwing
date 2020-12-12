import requests
import demjson
from random import choice
import hashlib

def cinput(text,ntype="text"):
    while True:
        stdin = input(text)
        if ntype != "text":
            try:
                stdin = int(stdin)
            except:
                print("错误: 请输入整数")
                continue
        if input("确认输入?(y/n):") == 'y':
            break
    return stdin

def md5Encode(key):
    input_name = hashlib.md5()
    input_name.update(key.encode("utf-8"))
    return input_name.hexdigest()

def rand_16(nums=1):
    return "".join([choice("0123456789ABCDEF") for i in range(nums*2)])

class Ekwing():
    is_logined = False
    token = ""
    uid = ""

    request_require_data = {
        'driverCode' : "3.9.0",
        'osv' : "10",
        'os' : "Android",
        'v' : "3.7",
        'client' : "student",
        'driverType' : "Redmi%20Y3",
        'deviceToken' : "{}:{}:{}:{}:{}:{}".format(rand_16(),rand_16(),rand_16(),rand_16(),rand_16(),rand_16()),
        'is_http' : "1", 
    }

    request_require_header = {
        "User-Agent" : "okhttp-okgo/jeasonlzy",
        "Host" : "mapi.ekwing.com"
    }

    APIs = {
        "login" : ["https://mapi.ekwing.com/student/User/login","POST"],
        "get_user_info" : ["https://mapi.ekwing.com/student/user/getuserinfoall","POST"],
        "apiconf" : ["https://mapi.ekwing.com/student/Hw/apiconf","POST"],
        "get_exam_list" : ["https://mapi.ekwing.com/student/exam/getstuexamlist","POST"],
        "get_test_list" : ["https://mapi.ekwing.com/student/Hw/getList","POST"],
        "get_keys_answer" : ["https://mapi.ekwing.com/student/hw/getacpfcontent","POST"],
        "get_subject_list" : ["https://mapi.ekwing.com/student/Hw/getHwItems","POST"]
    }

    def __init__(self):
        pass

    def login(self,username,password):
        password = md5Encode(password)
        api = self.APIs['login']
        if api[1] == "POST":
            req = requests.post
        else:
            req = requests.get
        data = self.request_require_data
        data["username"] = username
        data["password"] = password
        response = demjson.decode(req(url=api[0],data=data,headers=self.request_require_header).text)
        if response["status"] == 1:
            return [False,response["data"]["error_msg"]]
        else:
            self.is_logined = True
            self.token = response["data"]["token"]
            self.uid = response["data"]["uid"]
            return [True,[response["data"]["token"],response["data"]["uid"]]]

    def login_with_token(self,token,uid):
        api = self.APIs['get_user_info']
        if api[1] == "POST":
            req = requests.post
        else:
            req = requests.get
        data = self.request_require_data
        data["token"] = token
        data["uid"] = uid
        data["author_id"] = uid
        response = demjson.decode(req(url=api[0],data=data,headers=self.request_require_header).text)
        if response["status"] == 1:
            return [False,"登录已过期"]
        else:
            self.is_logined = True
            self.token = token
            self.uid = uid
            return [True]
        
    def base_api_request(self,api,md={}):
        api = self.APIs[api]
        if api[1] == "POST":
            req = requests.post
        else:
            req = requests.get
        data = self.request_require_data
        data["token"] = self.token
        data["uid"] =self.uid
        data["author_id"] = self.uid
        data.update(md)
        response = req(url=api[0],data=data,headers=self.request_require_header).text
        return response
    
    def get_user_info(self):
        if self.is_logined == False:
            return [False,"未登录"]
        response = demjson.decode(self.base_api_request("get_user_info"))
        if response["status"] == 1:
            return [False,"未知错误"]
        else:
            d = response['data']
            return {"name":d['nicename'],"uid":d['users_uid'],'username':d['username'],'school':d['school'],'classes':d['classes']}

    def get_exam_list(self):
        if self.is_logined == False:
            return [False,"未登录"]
        response = demjson.decode(self.base_api_request("get_exam_list"))
        if response["status"] == 1:
            return [False,"未知错误"]
        else:
            exam_list = []
            for i in response['data']['list']:
                exam_list.append({"title":i["self_title"],"sub_time":i["sub_time"],"url":i["start_url"]})
            return exam_list
    
    def get_test_list(self):
        if self.is_logined == False:
            return [False,"未登录"]
        response = demjson.decode(self.base_api_request("get_test_list"))
        if response["status"] == 1:
            return [False,"未知错误"]
        else:
            exam_list = []
            for i in response['data']['list']:
                exam_list.append({"title":i["title"],"left_time":i["left_time"],"hid":i["hid"]})
            return exam_list
    
    def get_exam_answer(self,url):
        if self.is_logined == False:
            return [False,"未登录"]
        data = self.request_require_data
        data['product'] = "student"
        data["token"] = self.token
        data["uid"] =self.uid
        data["author_id"] = self.uid
        response = requests.get(url=url,params=data,headers=self.request_require_header)
        return response.text
    
    def get_hwitems(self,hid):
        if self.is_logined == False:
            return [False,"未登录"]
        response = demjson.decode(self.base_api_request("get_subject_list",{"hid":hid}))
        if response['status'] == 1:
            return [False,"未知错误"]
        else:
            lists =  []
            for i in response['data']['list']:
                lists.append({
                    'title':i['type_name'],
                    'keys':i['tk_path'].split('|')[0] if '|' in i['tk_path'] else i['tk_path'],
                })
            return lists
    
    def get_keys_answer(self,keys):
        if self.is_logined == False:
            return [False,"未登录"]
        response = self.base_api_request('get_keys_answer',{'keys':keys,'url':'https://acpf.ekwing.com/wapi/getbaseworktimucontent'})
        response = demjson.decode(response)
        answer_list = []
        if response['errno'] != 0:
            return [False,"未知错误"]
        for i in response['data']:
            if 'question' in i.keys():
                for o in i['question']['qus_item']:
                    answer_list.append(o['answer'].replace('[','').replace(']',''))
            elif 'ques_item' in i.keys():
                for o in i['ques_item']:
                    answer_list.append(o['text'])
        answer_text = ''
        for i in range(len(answer_list)):
            answer_text += "{}. {}\n".format(str(i+1),answer_list[i])
        return answer_text

if __name__ == "__main__":
    e = Ekwing()
    print("---- 翼课网答案获取系统 ----")
    print("By 御坂夏浔")
    print("---- 登录 ----")
    while True:
        username = cinput("翼课网手机号:")
        password = cinput("翼课网密码:")
        #username = '13533001468'
        #password = 'Misaka@=.123'
        login = e.login(username,password)
        if login[0]:
            print("---- 登录成功 ----")
            userinfo = e.get_user_info()
            print("你好，{}".format(userinfo['name']))
            print("---- 个人信息 ----")
            print("名称: {}".format(userinfo['name']))
            print("用户名: {}".format(userinfo['username']))
            print("学校: {}".format(userinfo['school']))
            print("班级: {}".format(userinfo['classes']))
            print("UID: {}".format(userinfo['uid']))
            break
        else:
            print("登陆失败:",login[1])
    print("---- 获取考试中 ----")
    exam_lists = e.get_exam_list()
    test_lists = e.get_test_list()
    index = 1
    for i in exam_lists:
        print(index,". 试题名称:{} 强制提交时间:{}".format(i['title'],i['sub_time']))
        index += 1
    for i in test_lists:
        print(index,". 试题名称:{} 余剩提交时间:{}".format(i['title'],i['left_time']))
        index += 1
    if index == 1:
        print("暂无考试")
        print("---- 程序终止 ----")
        print("回车以退出程序...")
        input()
    else:
        print("---- 获取完毕 --")
        while True:
            c = cinput("要获取答案的试题编号:",ntype="num")
            if c > (len(test_lists)+len(exam_lists)) or c < 0:
                print("错误: 请输入正确的试题编号")
                continue
            if c <= len(exam_lists):
                c = exam_lists[c-1]
                answer_page = e.get_exam_answer(c['url'])
                answer_json = ""
                is_do = False
                for i in answer_page.split("\n"):
                    if "            model_list:" in i:
                        answer_json += i.replace("            model_list:","")[:-1]
                answer_json = demjson.decode(answer_json)
                self_info = ""
                for i in answer_page.split("\n"):
                    if "            self_info: " in i:
                        self_info += i.replace("            self_info: ","")[:-1]
                answer_json = {"model_list":answer_json,'self_info':demjson.decode(self_info)}
                answer_list = []
                for i in answer_json['model_list'].keys():
                    value = answer_json['model_list'][i]
                    if value['model_type'] == "1":
                        answer_list.append({"name":value['name'],'value':value['real_text']})
                    elif value['model_type'] == "7":
                        temp = {"name":value['name'],'value':[]}
                        for o in value['ques_list']:
                            t_list = []
                            for p in o['answer']:
                                t_list.append(p[0])
                            t_list.sort()
                            temp['value'].append(t_list[0])
                        answer_list.append(temp)
                    elif value['model_type'] == "8":
                        temp = {"name":value['name'],'value':[]}
                        for o in value['ques_list']:
                            t_list = []
                            for p in o['answer']:
                                t_list.append(p[0])
                            t_list.sort()
                            temp['value'].append(t_list[0])
                        answer_list.append(temp)
                    elif value['model_type'] == "6":
                        temp = {"name":value['name'],'value':[]}
                        t_list = []
                        for p in value['answer']:
                            t_list.append(p[0])
                        t_list.sort()
                        temp['value'].append(t_list[0])
                        answer_list.append(temp)
                    elif value['model_type'] == "9":
                        temp = {"name":value['name'],'value':[]}
                        for o in value['ques_list']:
                            t_list = []
                            for p in o['answer']:
                                t_list.append(p[0])
                            t_list.sort()
                            temp['value'].append(t_list[0])
                        answer_list.append(temp)
                answer_text = ""
                for i in answer_list:
                    answer_text += i['name'] + "\n"
                    if type(i['value']) is str:
                        answer_text += i['value'] + "\n"
                    else:
                        i_index = 1
                        for o in i['value']:
                            ast = str(i_index) + ". " + o + "\n"
                            if len(ast) > 40:
                                ast = ast.replace(". ",".\n")
                            answer_text += ast
                            i_index +=1
                    answer_text += "\n"
                    filename = answer_json['self_info']['title'] + ".txt"
            else:
                c = test_lists[c-1-len(exam_lists)]
                filename = c['title'] + '.txt'
                hid = c['hid']
                subjects = e.get_hwitems(hid)
                answer_text = ''
                for i in subjects:
                    answer_text += i['title'] + '\n'
                    answer = e.get_keys_answer(i['keys'])
                    answer_text += answer+'\n'
            with open(filename,'wb') as fp:
                fp.write(answer_text.encode(encoding="UTF-8"))
            print("答案已成功获取，保存在{}".format(filename))
            if input("退出?(y/n):") == "y":
                print("---- 程序终止 ----")
                print("回车以退出程序...")
                input()
                break