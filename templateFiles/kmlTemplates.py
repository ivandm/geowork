

SCREEN_OVERLAY="""<ScreenOverlay id="generated"><name>%(screenOverlayName)s</name>
        <visibility>1</visibility>
        <open>0</open>
        <Icon><href>%(screenOverlayIconURL)s</href></Icon>
        <overlayXY x="-10" y="-20" xunits="pixels" yunits="pixels"/>
        <screenXY x="0" y="0" xunits="fraction" yunits="fraction"/>
    </ScreenOverlay>"""
attrs_SCREEN_OVERLAY = {
    'screenOverlayName'         : u'generated by Adventure2Italy',
    'screenOverlayIconURL'      :'',
    }

FOLDER_TRACK="""<Folder><name>%(folderTrackName)s</name>
        <Placemark id="%(placemarkId)s"><name>%(placemarkName)s</name><description><![CDATA[%(placemarkDescription)s]]></description>
        <Style id="%(placemarkStyleId)s">
        %(balloonStyle)s
        <LineStyle><color>%(lineColor)s</color><width>%(lineWidth)s</width></LineStyle>
        </Style>
        <ExtendedData>%(folderTrackExtendData)s</ExtendedData>
        <LineString><coordinates>%(coords)s</coordinates></LineString>
        </Placemark>
    </Folder>"""
attrs_FOLDER_TRACK={
    'folderTrackName': '',
    'placemarkId': '',
    'placemarkName': '',
    'placemarkDescription': '',
    'placemarkStyleId': '',
    'balloonStyle': '',
    'lineColor': '',
    'lineWidth': '',
    'folderTrackExtendData': '',
    'coords': '',
    }
    
BALLOON_STYLE="""<BalloonStyle>
            <text><![CDATA[%(value)s]]></text>
        </BalloonStyle>"""
attrs_BALLOON_STYLE={
    'value': ''
    }

DATA="""<Data name="%(name)s"><value>%(DATA)s</value></Data>"""
attrs_DATA={
    'name'  : '',
    'DATA' : '',
    }
    
CDATA="""<Data name="%(name)s"><value><![CDATA[%(CDATA)s]]></value></Data>"""
attrs_CDATA={
    'name'  : '',
    'CDATA' : '',
    }

XML="""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
    <name>%(documentName)s</name>
    <open>1</open>
    %(folders)s
    %(screeOveraly)s
    </Document>
</kml>"""
attrs_XML = {
    'documentName'  : u'',
    'folders'       : '',
    'screeOveraly'  : SCREEN_OVERLAY % attrs_SCREEN_OVERLAY,
    }
 
import copy 

def clean(this_dict, default_dict):
    new_dict = copy.copy(this_dict)
    for k in this_dict.keys():
        if not k in default_dict.keys():
            del new_dict[k]
    return new_dict
    
def insertFOLDERS(kwargs):
    folders = []
    lista_folders_attr = []
    if not type(kwargs) in (list, tuple):
        kwargs = [kwargs]
    for attr in kwargs:
        d = copy.copy(attrs_FOLDER_TRACK)
        d.update(attr)
        
        # INSERISCE balloonStyle
        bs = copy.copy(attrs_BALLOON_STYLE)
        if type(d['balloonStyle']) == type({}):
            bs.update(d['balloonStyle'])
        d['balloonStyle'] = BALLOON_STYLE % bs
        
        # INSERISCE folderTrackExtendData
        lista_extra = []
        if type(d['folderTrackExtendData']) in (list, tuple):
            for dato in d['folderTrackExtendData']:
                if type(dato) == type({}):
                    if dato.has_key('DATA'):
                        new = copy.copy(attrs_DATA)
                        new.update(dato)
                        lista_extra.append(DATA % new)
                    if dato.has_key('CDATA'):
                        new = copy.copy(attrs_DATA)
                        new.update(dato)
                        lista_extra.append(CDATA % new)
        d['folderTrackExtendData'] = ''.join(lista_extra)
        
        lista_folders_attr.append(d)
    for attr in lista_folders_attr:
        folders.append(FOLDER_TRACK % attr)
    return ''.join(folders)
    
def kml(**kwargs):
    folders = ''
    if kwargs.has_key('attrs_FOLDER_TRACK'):
        folders = insertFOLDERS(kwargs['attrs_FOLDER_TRACK'])
        
    attrs_SCREEN_OVERLAY.update(kwargs.get('attrs_SCREEN_OVERLAY', attrs_SCREEN_OVERLAY))
    
    attrs_XML.update({'documentName': kwargs.get('documentName', attrs_XML['documentName'])})
    attrs_XML['folders'] = folders
    attrs_XML['screeOveraly'] = SCREEN_OVERLAY % attrs_SCREEN_OVERLAY
    kmlFile = XML % attrs_XML
    return kmlFile
    
"""
f = open('kml.kml', 'wb')
f.write(kml(
    documentName = 'TEST KML',
    attrs_SCREEN_OVERLAY = 
            {
            'screenOverlayName'         : u'generated by Adventure2Italy',
            'screenOverlayIconURL'      :'www.adventure2italy',
            },
    attrs_FOLDER_TRACK =
            {
            'folderTrackName': 'NOME FOLDER',
            'placemarkId': 'ID',
            'placemarkName': 'PLACE MARK NAME',
            'placemarkDescription': 'PLACE MARK DESCRIPTION',
            'placemarkStyleId': 'PLACEMARK STYLE ID',
            'balloonStyle': {'value': 'BALLONSTYLE'},
            'lineColor': 'ff000000',
            'lineWidth': '6',
            'folderTrackExtendData': 
                    [
                    'provaSTR',
                    ['PROVA lista'],
                    {'name':'NAME1', 'DATA':'VALUE1'},
                    {'name':'NAME2', 'CDATA':'VALUE2'},
                    ],
            'coords': '''10.02458,50.46964 10.02472,50.46992 10.02475,50.47009 10.02470,50.47060 10.02462,50.47098 10.02460,50.47218 10.02467,50.47253 10.02478,50.47275 10.02492,50.47293 10.02533,50.47327
            10.02551,50.47348 10.02563,50.47369 10.02569,50.47389 10.02570,50.47407 10.02562,50.47474 10.02562,50.47495 10.02563,50.47511 10.02569,50.47524 10.02579,50.47536 10.02598,50.47550
            10.02621,50.47566 10.02654,50.47585 10.02691,50.47600 10.02738,50.47614 10.02825,50.47632 10.02854,50.47635 10.02883,50.47637 10.02912,50.47638 10.02939,50.47637 10.02971,50.47634
            10.03037,50.47721 10.03135,50.47856 10.03189,50.47924 10.03224,50.47961 10.03259,50.48003 10.03278,50.48034 10.03289,50.48093 10.03290,50.48117 10.03315,50.48175 10.03342,50.48203
            10.03360,50.48227 10.03377,50.48252 10.03381,50.48264 10.03388,50.48293 10.03393,50.48361 10.03396,50.48493 10.03551,50.48524 10.03941,50.48625 10.04416,50.48764 10.04425,50.48769
            10.04428,50.48773 10.04420,50.48814 10.04488,50.48825 10.04787,50.48882 10.04896,50.48899 10.04944,50.48905 10.05106,50.48920 10.05733,50.48967 10.06050,50.48984 10.06085,50.48984
            10.06134,50.48978''',
            },
    ))
f.close()
"""