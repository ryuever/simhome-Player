# fork_server.py
import os, time, sys, xml.etree.ElementTree as ET
import json
import StringIO
import re
from datetime import datetime

# {"method":"get", "sender":"First", "date":"2014/07/31", "time":"00:01:00", "type":"int"}
# {"method":"get", "sender":"", "date":"", "time":"", "type":""}
# "date": "2014/07/31", "time": "00:01:00", "type": "int", "text": "25"
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def inquery(root, sorted_request_list):
    buf = StringIO.StringIO()
    print(sorted_request_list)
    index = 0
    while index < len(sorted_request_list):
        print 'in while loop'
        item = sorted_request_list[index]
        print 'first : ', item['flag']
        if item['flag'] == '0':            
            print 'second : '
            pattern = './/'
            if item['sender']:
                sender_pattern = "data[@sender='"+item['sender']+"']/value"
                print(sender_pattern)
                pattern += sender_pattern
            else:
                pattern += 'value'
            if item['date']:
                date_pattern = '[@date="'+item['date']+'"]'
                print(date_pattern)
                pattern += date_pattern
            if item['time']:
                time_pattern = '[@time="'+item['time']+'"]'
                print(time_pattern)
                pattern += time_pattern
            print(pattern)
            for item in root.findall(pattern):
                attr = item.attrib
                text = item.text 
                result = '<value date="' + attr['date'] + '" ' + 'time="' + attr['time'] + '" ' \
                         + 'type="' + attr['type'] + '">' + text + '</value>\n'
                buf.write(bytes(result))
        else:
            if item['flag'].endswith('max'):
                print 'in else'
                index += 1
                print 'else ', index
                item_next = sorted_request_list[index]
                print 'item_next :', item_next
                time_min = int(item_next['time'].replace(':',''))
                time_max = int(item['time'].replace(':',''))
                print 'item["date"], time_max, time_min', item['date'], time_max, time_min
                if item['date']:
                    pass
                else:
                    print 'second loop'                    
                    for ele in root.findall('.//value'):
                        ele_attr = ele.attrib
                        ele_text = ele.text 
                        item_time = int(ele_attr['time'].replace(':',''))
                        print item_time
                        start = False
                        print 'time_min, item_tiem, time_max', time_min, item_time, time_max
                        if time_min < item_time < time_max:
                            print "matched"
                            ele_result = '<value date="' + ele_attr['date'] + '" ' + 'time="' + ele_attr['time'] + '" ' \
                                     + 'type="' + ele_attr['type'] + '">' + ele_text + '</value>\n'
                            buf.write(bytes(ele_result))
                            start = True
                        elif start == True:
                            break
                        else:
                            continue
        index += 1            
    output = buf.getvalue()
    buf.close()
    return output

# {"method":"remove", "sender":"First", "date":"2014/07/31", "time":"00:01:00", "type":"int"}
# {"method":"remove", "sender":"", "date":"20140820", "time":"", "type":""}
def remove(root, sorted_request_list):
    pattern = './/'
    buf = StringIO.StringIO()


    if not (item['date'] or item['time'] or item['type']):
        if item['sender']:
            parent = '.'
            pattern = 'data[@sender="'+item['sender']+'"]'
            print(parent)
            print(pattern)
        else:
            parent = '.'
            pattern = 'data'
    else:
        if item['sender']:
            parent = 'data[@sender="'+item['sender']+'"]'
            sender_pattern = "data[@sender='{}']/value".format(item['sender'])
            print(sender_pattern)
            pattern += sender_pattern
        else:
            pattern += 'value'
            parent = 'data'

        if item['date']:
            date_pattern = '[@date="'+item['date']+'"]'
            print(date_pattern)
            pattern += date_pattern
        if item['time']:
            time_pattern = '[@time="'+item['time']+'"]'
            print(time_pattern)
            pattern += time_pattern
        if item['type']:
            type_pattern = '[@type="'+item['type']+'"]'
            print(type_pattern)
            pattern += type_pattern

    for item in root.findall(parent):
        for child in root.findall(pattern):
            item.remove(child)
            attr = child.attrib
            text = child.text
            result = '<value date="' + attr['date'] + '" ' + 'time="' + attr['time'] + '" ' \
                + 'type="' + attr['type'] + '">' + text + '</value>\n'
            buf.write(result)
        ET.dump(root)
    output = buf.getvalue()
    buf.close()
    return output

# {"method":"insert", "sender":"First", "date":"2014/07/01", "time":"00:01:00", "type":"int", "text":"200"}
# {"method":"insert", "sender":"Second", "date":"2014/06/31", "time":"00:01:00", "type":"int", "text":200}
# {"method":"insert", "sender":"First", "date":"20140701", "time":"00:01:00", "type":"int", "text":"200"}
def insert(root, tree, item):
    print(item)
    print('in get_all')
    pattern = './/'

    if not (item['date'] or item['time'] or item['type']):
        raise Exception("error message")
    else:
        attrib = dict((k, item[k]) for k in ('date', 'time', 'type') if k in item)
        if item['sender']:
            parent = 'data[@sender="'+item['sender']+'"]'
            print(item['date'])
        else:
            parent = 'data'

        subele = '<value date="' + attr['date'] + '" ' + 'time="' + attr['time'] + '" ' \
            + 'type="' + attr['type'] + '">' + text + '</value>\n'

    print(subele)
    ele = ET.fromstring(subele)
    #    print(ET.dump(e))
            
    # # create new element
    # builder = ET.TreeBuilder()
    # builder.start('value', attrib)
    # print(item['text'])
    # builder.data(item['text'])
    # builder.end('value')
    # subele = builder.close()
    # print("subele is : ", subele)
    # print(ET.dump(subele))    

    # print("parent is : ", parent)
    # print("attrib is : ", attrib)
    for item in root.findall(parent):
        if item:
            # sub = SubElement(item, 'value',attrib)
            item.append(ele)
            # print(sub)
            # ET.SubElement(item,'value',attrib)
    print(ET.dump(root))

    import time
    filename = 'update_' + str(time.time()).replace('.', '_') + '.xml'
    tree.write(filename)

    output = "1 records is appened"
    return output

# for only one xml record to tuple list
def single_xml2lst(xml_data):
    regexpattern = '<|>| |"'
    splited_data = re.split(regexpattern, xml_data)
    temp_lt = []
    temp_lt.append(splited_data[3])
    temp_lt.append(splited_data[6])
    temp_lt.append(splited_data[9])
    temp_lt.append(splited_data[14])
    return tuple(temp_lt)

def multi_xml2lst(xml_data):
    root = ET.fromstring('<root>\n' + xml_data + '</root>')
    res = [(item.attrib['sender'],
            datetime.strptime(item.attrib['date']+ item.attrib['time'], "%Y%m%d%H:%M"), item.text)
           for item in root]
    return res
    
