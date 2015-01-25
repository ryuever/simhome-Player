# fork_server.py
import os, time, sys, xml.etree.ElementTree as ET
import json
from socket import *                      # get socket constructor and constants
import StringIO
import socket

# {"method":"get", "sender":"First", "date":"2014/07/31", "time":"00:01:00", "type":"int"}
# {"method":"get", "sender":"", "date":"", "time":"", "type":""}
# "date": "2014/07/31", "time": "00:01:00", "type": "int", "text": "25"
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def get_all(root, dict_ins):
    buf = StringIO.StringIO()
    print(dict_ins)
    print('in get_all')
    pattern = './/'
    if dict_ins['sender']:
        sender_pattern = "data[@sender='"+dict_ins['sender']+"']/value"
        # sender_pattern = "data[@sender='{}']/value".format(dict_ins['sender'])
        print(sender_pattern)
        pattern += sender_pattern
    else:
        pattern += 'value'
    if dict_ins['date']:
        date_pattern = '[@date="'+dict_ins['date']+'"]'
        print(date_pattern)
        pattern += date_pattern
    if dict_ins['time']:
        time_pattern = '[@time="'+dict_ins['time']+'"]'
        print(time_pattern)
        pattern += time_pattern
    if dict_ins['type']:
        type_pattern = '[@type="'+dict_ins['type']+'"]'
        print(type_pattern)
        pattern += type_pattern
    print(pattern)
    for item in root.findall(pattern):
        attr = item.attrib
        text = item.text 
        result = '<value date="' + attr['date'] + '" ' + 'time="' + attr['time'] + '" ' \
            + 'type="' + attr['type'] + '">' + text + '</value>\n'

        buf.write(bytes(result))
    output = buf.getvalue()
    buf.close()
    return output

# {"method":"remove", "sender":"First", "date":"2014/07/31", "time":"00:01:00", "type":"int"}
# {"method":"remove", "sender":"", "date":"20140820", "time":"", "type":""}
def remove(root, dict_ins):
    print(dict_ins)
    print('in get_all')
    pattern = './/'
    buf = io.StringIO()

    if not (dict_ins['date'] or dict_ins['time'] or dict_ins['type']):
        if dict_ins['sender']:
            parent = '.'
            pattern = 'data[@sender="'+dict_ins['sender']+'"]'
            print(parent)
            print(pattern)
        else:
            parent = '.'
            pattern = 'data'
    else:
        if dict_ins['sender']:
            parent = 'data[@sender="'+dict_ins['sender']+'"]'
            sender_pattern = "data[@sender='{}']/value".format(dict_ins['sender'])
            print(sender_pattern)
            pattern += sender_pattern
        else:
            pattern += 'value'
            parent = 'data'

        if dict_ins['date']:
            date_pattern = '[@date="'+dict_ins['date']+'"]'
            print(date_pattern)
            pattern += date_pattern
        if dict_ins['time']:
            time_pattern = '[@time="'+dict_ins['time']+'"]'
            print(time_pattern)
            pattern += time_pattern
        if dict_ins['type']:
            type_pattern = '[@type="'+dict_ins['type']+'"]'
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
def insert(root, tree, dict_ins):
    print(dict_ins)
    print('in get_all')
    pattern = './/'

    if not (dict_ins['date'] or dict_ins['time'] or dict_ins['type']):
        raise Exception("error message")
    else:
        attrib = dict((k, dict_ins[k]) for k in ('date', 'time', 'type') if k in dict_ins)
        if dict_ins['sender']:
            parent = 'data[@sender="'+dict_ins['sender']+'"]'
            print(dict_ins['date'])
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
    # print(dict_ins['text'])
    # builder.data(dict_ins['text'])
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
