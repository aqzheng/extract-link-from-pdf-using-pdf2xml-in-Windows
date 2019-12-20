# -*- coding: UTF-8 -*-
import os
import sys
import json
import re
import xml.etree.ElementTree as ET
sys.path.append(os.path.abspath(__file__))
from src.link import get_link

import datetime

def extract(pdfPath):
    # 定义数据类型
    starttime = datetime.datetime.now()
    data = {
        'resource': None,
    }
    link = {
        'pos_flag': None,
        'index': None,
        'link': None,
        'context': None,
    }
    pdf_content_list = []

    # 2. 使用pdf2xml工具来抽取link，context
    footnote_list, bodytext_list = get_link(pdfPath)

    for i in footnote_list:
        link['pos_flag'] = i['pos_flag']
        link['index'] = i['index']
        link['link'] = i['link']
        link['context'] = i['context']
        pdf_content_list.append({'pos_flag': i['pos_flag'], 'index': i['index'], 'link': i['link'], 'context': i['context']})

    num = 0
    
    for i in bodytext_list:
        link['pos_flag'] = i['pos_flag']
        link['index'] = i['index'] + num
        link['link'] = i['link']
        link['context'] = i['context']
        pdf_content_list.append({'pos_flag': i['pos_flag'], 'index': i['index']+num, 'link': i['link'], 'context': i['context']})
    
    endtime = datetime.datetime.now()
    data['resource'] = pdf_content_list

    return data

def gci(filepath):
    if os.path.isfile(filepath):
        if os.path.splitext(filepath)[1]=='.pdf':
            result = extract(filepath)
            with open(os.path.splitext(filepath)[0] + '.jsonl', 'w', encoding='utf-8') as fp:
                fp.write(json.dumps(result) + '\n')
    else:
        files = os.listdir(filepath)
        for fi in files:
            fi_d = os.path.join(filepath, fi)
            if os.path.isdir(fi_d):
                gci(fi_d)
            elif os.path.splitext(fi)[1]=='.pdf':
                result = extract(fi_d)
                with open(os.path.splitext(fi_d)[0] + '.jsonl', 'w') as fp:
                    fp.write(json.dumps(result) + '\n')
                            
if __name__ == '__main__':
    gci('C://Users//admin//Desktop//pdf2xml//pdf')

