# coding: utf-8
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from db import Base
from db import ENGINE

# 유저 테이블
class t_member(Base):
    __tablename__ = 't_members'
    mb_no = Column(Integer, primary_key=True, autoincrement=True)
    mb_email = Column(String(45), ForeignKey(
        "t_logins.mb_email"), nullable=False)
    mb_nickname = Column(String(45), nullable=False)
    mb_gender = Column(String(45), nullable=False)
    mb_region = Column(String(45), nullable=False)
    mb_region_more = Column(String(45), nullable=False)
    mb_birthdate = Column(String(45), nullable=False)
    mb_marriage_yn = Column(String(45), nullable=False)
    mb_photo_yn = Column(String(45), nullable=False)
    mb_photo_cnt = Column(String(45), nullable=False)
    mb_profile = Column(String(500), nullable=False)
    mb_job = Column(String(45), nullable=False)
    mb_job_more = Column(String(100), nullable=False)
    mb_salary = Column(Integer, nullable=True)
    mb_height = Column(String(45), nullable=True)
    mb_weight = Column(String(45), nullable=True)
    mb_religion = Column(String(45), nullable=True)
    mb_car = Column(String(45), nullable=True)
    mb_academic = Column(String(45), nullable=True)
    mb_style = Column(String(45), nullable=True)
    mb_character = Column(String(45), nullable=True)
    mb_hobby = Column(String(45), nullable=True)
    mb_marriage_plan = Column(String(45), nullable=True)
    mb_fashion = Column(String(45), nullable=True)
    mb_asset = Column(String(30), nullable=True)
    mb_food = Column(String(60), nullable=True)
    mb_smoke_yn = Column(String(10), nullable=True)
    mb_drink_yn = Column(String(10), nullable=True)
    mb_health = Column(String(45), nullable=True)
    mb_joindate = Column(DateTime, nullable=True)
    mb_info_update = Column(DateTime, nullable=True)
    mb_age = Column(String(45), nullable=True)
    mb_ideal = Column(String(500), nullable=False)
    mb_bloodtype = Column(Integer, nullable=False)

    # login = relationship("t_login", back_populates="member", uselist=False)
    mail = relationship("t_login", back_populates="email")


# 유저 테이블 속성
class member(BaseModel):
    mb_no = int
    mb_email = str
    mb_nickname = str
    mb_gender = str
    mb_region = str
    mb_region_more = str
    mb_birthdate = str
    mb_marriage_yn = str
    mb_photo_yn = str
    mb_photo_cnt = str
    mb_profile = str
    mb_job = str
    mb_job_more = str
    mb_salary = Integer
    mb_height = str
    mb_weight = str
    mb_religion = str
    mb_car = str
    mb_academic = str
    mb_style = str
    mb_character = str
    mb_hobby = str
    mb_marriage_plan = str
    mb_fashion = str
    mb_asset = str
    mb_food = str
    mb_smoke = str
    mb_drink = str
    mb_health = str
    mb_joindate = str
    mb_info_update = str
    mb_age = str
    mb_ideal = str
    mb_bloodtype = int


# 로그인 테이블
class t_login(Base):
    __tablename__ = 't_logins'
    mb_no = Column(Integer, primary_key=True, autoincrement=True)
    mb_email = Column(String(45), nullable=False, unique=True)
    mb_pw = Column(String(300), nullable=False)

    # member = relationship("t_member", back_populates="login")
    email = relationship("t_member", back_populates="mail")

# 로그인 테이블 속성


class login(BaseModel):
    mb_no = int
    mb_email = str
    mb_pw = str

# 이미지 테이블 생성
class t_image(Base):
    __tablename__ = "t_image"
    img_no = Column(Integer, primary_key=True)
    mb_no = Column(Integer)
    mb_image1 = Column(String(1000), nullable=False)
    mb_image2 = Column(String(1000), nullable=False)
    mb_image3 = Column(String(1000), nullable=False)
    mb_image4 = Column(String(1000), nullable=False)
    mb_image5 = Column(String(1000), nullable=False)
    mb_image6 = Column(String(1000), nullable=False)

# 좋아요 테이블 생성.
class t_like(Base):
    __tablename__ = 't_userlike'
    like_no = Column(Integer, primary_key=True)
    like_mb_no = Column(Integer,nullable=False)
    like_user_no = Column(Integer,nullable=False)
    unlike = Column(String(10),nullable=False)
    like_time = Column(DateTime, nullable=False)

# 좋아요 테이블 속성
class like(BaseModel):
    like_no = int
    like_mb_no = int
    like_user_no = int
    unlike = str
    like_time = str




def main():
    # Table 없으면 생성
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
