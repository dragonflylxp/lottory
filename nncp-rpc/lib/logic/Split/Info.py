#encoding=utf-8
__LOT_INFOS__ = {
    1: {'lotId': 1, 'lotName': '胜负彩', 'dbId': 'sfc', 'tableId': 'sfc', 'columnId': 'f',
        'tradeDir': 'sfc', 'lotType': []},
    3: {'lotId': 3, 'lotName': '双色球', 'dbId': 'ssq', 'tableId': 'ssq', 'columnId': 'l',
        'tradeDir': 'ssq', 'lotType': []},
    4: {'lotId': 4, 'lotName': '七星彩', 'dbId': 'qx', 'tableId': 'qx', 'columnId': 'f',
        'tradeDir': 'qx', 'lotType': []},
    5: {'lotId': 5, 'lotName': '排列三', 'dbId': 'ps', 'tableId': 'ps', 'columnId': 'f',
        'tradeDir': 'ps', 'lotType': []},
    15: {'lotId': 15, 'lotName': '六场半全场', 'dbId': 'lzc', 'tableId': 'lzc', 'columnId': 'f',
        'tradeDir': 'lzc', 'lotType': []},
    17: {'lotId': 17, 'lotName': '四场进球', 'dbId': 'szc', 'tableId': 'szc', 'columnId': 'f',
        'tradeDir': 'szc', 'lotType': []},
    28: {'lotId': 28, 'lotName': '大乐透', 'dbId': 'lt', 'tableId': 'lt', 'columnId': 'l',
        'tradeDir': 'dlt', 'lotType': []},
    44: {'lotId': 44, 'lotName': '广西十一选五', 'dbId': 'dlc', 'tableId': 'dlc', 'columnId': 'f',
        'tradeDir': 'dlc', 'lotType': []},
    45: {'lotId': 45, 'lotName': '江西十一选五', 'dbId': 'dlc', 'tableId': 'dlc', 'columnId': 'f',
        'tradeDir': 'dlc', 'lotType': []},
    46: {'lotId': 46, 'lotName': '竞彩足球', 'dbId': 'jz', 'tableId': 'jz', 'columnId': 'f',
        'tradeDir': 'jczq', 'lotType': ['MULTIPRIZE', 'CHNLOTT']},
    47: {'lotId': 47, 'lotName': '竞彩篮球', 'dbId': 'jl', 'tableId': 'jl', 'columnId': 'f',
        'tradeDir': 'jclq', 'lotType': ['MULTIPRIZE', 'CHNLOTT']},
    60: {'lotId': 60, 'lotName': '排列五', 'dbId': 'plw', 'tableId': 'plw', 'columnId': 'f',
        'tradeDir': 'pw', 'lotType': []},
    61: {'lotId': 61, 'lotName': '任选九场', 'dbId': 'rj', 'tableId': 'rj', 'columnId': 'f',
        'tradeDir': 'rj', 'lotType': []}
}

def get(lotId):
    return __LOT_INFOS__.get(int(lotId))
