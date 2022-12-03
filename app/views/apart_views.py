from flask import Blueprint, render_template, request
#from ..forms import ApartSearchForm
from ..models import BjdCode, AptDeal
import pandas as pd
import re

bp = Blueprint('apartment', __name__, url_prefix='/apartment')

@bp.route('/')
def input_keyword():
    return render_template('apart/apartment.html')

@bp.route('/search_code/')
def search_code():
    keyword = request.args.get("keyword")
    
    if 'admindata$' in keyword:
        command = (keyword.split())[1]
        #공공데이터포털 아파트 실거래가 데이터베이스 만들기
        if command == 'makepricedb':
            p = re.compile('20[1-2][0-9][0-1][0-9]')
            yearmonth = (keyword.split())[2]
            if p.match(yearmonth):
                makepricedb(yearmonth)
                return render_template('apart/apartment_DB.html', dbcode=1)
            else: return render_template('apart/apartment.html')
        #makebjddb 공공데이터포털 아파트의 법정동코드 데이터베이스 만들기
        elif command == 'makebjddb':
            makebjddb()
            return render_template('apart/apartment_DB.html', dbcode=2)
        #법정동 코드리스트 보기
        elif command == 'showbjdlist':
            sidoList, bjdCodeList = showbjdlist()
            return render_template('apart/apartment_DB.html', dbcode=3, sidoList=sidoList, bjdCodeList=bjdCodeList)
        #아파트 이름 교정하기
        elif command == 'namecorrection':
            namecorrection()
            return render_template('apart/apartment_DB.html', dbcode=4)
        else: return render_template('apart/apartment_DB.html')

    #아파트실거래가 검색하기
    else:
        if '이편한' in keyword:
            keyword = keyword.replace('이편한', '이편한세상')
        
        bjdList = checkBjdcode(keyword)
        print(bjdList)
        if len(bjdList) == 1:
            bjdong = bjdList[0]
            aptList = checkApartname(keyword, bjdong)
            print(aptList)
            if len(aptList) == 1:
                aptname = aptList[0]
                areaList = checkApartarea(bjdong, aptname)
                return render_template('apart/apartment_search_area.html', keyword=keyword, bjdong=bjdong, aptname=aptname, areaList=areaList)
            return render_template('apart/apartment_search_name.html', keyword=keyword, bjdong=bjdong, aptList=aptList)
        return render_template('apart/apartment_search_code.html', keyword=keyword, bjdList=bjdList)

@bp.route('/search_name/', methods=('GET', 'POST'))
def search_name():
    if request.method == 'POST':
        keyword = request.form["keyword"]
        bjdong = request.form["bjdong"]
        aptList = checkApartname(keyword, bjdong)
        if len(aptList) == 1:
            aptname = aptList[0]
            areaList = checkApartarea(bjdong, aptname)
            return render_template('apart/apartment_search_area.html', keyword=keyword, bjdong=bjdong, aptname=aptname, areaList=areaList)
        return render_template('apart/apartment_search_name.html', keyword=keyword, bjdong=bjdong, aptList=aptList)
    return render_template('apart/apartment.html')

@bp.route('/search_area/', methods=('GET', 'POST'))
def search_area():
    if request.method == 'POST':
        keyword = request.form["keyword"]
        bjdong = request.form["bjdong"]
        aptname = request.form["aptname"]
        areaList = checkApartarea(bjdong, aptname)
        return render_template('apart/apartment_search_area.html', keyword=keyword, bjdong=bjdong, aptname=aptname, areaList=areaList)
    return render_template('apart/apartment.html')

@bp.route('/search_result/', methods=('GET', 'POST'))
def search_result():
    if request.method == 'POST':
        keyword = request.form["keyword"]
        bjdong = request.form["bjdong"]
        aptname = request.form["aptname"]
        area = request.form["area"]
        buildyear, resultList = loadDealprice(bjdong, aptname, area)
        return render_template('apart/apartment_search_result.html', keyword=keyword, bjdong=bjdong, aptname=aptname, area=area, buildyear=buildyear, resultList=resultList)
    return render_template('apart/apartment.html')



#아파트 실거래가 불러오기--------------------------------------------------------------------------------------------------
def loadDealprice(bjdong, aptname, area):
    #법정동 코드번호 추출
    temp = bjdong.split()
    temp[1] = temp[1].replace('(', '')
    bjdcode = temp[1].replace(')', '')
    #데이터베이스를 데이터프레임으로 가져오기
    dealDB = AptDeal.query.filter_by(bjdcode=bjdcode, apartment=aptname)
    df = pd.read_sql_query(dealDB.statement, dealDB.session.connection())
    for n in range(len(df)):
        df.loc[n, 'area'] = int(float(df.loc[n, 'area']))#전용면적 소수점이하 버리기
    #찾고자하는 전용면적으로 분리하기
    resultdf = df[df['area'] == int(area)]
    resultdf.sort_values(by=['dealyear','dealmonth', 'dealday'])
    resultdf = resultdf.reset_index(drop=True)#index초기화
    #print(resultdf)
    resultList=[]
    buildyear = df.loc[0, 'buildyear']
    for o in range(len(resultdf)):
        resultList.append([o, resultdf.loc[o, 'dealyear'], resultdf.loc[o, 'dealmonth'], resultdf.loc[o, 'dealday'], resultdf.loc[o, 'floor'], resultdf.loc[o, 'price']])
    return buildyear, resultList

#전용면적 체크--------------------------------------------------------------------------------
def checkApartarea(bjdong, aptname):
    #법정동 코드번호 추출
    temp = bjdong.split()
    temp[1] = temp[1].replace('(', '')
    bjdcode = temp[1].replace(')', '')
    #데이터베이스를 데이터프레임으로 가져오기
    dealDB = AptDeal.query.filter_by(bjdcode=bjdcode, apartment=aptname)
    df = pd.read_sql_query(dealDB.statement, dealDB.session.connection())
    df['check'] = 0
    #전용면적 리스트 만들기
    areaList = []#전용면적 목록
    for m in range(len(df)):
        df.loc[m, 'area'] = int(float(df.loc[m, 'area']))#전용면적 소수점이하 버리기
        areaList.append(df.loc[m, 'area'])
    areaList = list(set(areaList))
    areaList.sort()
    return areaList

#아파트이름 체크--------------------------------------------------------------------------------
def checkApartname(keyword, bjdong):
    #법정동 코드번호 추출
    temp = bjdong.split()
    temp[1] = temp[1].replace('(', '')
    bjdcode = temp[1].replace(')', '')
    #데이터베이스를 데이터프레임으로 가져오기
    dealDB = AptDeal.query.filter_by(bjdcode=bjdcode)
    df = pd.read_sql_query(dealDB.statement, dealDB.session.connection())
    df['check'] = 0
    #찾고자하는 아파트명에서 두글자씩 추출해서 아파트리스트와 비교하여 두글자가 포함되면 'check'값을 1 올린다.
    for i in range(len(keyword)-1):
        a1 = keyword[i] + keyword[i+1]
        for j in range(len(df)):
            if a1 in (str(df.loc[j,'bjdong']) + str(df.loc[j,'apartment'])):
                df.loc[j,'check'] += 1
    
    aptList = []#'check'값이 가장 높은 가장높은 아파트를 뽑는다.
    for k in range(len(df)):
        if df.loc[k,'check'] == df['check'].max():
            aptList.append(df.loc[k,'apartment'])
    aptList = list(set(aptList))
    aptList.sort()
    return aptList

#법정동코드 찾기------------------------------------------------------------------------------------------------------------
def checkBjdcode(keyword):
    #데이터베이스를 데이터프레임으로 가져오기
    bjdDB = BjdCode.query.filter()
    df = pd.read_sql_query(bjdDB.statement, bjdDB.session.connection())
    df['check'] = 0
    #찾고자하는 아파트명에서 두글자씩 추출해서 아파트리스트와 비교하여 두글자가 포함되면 'check'값을 1 올린다.
    for i in range(len(keyword)-1):
        a1 = keyword[i] + keyword[i+1]
        for j in range(len(df)):
            if a1 in (str(df.loc[j,'gu']) + str(df.loc[j,'dong']) + str(df.loc[j,'apartment'])):
                df.loc[j,'check'] += 1
    
    bjdList = []
    #check 제일 큰 값이 2보다 작으며 결과없음으로 처리
    if df['check'].max() < 2:
        return bjdList
    #check값이 제일 큰 법정동 코드를 가져온다.
    for j in range(len(df)):
        if df.loc[j,'check'] == df['check'].max():
            bjdList.append(str(df.loc[j,'gu']) + ' ' + ' (' + str(df.loc[j,'bjdcode'])[0:5] + ')')
    bjdList = list(set(bjdList))
    bjdList.sort()
    return bjdList

#공공데이터포털 아파트 실거래가 데이터베이스 만들기-------------------------------------------------------
def makepricedb(period):
    import requests
    import xml.etree.ElementTree as ET
    import pandas as pd
    from .. import db

    serviceKey = 'XS%2FfcMwMTBUQfYl8hPGTIjWgVfnZ12m6jvjMJsJQKcBXdgE1pCJc2GgcH9YJsVUYr3pSxsJGS4LVTYN8VqiESA%3D%3D'
    pageNo = '1'
    numOfRows = '9999'

    #중복 데이터베이스 삭제
    trashlist = AptDeal.query.filter((AptDeal.dealyear == period[0:4]) & (AptDeal.dealmonth == period[4:6]))
    for trash in trashlist:
        db.session.delete(trash)
        db.session.commit()
        print(trash + "...삭제")
          
    aptbjd_list = BjdCode.query.all()
    bjdCodeList = []
    for aptbjd in aptbjd_list:
        bjdCodeList.append(str(aptbjd.bjdcode)[0:5])
    bjdCodeList = list(set(bjdCodeList))
    bjdCodeList.sort()
    
    for bjdCode in bjdCodeList:
        dealList = []
        #공공데이터포털에서 실거래가 데이터베이스 저장하기        
        print('데이터수집중......' + bjdCode + "..." + period)
        url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev?'
        payload = 'serviceKey=' + serviceKey + \
                '&pageNo=' + pageNo + \
                '&numOfRows=' + numOfRows + \
                '&LAWD_CD=' + bjdCode + \
                '&DEAL_YMD=' + period
        response = requests.get(url+payload)
        root = ET.fromstring(response.content)
        content = root.findall('body')
        for body in content:
            for items in body:
                for item in items:
                    itemList = {}
                    for elements in item:
                        if elements.tag == "거래금액" or elements.tag == "건축년도" or elements.tag == "년" or elements.tag == "아파트" or elements.tag == "법정동" or elements.tag == "아파트" or elements.tag == "월" or elements.tag == "일" or elements.tag == "전용면적" or elements.tag == "층":
                            #괄호문자 제거-test미확인
                            elements.text = elements.text.replace('(', '')
                            elements.text = elements.text.replace(')', '')
                            itemList[elements.tag] = elements.text.strip()
                    dealList.append(itemList)
        print(bjdCode+" 데이터 가져오기 완료")

        df = pd.DataFrame(data=dealList)
        #print(df)
        for i in range(len(df)):
            aptdeal = AptDeal(bjdcode=bjdCode, bjdong=df.loc[i,'법정동'], apartment=df.loc[i,'아파트'], buildyear=str(df.loc[i,'건축년도']), dealyear=str(df.loc[i,'년']), dealmonth=str(df.loc[i,'월']), dealday=str(df.loc[i,'일']), area=df.loc[i,'전용면적'], floor=str(df.loc[i,'층']), price=df.loc[i,'거래금액'])
            db.session.add(aptdeal)
            db.session.commit()
            #print(i)
        print(bjdCode+" 데이터베이스 저장완료")

    return

#makebjddb 공공데이터포털 아파트의 법정동코드 데이터베이스 만들기-------------------------------------------------------
def makebjddb():
    import requests
    import xml.etree.ElementTree as ET
    import pandas as pd
    from .. import db

    #공공데이터포털 Request Parameters
    serviceKey = 'XS%2FfcMwMTBUQfYl8hPGTIjWgVfnZ12m6jvjMJsJQKcBXdgE1pCJc2GgcH9YJsVUYr3pSxsJGS4LVTYN8VqiESA%3D%3D'
    pageNo = '1'
    numOfRows = '9999'
    apartList = []

    #서울(11)~제주(50)까지 아파트정보 가져오기
    for i in range(11,51):
        sidoCode = str(i)
        url = 'http://apis.data.go.kr/1613000/AptListService2/getSidoAptList'
        urlParams = '?serviceKey=' + serviceKey + '&sidoCode=' + sidoCode + '&pageNo=' + pageNo + '&numOfRows=' + numOfRows
        response = requests.get(url + urlParams)
        #print(response)

        #XML data parsing
        root = ET.fromstring(response.content)
        content = root.findall('body')
        for body in content:
            for items in body:
                for item in items:
                    itemList = {}
                    for elements in item:
                        itemList[elements.tag] = elements.text.strip()
                    apartList.append(itemList)

    #XML parsing data를 dataframe으로 변환 DB만들기
    df = pd.DataFrame(data=apartList)
    print(df)
    for i in range(len(df)):
        aptbjd = BjdCode(si=df.loc[i,'as1'], gu=df.loc[i,'as2'], dong=df.loc[i,'as3'], bjdcode=df.loc[i,'bjdCode'], apartment=df.loc[i,'kaptName'])
        db.session.add(aptbjd)
        db.session.commit()
        #print(i)

    return

#법정동 코드리스트 보기----------------------------------------------------------------------------------------
def showbjdlist():
    seoul = ['11', '서울']#25
    busan = ['26', '부산']#16
    daegu = ['27', '대구']#8
    incheon = ['28', '인천']#8
    gwangju = ['29', '광주']#5
    daegeon = ['30', '대전']#5
    ulsan = ['31', '울산']#5
    sejong = ['36', '세종']#1
    kyungki = ['41', '경기도']#42
    kangwon = ['42', '강원도']#18
    chungbuk = ['43', '충북']#14
    chungnam = ['44', '충남']#16
    junbuk = ['45', '전북']#15
    junnam = ['46', '전남']#20
    kyungbuk = ['47', '경북']#23
    kyungnam = ['48', '경남']#22
    jeju = ['50', '제주']#2
    sidoList = [seoul, busan, daegu, gwangju, daegeon, ulsan, sejong, kyungki, kangwon, chungbuk, chungnam, junbuk, junnam, kyungbuk, kyungnam, jeju, incheon]
    
    aptbjd_list = BjdCode.query.all()

    bjdCodeList = []
    for aptbjd in aptbjd_list:
        bjdCodeList.append(str(aptbjd.bjdcode)[0:5])
    bjdCodeList = list(set(bjdCodeList))
    bjdCodeList.sort()

    return sidoList, bjdCodeList

#데이터베이스의 아파트 이름 교정하기----------------------------------------------------------------
def namecorrection():
    from .. import db

    correctionbefore = ['e편한','e-편한','E-편한','LEADERS','Leaders','SoulLeader','TheFirst','Winnervill','We’vePark','FIRSTVIEW','VIEW','View','CASTLE', 'Castle','Sky 뷰','Palace','PALACE','HIPARK','I-PARK','I-Park','IPARK',"I'PARK",'HILLS','Hills','TOPCLASS','TOP-Class']
    correctionafter  = ['이편한','이편한','이편한', '리더스',   '리더스'   '소울리더',    '더퍼스트',  '위너스빌',     '위브파크',   '퍼스트뷰',   '뷰',   '뷰',   '캐슬',    '캐슬',   '스카이뷰','팰리스', '팰리스',  '하이파크','아이파크','아이파크','아이파크','아이파크','힐스',  '힐스',   '탑클래스',  '탑클래스']
    
    for i in range(len(correctionbefore)):
        correctionaptdeallist = AptDeal.query.filter(AptDeal.apartment.like('%'+correctionbefore[i]+'%')).all()
        for correctionaptdealitem in correctionaptdeallist:
            correctionaptdealitem.apartment = str(correctionaptdealitem.apartment).replace(correctionbefore[i], correctionafter[i])
            db.session.commit()
            print(correctionaptdealitem.apartment)
    print('아파트 실거래가 데이터베이스 아파트이름 수정완료')
    
    for i in range(len(correctionbefore)):
        correctionbjcodelist = BjdCode.query.filter(BjdCode.apartment.like('%'+correctionbefore[i]+'%')).all()
        for correctionbjdcodeitem in correctionbjcodelist:
            correctionbjdcodeitem.apartment = str(correctionbjdcodeitem.apartment).replace(correctionbefore[i], correctionafter[i])
            db.session.commit()
            print(correctionbjdcodeitem.apartment)
    print('법정동코드 데이터베이스 아파트이름 수정완료')
