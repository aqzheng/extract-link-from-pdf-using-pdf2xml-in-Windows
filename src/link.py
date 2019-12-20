# -*- coding: UTF-8 -*-
import os
import xml.etree.ElementTree as ET
import unicodedata
import operator
import re
from nltk.tokenize import sent_tokenize
def get_link(pdfPath):
    # 获取相关文件路径
    pwd = os.path.dirname(os.path.abspath(__file__)) # 当前文件路径
    father_path = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".") # 当前文件的父路径
    exePath = os.path.join(father_path, 'tool', 'pdftoxml.exe') # pdf2xml 路径
    pdfname = os.path.basename(pdfPath).split('.')[0]
    htmlName = pdfname + '.html'
    htmlPath = os.path.join(father_path, 'html', htmlName) # 将pdf转化为html存储的路径
    # 执行pdf2xml工具
    run_exe = exePath + ' ' + '-noImage -noImageInline' + ' ' + pdfPath + ' ' + htmlPath
    os.system(run_exe)

    tree = ET.parse(htmlPath)
    root = tree.getroot()
    # pre_process
    y_diff = {}
    fsizes = {}
    pre_Y = 0
    for pages in root.findall('PAGE'):
        for texts in pages.findall('TEXT'):
            y_sizes = {}
            for token in texts.findall('TOKEN'):
                fsizes[round(float(token.attrib['font-size']))] = fsizes.get(round(float(token.attrib['font-size'])), 0) + 1
                y_sizes[float(token.attrib['y'])]  = y_sizes.get(float(token.attrib['y']), 0) + 1
            now_Y = max(y_sizes, key=y_sizes.get)
            y_diff[round(abs(now_Y-pre_Y))] = y_diff.get(round(abs(now_Y-pre_Y)), 0) + 1
            pre_Y = now_Y
    max_fs = 0
    for size in fsizes.keys():
        if max_fs == 0 or fsizes[size]>fsizes[max_fs]:
            max_fs = size

    new_l = sorted(y_diff.items(), key=operator.itemgetter(1), reverse=True)[:7]

    limit1 = max(new_l[1][0],new_l[0][0])
    limit3 = min(new_l[1][0],new_l[0][0])
    limit2 = 3

    xroot = ET.Element("Document")
    chunk = ET.SubElement(xroot, "chunk")
    pre_Y = 0
    for pages in root.findall('PAGE'):
        for texts in pages.findall('TEXT'):
            is_first = True
            y_sizes = {}
            for token in texts.findall('TOKEN'):
                y_sizes[float(token.attrib['y'])]  = y_sizes.get(float(token.attrib['y']), 0) + 1
            now_Y = max(y_sizes, key=y_sizes.get)
            for token in texts.findall('TOKEN'):
                word = token.text   
                if word and len(word.replace(' ','')) > 0:
                    if is_first and (pre_Y == 0 or abs(now_Y - pre_Y) >= limit2):
                        chunk = ET.SubElement(xroot, "chunk")
                    p_yloc = float(token.attrib['y'])
                    ET.SubElement(chunk, "token", pages=pages.attrib['id'], x=token.attrib['x'], y=token.attrib['y'], font_size=token.attrib['font-size'], bold=token.attrib['bold']).text = word
                is_first = False
            pre_Y = now_Y
 
    tree = ET.ElementTree(xroot)
    newxroot = tree.getroot()

    pre_footnote_list = []
    link_list = []
    for chunk_pos,achunk in enumerate(newxroot.findall('chunk')):
        tokens = achunk.findall('token')
        if len(tokens) == 0 :
            continue
        else:
            # sentence = ' '.join([str(i.text) for i in tokens])
            sentence = get_sentence(tokens, False)

            # link_reg = re.compile('http[s]?://(?:[a-zA-Z]*|[0-9]*|[\$-_@.&+]*|[!*\(\),]*|(?:\%[0-9a-fA-F]*[0-9a-fA-F]*))').findall(sentence)
            link_reg = re.compile('[a-zA-Z]+://[^\s]*').findall(sentence)
            if link_reg and round(float(tokens[0].attrib['font_size'])) != max_fs:
                # print(link_reg)
                footnote_num = -1
                if sentence.split()[0].isdigit():
                    footnote_num = sentence.split()[0]
                else:
                    if chunk_pos > 1:
                        pre_tokens =  newxroot.findall('chunk')[chunk_pos-1].findall('token')
                        pre_sentence = get_sentence(pre_tokens, False)
                        if round(float(pre_tokens[0].attrib['font_size'])) != max_fs and pre_sentence.split()[0].isdigit():
                            footnote_num = pre_sentence.split()[0]
                        elif chunk_pos > 2:
                            pre_tokens =  newxroot.findall('chunk')[chunk_pos-2].findall('token')
                            pre_sentence = get_sentence(pre_tokens, False)
                            if round(float(pre_tokens[0].attrib['font_size'])) != max_fs and pre_sentence.split()[0].isdigit():
                                footnote_num = pre_sentence.split()[0]

                if footnote_num != -1:
                    now_link = link_reg[0]
                    now_pos = chunk_pos
                    if sentence.split()[-1] == now_link:
                        while 1 :
                            try :
                                next_token = newxroot.findall('chunk')[now_pos+1].findall('token')
                                next_sentence = get_sentence(next_token, True).split()
                                if ('/' in next_sentence[0] or ('.' in next_sentence[0] and next_sentence[0][-1] != '.')) and not next_sentence[0][0].isdigit():
                                    now_link += next_sentence[0]
                                    if len(next_sentence) == 1 :
                                        now_pos += 1
                                    else:
                                        break
                                else:
                                    break
                            except:
                                break
                   
                    link_list.append(now_link)
                    # print(now_link)
                    link_info = {
                        'index': footnote_num,
                        'link': now_link,
                        'page_id': tokens[0].attrib['pages'],
                        'x': None,
                        'y': None
                    }
                    ids = tokens[0].attrib['pages']
                    
                    for pages in root.findall('PAGE'):
                        if pages.attrib['id'] == ids :
                            link_find = False
                            for texts in pages.findall('TEXT'):
                                fsizes = {}
                                for token in texts.findall('TOKEN'):
                                    fsizes[round(float(token.attrib['font-size']))] = fsizes.get(round(float(token.attrib['font-size'])), 0) + 1
                
                                now_fs = max(fsizes, key=fsizes.get)
                                tests_list = texts.findall('TOKEN')
                                for pos in range(len(tests_list)):
                                    # # print( str(pos) + ' ' + str(tests_list[pos].text) + ' ' + str(tests_list[pos].attrib['font-size']) + ' ' + tests_list[pos].attrib['x'] + ' ' + tests_list[pos].attrib['y'])
                                    # if float(tests_list[pos].attrib['x']) == 389.023 :# and tests_list[pos].attrib['y'] == 539.462:
                                    #     print(tests_list[pos].text)
                                    #     print(footnote_num)
                                    #     print(tests_list[pos].text == footnote_num)
                                    #     print(now_fs == max_fs)
                                    # if  str(tests_list[pos].text) == footnote_num and now_fs == max_fs:
                                    #     link_info['x'] = tests_list[pos].attrib['x']
                                    #     link_info['y'] = tests_list[pos].attrib['y']
                                    #     pre_footnote_list.append(link_info)

                                    if (pos == 0 or float(tests_list[pos-1].attrib['y']) > float(tests_list[pos].attrib['y']) )and \
                                           (pos == len(tests_list) - 1 or float(tests_list[pos + 1].attrib['y']) > float(tests_list[pos].attrib['y'])) and \
                                           round(float(tests_list[pos].attrib['font-size'])) != max_fs and str(tests_list[pos].text) == footnote_num and now_fs == max_fs:
                                        link_info['x'] = tests_list[pos].attrib['x']
                                        link_info['y'] = tests_list[pos].attrib['y']
                                        pre_footnote_list.append(link_info)
                                        link_find = True
                            if link_find == False:
                                for texts in pages.findall('TEXT'):
                                    tests_list = texts.findall('TOKEN')
                                    if len(tests_list) == 1 and str(tests_list[0].text) == footnote_num:
                                            link_info['x'] = tests_list[0].attrib['x']
                                            link_info['y'] = tests_list[0].attrib['y']
                                            pre_footnote_list.append(link_info)
                                            link_find = True
                    
    # pre_footnote_list = [dict(t) for t in set([tuple(d.items()) for d in pre_footnote_list])]
    pre_list = []
    for i in pre_footnote_list:
        is_exist = False
        for j in pre_list:
            if i == j :
                is_exist = True
        if is_exist == False:
            pre_list.append(i)
    pre_footnote_list = pre_list
    # print(pre_footnote_list)                                                             
    ALL_paragraph = []
    content = ""
    pre_Y = 0
    is_done = False
    pre_fs = 0
    for pages in root.findall('PAGE'):
        page_id = re.compile('[1-9]\d*').findall(pages.attrib['id'])[0]
        for texts in pages.findall('TEXT'):
            is_first = True
            fsizes = {}
            y_sizes = {}
            for token in texts.findall('TOKEN'):
                y_sizes[float(token.attrib['y'])]  = y_sizes.get(float(token.attrib['y']), 0) + 1
                fsizes[round(float(token.attrib['font-size']))] = fsizes.get(round(float(token.attrib['font-size'])), 0) + 1

            now_fs = max(fsizes, key=fsizes.get)
            now_Y = max(y_sizes, key=y_sizes.get)
            for token in texts.findall('TOKEN'):
                if is_done:
                    break
                if (token.text == 'References' and int(page_id) > 3 and (token.attrib['bold'] == 'yes' or round(float(token.attrib['font-size'])) >= max_fs)):
                    ALL_paragraph.append(content)
                    is_done = True
                    break
                pos = [id for id,x in enumerate(pre_footnote_list) if x['page_id'] == pages.attrib['id'] and x['x'] == token.attrib['x'] and x['y'] == token.attrib['y']]
                if len(pos) == 0:
                    word = token.text          
                else:
                    word = pre_footnote_list[pos[0]]['index'] + '< ' + pre_footnote_list[pos[0]]['link'] + ' >'

            
                if word and len(word.replace(' ','')) > 0:
                    if is_first and (pre_Y == 0 or round(abs(now_Y - pre_Y)) > limit1):
                        if len(content.split()) > 5 :
                            if len(ALL_paragraph) > 0 and ALL_paragraph[-1][-1] == '-':
                                ALL_paragraph[-1] = ALL_paragraph[-1][0:-1] + content
                            elif content[0].islower():
                                if len(ALL_paragraph) > 0 and ALL_paragraph[-1][0].isdigit() and ALL_paragraph[-1][1] == ' ':
                                    ALL_paragraph[-2] += ' ' + content
                                elif len(ALL_paragraph) > 0:
                                    ALL_paragraph[-1] += ' ' + content
                            elif len(ALL_paragraph) > 0 and (ALL_paragraph[-1][-1].isdigit() or ALL_paragraph[-1][-1].isalpha()):
                                ALL_paragraph[-1] += ' ' + content
                            else:
                                ALL_paragraph.append(content)
                        content = word
                    else:
                        if is_first and word[0].isupper() and content[-1] == '.':
                            ALL_paragraph.append(content)
                            content = word
                        elif is_first and content[-1] == '-':
                            content = content[0:-1] + word
                        else:
                            content += ' ' + word      
                is_first = False
            pre_fs = now_fs
            pre_Y = now_Y
   
    footnote_link = []
    for pos1,i in enumerate(ALL_paragraph):
        for pos2,j in enumerate(i.split()):
            link_flag = False
            for k in pre_footnote_list:
                if k['index'] + '< '+ k['link'] + ' >' == j :
                    link_flag = True
                    break
            if link_flag == False:
                try :
                    ALL_paragraph[pos1][pos2] = unicodedata.normalize('NFKD', j)
                except :
                    continue
        # print(i)
        # print()
  
    for i in pre_footnote_list:
        link_info = {
            'pos_flag': 1,
            'index': i['index'],
            'link': i['link'],
            'context': None,
        }
        context = [id for id,x in enumerate(ALL_paragraph) if i['index'] + '< '+ i['link'] + ' >' in x]
        if len(context) == 1  :
            context = ALL_paragraph[context[0]].replace(i['index'] + '< '+ i['link'] + ' >', '[ ' + i['link'] + ' ]')
            now_reg = re.compile('<\s([a-zA-Z]+://[^\s]*)\s>').findall(context)
            for j in now_reg:
                context = context.replace(j, '').replace('<  >','')
            link_info['context'] = context
            footnote_link.append(link_info)

    bodytext_list = []
    body_link_num = 1
    for pos_i,i in enumerate(ALL_paragraph):
        if pos_i == 0:
            continue
        link_reg = re.compile('[a-zA-Z]+://[^\s]*').findall(i)
        if link_reg:
            for link in link_reg:
                flag = 1
                for j in link_list:
                    if link in j:
                        flag = 0
                        break
                if flag:
                    
                    body_text = i.split()
                    for pos in range(len(body_text)):
                        if link in body_text[pos] and pos+1 != len(body_text) and \
                            ('/' in body_text[pos+1] or ('.' in body_text[pos+1] and body_text[pos+1][-1] != '.')):
                            link = body_text[pos] + ' ' + body_text[pos+1]
                            if link[0] == '(' :
                                link = link[1:]
                    if link[-1] == ')':
                        link = link[0:-1]
                    elif (link[-1] == '.' or link[-1] == ',') and link[-2] == ')':
                        link = link[0:-2]
                    link1 = link.replace(' ','')
                    link_info = {
                        'pos_flag': 0,
                        'index': body_link_num,
                        'link': link1,
                        'context': i.replace(link, '[ ' + link1 + ' ]'),
                    }
                    bodytext_list.append(link_info)
                    body_link_num += 1      
    return footnote_link, bodytext_list

def get_sentence(tokens, pre_url):
    sentence = None
    for token_pos, token in enumerate(tokens):
        if token_pos == 0:
            sentence = token.text
        else:
            if pre_url:
                if len(token.text) == 1:
                    if not token.text.isalnum() and (token_pos + 1 != len(tokens) and '/' in tokens[token_pos+1].text):
                        sentence += token.text
                    else:
                        sentence += ' ' + token.text
                        pre_url = False
                elif '/' in token.text or ('.' in token.text and token.text[-1] != '.'):
                    sentence += token.text
                else:
                    sentence += ' ' + token.text
                    pre_url = False
            else:
                sentence += ' ' + token.text
        if re.compile('[a-zA-Z]+://[^\s]*').findall(token.text):
            pre_url = True
    return sentence

