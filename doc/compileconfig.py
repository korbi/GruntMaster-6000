# -*- coding: utf-8 -*-
#!/usr/bin/python
'''

Script compiling config files created by hand.

ToDo:
check if it is possible to solve 'extends'

History:
0.2 removes all unnecesary data ('extends' attribute, and Nodes with 'abstract' attributes)
0.1 can extends Nodes which have 'extends' attribute

'''

import re, os, xml, sys
from xml.dom import minidom, Node

__VERSION__ = 0.2

def concChilds(first,second):
    pass

def removeContent(node, nodeTypes=[], attributes=[], nodeWithAttributes=[]):
    toRemove=[]
    #c = node
    for c in node.childNodes:
        rem = False
        if c.nodeType in nodeTypes:
            toRemove.append(c)
            rem = True
        elif c.nodeType==Node.ELEMENT_NODE:
            if len(c.attributes) and len(nodeWithAttributes):
                for a in nodeWithAttributes:
                    if c.hasAttribute(a):
                        toRemove.append(c)
                        rem = True
                        break
            if rem==False and c.hasChildNodes():
                removeContent(c,nodeTypes,attributes,nodeWithAttributes)
            for x in attributes:
                if c.hasAttribute(x):
                    c.removeAttribute(x)
    for x in toRemove:
        node.removeChild(x)

def compile(mainNode):
    cNodes = mainNode.childNodes
    nodeExtended = {} # czyli rozszerzone i przez co
    notExtending = [] # czyli nie rozszerzające niczego (będzie modyfikowana - dodawane nowe pozycje)
    extending = {} # słownik oznaczający kto co rozszerza
    nodesToRemove = []
    allNodes = []
    #extended - rozszerzony
    #extending - rozszerzający
    for c in cNodes:
        if c.nodeType==Node.ELEMENT_NODE:
            allNodes.append(c.nodeName)
            if c.hasAttribute('extends'):
                extended = c.getAttribute('extends')
                el = extended.split(' ')
                tmp = []
                for e in el:
                    if el!=' ':
                        tmp.append(e)
                        if nodeExtended.has_key(e)==False:
                            nodeExtended[e] = [c]
                        else:
                            nodeExtended[e].append(c)
                #print c.nodeName, 'extends', extended
                if not extending.has_key(c.nodeName):
                    extending[c.nodeName] = tmp
                else:
                    #here should rise an Error!
                    pass
            else:
                notExtending.append(c)
                #print c.nodeName,'is not extending'
            if c.hasAttribute('abstract'):
                nodesToRemove.append(c)
                #print c.nodeName,'will be removed'
    for n in notExtending: # dla n ktory nic juz nie rozszerza
        if nodeExtended.has_key(n.nodeName): # jesli n jest rozszerzany
            #print n.nodeName
            for e in nodeExtended[n.nodeName]: #dla każdego e rozszerzajacego n
                #print e.nodeName
                for c in n.childNodes:
                    #print c.nodeName
                    if len(e.getElementsByTagName(c.nodeName))==0:
                        e.appendChild(c.cloneNode(False))            #dodaj do e dziecko c
                extending[e.nodeName].remove(n.nodeName)
                if len(extending[e.nodeName])==0:
                    notExtending.append(e)
                #print e.nodeName, extending[e.nodeName]
                
    for c in nodesToRemove:
        mainNode.removeChild(c)

if __name__=='__main__':
    #parsuj argumenty
    if len(sys.argv)<3:
        print "not enough arguments"
        print "try: %s <input file name> <output file name>"%sys.argv[0]
        sys.exit(0)
    inputfile = sys.argv[1]
    outputfile =  sys.argv[2]
    #wczytaj konfigurację
    DOMTree = minidom.parse(inputfile)
    cNodes = DOMTree.childNodes
    #zastosuj atrybuty
    # abstract - nie powinny się znaleźć w pliku
    # extends - dołącz pola z klas bazowych
    # predefined
    removeContent(DOMTree,[Node.COMMENT_NODE,Node.TEXT_NODE])
    info = DOMTree.createComment('File created from %s using %s ver. %s'%(inputfile,sys.argv[0],__VERSION__))
    for c in cNodes:
        if c.nodeType==Node.ELEMENT_NODE:
            #print 'element',c.nodeName
            if c.nodeName=='configuration':
                #removeContent(c,[Node.COMMENT_NODE,Node.TEXT_NODE])
                compile(c)
                DOMTree.insertBefore(info, c)
                removeContent(c,attributes=['extends'],nodeWithAttributes=['abstract']);
    o = open(outputfile,'w')
    o.write(DOMTree.toprettyxml(encoding='UTF-8'))
    #o.write(DOMTree.toxml(encoding='UTF-8'))
    o.close()
    #wypisz skompilowaną wersję
    #print DOMTree.toxml()
