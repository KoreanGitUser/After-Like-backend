import pickle
import numpy as np
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, and_
from fastapi import FastAPI, File
from typing import List
from starlette.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from db import session
from model import t_member, t_login,  t_image, t_like, t_like
import jwt
import time
from datetime import datetime
from 전처리 import 종교전처리, 차전처리, 결혼계획전처리, 음주전처리, 운동전처리, 흡연전처리, 지역전처리
from hangle import 지역, 성별,  혈액형, 음주, 흡연, 운동, 결혼유무, 결혼계획, 학력, 직업, 연봉
from hangle import 자산, 차량, 혈액형, 남자외모, 여자외모, 남자패션, 여자패션, 남자성격, 여자성격
import io
import uuid
import boto3
import base64
from sqlalchemy import select
import pymysql
from collections import ChainMap
import uvicorn
import json

# DB 접속코드 ---------------------
conn = pymysql.connect(host="project-db-stu.ddns.net", port=3307, user='inho',
                       password='k123456789', db='inho', charset='utf8')
cursor = conn.cursor(pymysql.cursors.DictCursor)
### 피클 자리##################################
man_xg부스트_1 = pickle.load(open("C:/PK/man_rf_clf.pkl", 'rb'))
man_랜덤포레_2 = pickle.load(open("C:/PK/man_tree.pkl", 'rb'))
man_결정트리_3 = pickle.load(open("C:/PK/tree_model_man.pkl", 'rb'))


woman_xg부스트_1 = pickle.load(open("C:/PK/tree_model_woman.pkl", 'rb'))
woman_랜덤포레_2 = pickle.load(open("C:/PK/woman_rf_clf.pkl", 'rb'))
woman_결정트리_3 = pickle.load(open("C:/PK/woman_tree.pkl", 'rb'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "21e7a7483f3348e9ae812e130882056a1d4aeb068e5cf6266e936635a0723601"
ALGORITHM = "HS256"

origins = [
    "http://localhost:3000",
    "localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------API 정의------------
mb_data1 = []


login = []
# ------------------------ 카카오 회원가입 !-----------------------------------------
@app.post("/login/easy-auth")
async def kakao_user(info: dict) -> dict:
    info["email"] = info["email"].replace('"', '', 2)
    print(info["email"])
    print(info["password"])
    user = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()  # 단일 사용자

    if user:
        print("아이디가 중복입니다.")

        return {"isLogin": True}

    else :
        mb = t_member()
        im = t_image()
        lg = t_login()
        # lg.mb_name = info["nickname"]
        lg.mb_email = info["email"]
        lg.mb_pw = info["password"]
    

        session.add(lg)
        session.commit()

        im.mb_no = lg.mb_no

        session.add(im)
        session.commit()

        mb.mb_no = lg.mb_no
        mb.mb_email = lg.mb_email
        session.add(mb)
        session.commit()


        print("아이디가 만들어졌습니다")
        return {"isReady": True}


    # 일반 이메일 회원가입 #############################
@app.post("/login/easy-auth/sign-up")
async def create_user(info: dict) -> dict:
    member = session.query(t_login.mb_no).filter().first()
    user = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()  # 단일 사용자

    if user:
        print("아이디가 중복입니다.")

        return {"repeat": False}

    else:

        login.append(info)
        mb = t_member()
        im = t_image()
        lg = t_login()
        # lg.mb_name = info["nickname"]
        lg.mb_email = info["email"]
        lg.mb_pw = info["password"]
        lg.mb_pw = pwd_context.hash(lg.mb_pw)

        session.add(lg)
        session.commit()

        im.mb_no = lg.mb_no

        session.add(im)
        session.commit()

        mb.mb_no = lg.mb_no
        mb.mb_email = lg.mb_email
        session.add(mb)
        session.commit()

        member = session.query(t_login).filter(
            t_login.mb_no == mb.mb_no).first()
        print("아이디가 만들어졌습니다")
        email = lg.mb_email
        return {"isReady": True, "repeat": True, "email": email}


# --------------------------- 로그인!!--------------------------------------------
@app.post("/login")
async def add_login(info: dict):  # 가입정보를 딕셔너리 형태로 받아옴
    mb_data1.append(info)

    password = info["password"]

    user = session.query(t_login).filter(
        t_login.mb_email == info["email"]).first()  # 단일 사용자
    if not user or not pwd_context.verify(password, user.mb_pw):
        print("비밀번호나 아이디가 틀렸습니다.")
        return {"isAuthenticated": False}
    else:
        print("로그인완료")
        return {"isAuthenticated": True, "email": info["email"]}



## 닉네임 중복 처리 기능.
@app.post("/user-data-input/doubleCheck")
async def create_member(info: dict) -> dict:

    user2 = session.query(t_member).filter(t_member.mb_nickname == info["nickname"]).first()
    print(user2)
    # 닉네임
    if user2:
        print("gg")
        return {"doubleCheck" : False}
    else :
        print("zz")
        return {"doubleCheck" : True}
    

# ------------------------상세정보 입력----------------------------------------------
@app.put("/user-data-input")
async def create_member(info: dict) -> dict:

    mb_data1.append(info)
    info["email"] = info["email"].replace('"', '', 2)
    user1 = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()
    user_no = user1.mb_no
    user2 = session.query(t_member).filter(
        (t_member.mb_no == user_no)).first()
    if user2:
        # 성별
        user2.mb_gender = info["gender"]
        # 생년
        user2.mb_birthdate = info["birth"][0:4]
        #닉네임
        user2.mb_nickname = info["nickname"]
        # 지역
        user2.mb_region = info["region"]
        # 지역상세
        user2.mb_region_more = info["detailRegion"]
        # 결혼유무
        user2.mb_marriage_yn = info["married"]
        # 결혼 계획
        user2.mb_marriage_plan = info["marriagePlan"]
        # 몸무게
        user2.mb_weight = info["weight"]
        # 키
        user2.mb_height = info["height"]
        # 음주여부
        user2.mb_drink_yn = info["alcohol"]
        # 흡연여부
        user2.mb_smoke_yn = info["smoke"]
        # 외모
        if info["gender"] == 'f':
            sty = list(info["womanAppearance"].values())
            style = sty[0]
            user2.mb_style = style
        else:
            sty = list(info["manAppearance"].values())
            style = sty[0]
            user2.mb_style = style
        # 성격
        if info["gender"] == 'f':
            cha = list(info["womanPersonality"].values())
            character = ','.join(i for i in cha)
            user2.mb_character = character
        else:
            cha = list(info["manPersonality"].values())
            character = ','.join(i for i in cha)
            user2.mb_character = character
        # 패션스타일
        if info["gender"] == 'f':
            fas = list(info["womanFashion"].values())
            fashion = ','.join(i for i in fas)
            user2.mb_fashion = fashion
        else:
            fas = list(info["manFashion"].values())
            fashion = ','.join(i for i in fas)
            user2.mb_fashion = fashion
        # 직업
        user2.mb_job = info["job"]
        # 직업 상세
        user2.mb_job_more = info["jobInfo"]
        # 종교
        user2.mb_religion = info["religion"]
        # 학력
        user2.mb_academic = info["education"]
        # 재산
        user2.mb_asset = info["asset"]
        # 연봉
        user2.mb_salary = info["salary"]
        # 차량
        user2.mb_car = info["vehicle"]
        # 혈액형
        user2.mb_bloodtype = info["blood"]
        # 운동
        user2.mb_health = info["health"]
        # 가입 시간
        user2.mb_joindate = time.localtime()
        # 업데이트 시간
        user2.mb_info_update = time.localtime()
        # 나이
        user2.mb_age = datetime.today().year - int(info["birth"][0:4]) + 1

        session.add(user2)
        session.commit()
        session.close()
        style = list(info["manAppearance"].values())
        return {"isCompleted": True}

    else:
        print("ㅋㅋ")



# --------------상호추천 알고리즘 적용, 추출 ---------------------------------------------
@app.post("/recommend")
async def create_member(info: dict) -> dict:
    mb_data = []
    info["email"] = info["email"].replace('"', '', 2)
    print(info["email"])
    user = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()
    user_no = user.mb_no
    f_user = session.query(t_member).filter(
        t_member.mb_no == user_no).first()
    user_nick = f_user.mb_nickname
   # 추천을 누른 회원의 데이터 정보 빼오기
    user성별 =f_user.mb_gender
    data1 = f_user.mb_no
    data2 = f_user.mb_birthdate[:4]
    data3 = f_user.mb_job
    data4 = f_user.mb_height
    data5 = f_user.mb_weight
    data6 = f_user.mb_style
    for i in range(7,62):
        globals()['data'+str(i)]="0"
    if (f_user.mb_region_more)=="r":       
            data7=1 #재혼
            data8=0 #초혼
    else : ###"w"면
            data7=0
            data8=1
    종교전처리jc = 종교전처리()
    #####종교전처리#################################################################
    if 종교전처리jc[f_user.mb_religion] in 종교전처리jc :
        globals()['data'+str(종교전처리jc[종교전처리jc[f_user.mb_religion]])]="1"

    #################차전처리###########################################################
    차전처리jc = 차전처리()    
    if 차전처리jc[f_user.mb_car] in 차전처리jc :
        globals()['data'+str(차전처리jc[차전처리jc[f_user.mb_car]])]="1"
    ##### 결혼계획 전처리#######################################################
    결혼계획전처리jc = 결혼계획전처리()  
    if 결혼계획전처리jc[f_user.mb_marriage_plan] in 결혼계획전처리jc :
        globals()['data'+str(결혼계획전처리jc[결혼계획전처리jc[f_user.mb_marriage_plan]])]="1"
    ##### 음주처리######################################################
    음주전처리jc = 음주전처리()
    if 음주전처리jc[f_user.mb_drink_yn] in 음주전처리jc :
        globals()['data'+str(음주전처리jc[음주전처리jc[f_user.mb_drink_yn]])]="1"
    ######운동전처리 ###############################################################
    운동전처리jc = 운동전처리()
    if 운동전처리jc[f_user.mb_health] in 운동전처리jc :
        globals()['data'+str(운동전처리jc[운동전처리jc[f_user.mb_health]])]="1"
    ####### 흡연전처리 #######################################################
    흡연전처리jc = 흡연전처리()
   
    if 흡연전처리jc[f_user.mb_smoke_yn] in 흡연전처리jc :
        globals()['data'+str(흡연전처리jc[흡연전처리jc[f_user.mb_smoke_yn]])]="1"
    ############## 지역전처리###############################################
    지역전처리jc = 지역전처리()
    if 지역전처리jc[f_user.mb_region] in 지역전처리jc :
        globals()['data'+str(지역전처리jc[지역전처리jc[f_user.mb_region]])]="1"

    arr = np.array([[data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,data12,data13,data14,data15,data16,data17,data18,data19,data20,data21,data22,data23,data24,data25,data26,data27,data28,data29,data30,data31,data32,data33,data34,data35,data36,data37,data38,data39,data40,data41,data42,data43,data44,data45,data46,data47,data48,data49,data50,data51,data52,data53,data54,data55,data56,data57,data58,data59,data60,data61]])
    print(arr)

    if user성별=="m":
        pred1 = man_xg부스트_1.predict(arr)
        pred2 = man_랜덤포레_2.predict(arr)
        pred3 = man_결정트리_3.predict(arr)


        pred1=pred1.astype(int)
        pred2=pred2.astype(int)
        pred3=pred3.astype(int)
        print(pred1)
        print(pred2)
        print(pred3)

        회원=[pred1[0],pred2[0],pred3[0]]    
    else :
        pred1 = woman_xg부스트_1.predict(arr)
        pred2 = woman_랜덤포레_2.predict(arr)
        pred3 = woman_결정트리_3.predict(arr)
        pred1=pred1.astype(int)
        pred2=pred2.astype(int)
        pred3=pred3.astype(int)
        print(pred1)
        print(pred2)
        print(pred3)

        회원=[pred1[0],pred2[0],pred3[0]]
    ai=[]
    for i in(회원):
        meosin = session.query(t_member).filter(t_member.mb_no == i).first()

        meosinimg = session.query(t_image).filter(t_image.mb_no == i).first()

        globals()["usernick"+str(i)] = meosin.mb_nickname
        globals()["userregion"+str(i)] = 지역()[meosin.mb_region]
        globals()["userjob "+str(i)] = 직업()[meosin.mb_job]
        globals()["serimage1"+str(i)] = meosinimg.mb_image1
        결과 = {'nickname': globals()["usernick"+str(i)] , 'region': globals()["userregion"+str(i)] , "job" : globals()["userjob "+str(i)] , "image" :globals()["serimage1"+str(i)]}
        ai.append(결과)

    print(ai)
    b= {'myName': user_nick}
    ai.append(b)
    session.close()

    return ai 
 # 머신러닝 준비중
# 여기는 나중에 코드 줄여야겠당


# -------------이미지 s3 저장 및 웹으로 보내기 -------------------------------'
@app.put("/user-data-input/user-image-input")
async def create_image(info: dict):

    for i in range(0, 6):
        globals()["img"+str(i)] = info["formData"][i]
        img = globals()["img"+str(i)]   # 이미지 6개 딕셔너리를
        if globals()["img"+str(i)] == f"{''}":
            pass
        else:
            image1 = bytes(img, 'utf-8')  # 바이트로 변환

    ###### 지우지마####

        # print(len(userImage))  # 길이 확인할려고~
            userImage2 = str(image1)  # 스트링으로 다시 바꿔야 인식함
            userimage = userImage2[24:]  # data:image/bmp;base64< 이거 없애야 디코딩됨

            imgdata = base64.b64decode(userimage)  # 디코딩 하자
        # image =Image.open(io.BytesIO(imgdata)) # 이미지 오픈

        # image.show()#이미지보기
            file = io.BytesIO(imgdata)  # 디코딩 이미지 파일로 만들기
            # if img == globals()["img"+str(i)]:
            # 파일에 이름줘야함 {}<<이거써서 이메일같은거 넣으면될듯
            img_list = list(info["imageName"].values())
            file.name = img_list[i]
            print(file.name)

    # url = uuid.uuid1().hex  # 유니크한 네임 줘야함
            url = file.name
            s3_client = boto3.client(  # aws 접속코드
                service_name="s3",
                region_name="ap-northeast-2",
                aws_access_key_id="AKIAW3XAAHKCN3ZSO6LT",
                aws_secret_access_key="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"
            )

            s3_client.upload_fileobj(  # aws업로드
                file,
                "notfound-404",  # 버킷이름
                url,  # 여기에 주소결정
                ExtraArgs={
                    "ContentType": "public-read"
                }
            )

            # timage = t_image()  # 이미지 주소 디비 저장
            # timage.mb_image1 = url
            # session.add(timage)
            # session.commit()
    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()
    user_no = user.mb_no
    i_user = session.query(t_image).filter(
        t_image.mb_no == user_no).first()
    print(img_list)
    # if i_user.mb_no == user_no:
    # globals()["i_user.mb_image"+str(i+1)] = url
    # print(globals()["i_user.mb_image"+str(i+1)])
    # print(i_user.mb_image1)
    # print(i_user.mb_image2)
    i_list = []
    # i_user.mb_image1 = img_list[0]
    # i_user.mb_image2 = img_list[1]
    # i_user.mb_image3 = img_list[2]
    # i_user.mb_image4 = img_list[3]
    # i_user.mb_image5 = img_list[4]
    # i_user.mb_image6 = img_list[5]
    for i in img_list :
        if i == '' :
            i = 'default'
            i_list.append(i)
        else :
            i_list.append(i)
    i_user.mb_image1 = i_list[0]
    i_user.mb_image2 = i_list[1]
    i_user.mb_image3 = i_list[2]
    i_user.mb_image4 = i_list[3]
    i_user.mb_image5 = i_list[4]
    i_user.mb_image6 = i_list[5]


    session.add(i_user)
    session.commit()
    session.close()

    del img_list[:]
    return {"isAuthenticated": True}


# -------------- 유저 정보 수정 및 회원탈퇴 ---------------------------
@app.delete("/user-setting")
async def delete_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    print(info["email"])

  #   회원테이블 유저 정보 삭제
    user1 = session.query(t_member).filter_by(mb_email=info["email"]).first()

    session.delete(user1)
    session.commit()
    session.close()
  # 이미지 테이블 유저 정보 삭제
    user = session.query(t_login).filter_by(mb_email=info["email"]).first()
    user.mb_no == t_image.mb_no
    user2 = session.query(t_image).filter_by(mb_no=user.mb_no).first()

    session.delete(user2)
    session.commit()
    session.close()
  # 로그인 테이블 유저 정보 삭제
    user = session.query(t_login).filter_by(mb_email=info["email"]).first()
    user.mb_no == t_image.mb_no

    user1 = session.query(t_image).filter_by(mb_no=user.mb_no).first()

    session.delete(user)
    session.commit()
    session.close()


# 회원 정보창에 프로필 정보 넘겨주기 ----------------------------------------------
@app.post("/user-setting")
async def post_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_member).filter_by(mb_email=info["email"]).first()
    # 닉네임
    nickname = user.mb_nickname
    # 성별
    gender = 성별()[user.mb_gender]
    # 지역
    region = 지역()[user.mb_region]
    # 직업
    job = 직업()[user.mb_job]
    # 외모
    style = user.mb_style.split(",")[0]
    if user.mb_gender == 'm':
        style = 남자외모()[user.mb_style]
    else:
        style = 여자외모()[user.mb_style]
    # 패션
    fashion = user.mb_fashion.split(",")
    fashionlist = []
    if user.mb_gender == "m":
        for i in fashion:
            a = 남자패션()[i]
            fashionlist.append(a)
    else:
        for i in fashion:
            a = 여자패션()[i]
            fashionlist.append(a)
    # 성격
    character = user.mb_character.split(",")
    characterlist = []
    if user.mb_gender == "m":
        for i in character:
            a = 남자성격()[i]
            characterlist.append(a)
    else:
        for i in character:
            a = 여자성격()[i]
            characterlist.append(a)
    # 자기소개
    profile = user.mb_profile
    # 이상형
    ideal = user.mb_ideal
    # 이미지
    user2 = user.mb_no
    u_image = session.query(t_image).filter(t_image.mb_no == user2).first()
    image1 = u_image.mb_image1
    session.close()
    return [{"nickname":nickname,"region": region,"job": job, "gender": gender, "style": style,
     "fashion": fashionlist, "character": characterlist,"introduce": profile, "wanted" : ideal, "image": image1}]



 # ---------------- 유저 정보 수정 및 정보 보여주는 창 ----------------------
@app.post("/user-setting/user-information-modify")
async def post_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_member).filter_by(mb_email=info["email"]).first()
    # 닉네임
    nickname = user.mb_nickname
    # 성별
    gender = 성별()[user.mb_gender]
    # 생일
    birth = user.mb_birthdate
    # 지역
    region = 지역()[user.mb_region]
    # 혈액형
    blood = 혈액형()[user.mb_bloodtype]
    # 운동
    health = 운동()[user.mb_health]
    # 음주
    drink = 음주()[user.mb_drink_yn]
    # 흡연
    smoke = 흡연()[user.mb_smoke_yn]
    # 결혼유무
    married = 결혼유무()[user.mb_marriage_yn]
    # 결혼계획
    married_plan = 결혼계획()[user.mb_marriage_plan]
    # 학력
    education = 학력()[user.mb_academic]
    # 직업
    job = 직업()[user.mb_job]
    # 직업상세
    job_more = user.mb_job_more
    # 연봉
    salary = 연봉()[user.mb_salary]
    # 자산
    asset = 자산()[user.mb_asset]
    # 차량
    car = 차량()[user.mb_car]
    # 자기소개
    profile = user.mb_profile
    # 이상형
    ideal = user.mb_ideal
    # 외모
    style = user.mb_style.split(",")[0]
    if user.mb_gender == 'm':
        style = 남자외모()[user.mb_style]
    else:
        style = 여자외모()[user.mb_style]
    # 패션
    fashion = user.mb_fashion.split(",")
    fashionlist = []
    if user.mb_gender == "m":
        for i in fashion:
            a = 남자패션()[i]
            fashionlist.append(a)
    else:
        for i in fashion:
            a = 여자패션()[i]
            fashionlist.append(a)
    # 성격
    character = user.mb_character.split(",")
    characterlist = []
    if user.mb_gender == "m":
        for i in character:
            a = 남자성격()[i]
            characterlist.append(a)
    else:
        for i in character:
            a = 여자성격()[i]
            characterlist.append(a)
    print(characterlist)
    # 이미지 테이블 이미지 불러오기
    user2 = user.mb_no
    u_image = session.query(t_image).filter(t_image.mb_no == user2).first()
    i1 = u_image.mb_image1
    i2 = u_image.mb_image2
    i3 = u_image.mb_image3
    i4 = u_image.mb_image4
    i5 = u_image.mb_image5
    i6 = u_image.mb_image6
    i_list = [i1,i2,i3,i4,i5,i6]
    img_list = []
    for i in i_list :
        if i == '' :
            i = 'default'
            img_list.append(i)
        else :
            img_list.append(i)
    image1 = img_list[0]
    image2 = img_list[1]
    image3 = img_list[2]
    image4 = img_list[3]
    image5 = img_list[4]
    image6 = img_list[5]
    print(i_list)
    print(img_list)
    session.close()
    return [{"nickname": nickname, "gender": gender, "birth": birth, "region": region,
            "blood": blood, "health": health, "drink": drink, "smoke": smoke, "married": married,
             "married_plan": married_plan, "education": education, "job": job, "salary": salary, "introduce": profile, "wanted" : ideal,
             "asset": asset, "car": car, "style": style, "fashion": fashionlist, "character": characterlist, "job_info": job_more,
             "image": {"image1": image1, "image2": image2, "image3": image3, "image4": image4,
                       "image5": image5, "image6": image6}}]



# 프론트에서 나의 이상형, 자기소개글 정보 받기
@app.put("/user-setting/user-information-modify")
async def put_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_member).filter_by(mb_email=info["email"]).first()
    if info["wanted"] == None :
        pass
    else :
        user = session.query(t_member).filter_by(mb_email=info["email"]).first()
        user.mb_ideal = info["wanted"]
        ideal = user.mb_ideal
    if info["introduce"] == None :
        pass
    else :
        user = session.query(t_member).filter_by(mb_email=info["email"]).first()
        user.mb_profile = info["introduce"]
        profile = user.mb_profile
    print(ideal, profile)
    
    session.add(user)
    session.commit()
    session.close()

    return "good"

################## 메인페이지 #################
m="m"
f="f"
# ############################ 랜덤데이터 쏴주기 ~@#######################################
@app.post("/home")#### 여성이면 남성데이터 쏴주고 남성이면 남성데이터 쏴주기 ###################################
async def create_user(info: dict) -> dict:
   
    info["email"] = info["email"].replace('"', '', 2)
    # print(info["email"])## 현유저 이메일
    user22 = session.query(t_login).filter(
        (t_login.mb_email == info["email"])).first()  # 단일 사용자
    userno=user22.mb_no 
    # print(userno) ## 현유저 넘버
    현사용자 = session.query(t_member).filter(
        (t_member.mb_no ==  userno)).first()  # 단일 사용자
  
    useragem10 = int(현사용자.mb_birthdate)-10
    useragep10 = int(현사용자.mb_birthdate)+10
    print(useragem10)
    print(useragep10)
    li = []
    a = 0
    for i in range(useragem10,useragep10):
        li.append(i)
    print(li)
    if 현사용자.mb_gender == 'm' :
        메인회원정보s = session.query(t_member).filter(t_member.mb_gender == 'f').order_by(t_member.mb_no.desc()).all()
        useragem10 < int(현사용자.mb_birthdate) < useragep10
        for i in 메인회원정보s:
            if int(i.mb_birthdate) :
                메인회원이미지 = session.query(t_image).filter(t_image.mb_no == i.mb_no).first()
                image = 메인회원이미지.mb_image1
                cha = i.mb_character.split(",")[0]
                character = 여자성격()[cha]
                globals()['user_'+str(a)]= {"nick":f"{i.mb_nickname}", "birth":datetime.today().year - int(i.mb_birthdate) + 1, "region": f"{지역()[i.mb_region]}", "style" : f"{여자외모()[i.mb_style]}", "character":f"{character}", "profile":f"{i.mb_profile}", "ideal": f"{i.mb_ideal}","image":[f"{image}"] }
                a = a + 1
            else :
                pass
            if a == 15 :
                break
    else :
        메인회원정보s = session.query(t_member).filter(and_(t_member.mb_gender == 'm', useragem10 < int(현사용자.mb_birthdate) < useragep10)).order_by(t_member.mb_no.desc()).all()
        # 정보 = sqlalchemy.sql.expression.desc(메인회원정보s.mb_no)
        # fashion = 메인회원정보s.mb_fashion.split(",")[0]
        # fashion = 남자외모()[메인회원정보s.mb_fashion]
        # 메인디비정보 = 메인회원정보s.mb_nickname
        for i in 메인회원정보s:
            메인회원이미지 = session.query(t_image).filter(t_image.mb_no == i.mb_no).first()
            image = 메인회원이미지.mb_image1
            cha = i.mb_character.split(",")[0]
            character = 남자성격()[cha]
            # li.append([f"{i.mb_nickname}",f"{datetime.today().year - int(i.mb_birthdate) + 1}", f"{지역()[i.mb_region]}",f"{여자외모()[i.mb_style]}",f"{character}", f"{i.mb_profile}", f"{i.mb_ideal}", f"{메인회원이미지.mb_image1}"])
            globals()['user_'+str(a)]= {"nick":f"{i.mb_nickname}", "birth":datetime.today().year - int(i.mb_birthdate) + 1, "region": f"{지역()[i.mb_region]}", "style" : f"{남자외모()[i.mb_style]}", "character":f"{character}", "profile":f"{i.mb_profile}", "ideal": f"{i.mb_ideal}","image":[f"{image}"] }
            a = a + 1
            if a == 15 :
                break
    session.close()
    return  user_0,user_1,user_2,user_3,user_4,user_5,user_6,user_7,user_8,user_9,user_10,user_11,user_12,user_13,user_14
   


# 메인페이지 좋아요 보내면 DB에 데이터 저장하기
@app.put("/home")
async def user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    현user = session.query(t_login).filter(t_login.mb_email == info["email"]).first()
    당한  =   session.query(t_member).filter(t_member.mb_nickname == info["username"]).first()
    print(type(현user.mb_no))
    print(type(현user.mb_no))
    현 = 현user.mb_no
    당 = 당한.mb_no
    abc = t_like()
    abc.like_mb_no= 현
    abc.like_user_no = 당
    abc.unlike = 'False'
    abc.like_time = time.localtime()
 
    session.add(abc)
    session.commit()
    session.close()



# 누구에게 좋아요 보냈는지 확인하는 페이지 
@app.post("/user-setting/likeYou")
async def like_user(info: dict):
    
    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_member).filter(t_member.mb_email == info["email"]).first()
    u_mb_no = user.mb_no
            
    
    you = t_member()
    
    
    # image = session.query(t_image).filter(t_image.like_mb_no == u_mb_no).first()
    datalist=[]
    img =session.query(t_like).filter(and_(t_like.like_mb_no == u_mb_no, t_like.unlike == 'False')).all()
    for img1 in img:
        # print(f"id: {img1.like_mb_no}  email: {img1.like_user_no}")
        datalist.append([f"{img1.like_user_no}"]) 
    print(datalist)
    

    a = []
    for i in range(len(datalist)) :
        user1 = session.query(t_member).filter(t_member.mb_no == datalist[i][0]).first()
        # u_mb_no1 = user1.mb_no
        image = session.query(t_image).filter(t_image.mb_no== datalist[i][0]).first()
        globals()['user'+str(i)]={"nickname":user1.mb_nickname, "job": 직업()[user1.mb_job], "region" : 지역()[user1.mb_region],
                                  "married": 결혼유무()[user1.mb_marriage_yn], "marriagePlan" : 결혼계획()[user1.mb_marriage_plan],
                                  "image": image.mb_image1}
        a.append(globals()['user'+str(i)])

    return  (a if a else None)



     ###### 좋아요 보낸거 지우는 기능 #################
@app.put("/user-setting/likeYou")
async def like_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    member = session.query(t_member).filter(t_member.mb_email == info["email"]).first()
    u_mb_no = member.mb_no
    user = session.query(t_member).filter(t_member.mb_nickname == info["username"]).first()
    like_no = user.mb_no    
    like = session.query(t_like).filter(and_(t_like.like_mb_no == u_mb_no ,t_like.like_user_no == like_no)).first()
    if like.unlike == 'False':
        like.unlike = "True"
        # if like.unlike == None :
        #     like.unlike = 'True'
        print(like.unlike)
        session.add(like)
        session.commit()
        session.close()
    

        

# 누구에게 좋아요 받았는지 확인하는 페이지
@app.post("/like")
async def like_user(info: dict):

    info["email"] = info["email"].replace('"', '', 2)
    user = session.query(t_member).filter(t_member.mb_email == info["email"]).first()
    u_mb_no = user.mb_no

    # image = session.query(t_image).filter(t_image.like_mb_no == u_mb_no).first()
    datalist=[]
    img =session.query(t_like).filter(t_like.like_user_no == u_mb_no).all()
    for img1 in img:
        # print(f"id: {img1.like_mb_no}  email: {img1.like_user_no}")
        datalist.append([f"{img1.like_mb_no}"]) 
    print(datalist)

    a = []
    for i in range(len(datalist)) :
        user1 = session.query(t_member).filter(t_member.mb_no == datalist[i][0]).first()
        # u_mb_no1 = user1.mb_no
        image = session.query(t_image).filter(t_image.mb_no== datalist[i][0]).first()
        globals()['user'+str(i)]={"nickname":user1.mb_nickname, "job": 직업()[user1.mb_job], "region" : 지역()[user1.mb_region],
                                  "married": 결혼유무()[user1.mb_marriage_yn], "marriagePlan" : 결혼계획()[user1.mb_marriage_plan],
                                  "image": image.mb_image1}
        a.append(globals()['user'+str(i)])    


    return  (a if a else None)



##### like 페이지에서 하트 보내기, 패스 기능
@app.put("/like")
async def like_user(info: dict):
    info["email"] = info["email"].replace('"', '', 2)
    현user = session.query(t_login).filter(t_login.mb_email == info["email"]).first()
    당한  =   session.query(t_member).filter(t_member.mb_nickname == info["username"]).first()
    현 = 현user.mb_no
    당 = 당한.mb_no 
 
    print(info["unlike"])
    #################################### 패스###################################################
    info["email"] = info["email"].replace('"', '', 2)
    member = session.query(t_member).filter(t_member.mb_email == info["email"]).first()
    u_mb_no = member.mb_no
    user = session.query(t_member).filter(t_member.mb_nickname == info["username"]).first()
    like_no = user.mb_no   
    like = session.query(t_like).filter(and_(t_like.like_user_no == like_no, t_like.like_mb_no==u_mb_no)).first()

    if info["unlike"] == True:
        like.unlike = "True"
        # if like.unlike == None :
        #     like.unlike = 'True'
        session.add(like)
        session.commit()
        session.close()
         
    elif info["like"]==True :
            abc=t_like()
            abc.unlike = "False"
            abc.like_mb_no = 현
            # print(당)
            abc.like_user_no = user.mb_no
            
            abc.like_time = time.localtime()
        
            session.add(abc)
            session.commit()
            session.close()
        
    return {"username" : info["username"]}

    







#     # if __name__ == '__main__':
#     #     uvicorn .run(app, host="0.0.0.0", port=8000)
#     #     pass
