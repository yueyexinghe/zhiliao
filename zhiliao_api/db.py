import sqlite3
import datetime
import random
import hashlib
import base64

from flask import current_app


# 初始化表
def init():
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        # 这里初始化和文档中表略有不同，增加冗余数据避免多表连接
        # 创建用户表Member
        dbc.execute('''
                    CREATE TABLE IF NOT EXISTS Member(
                        Member_Id INTEGER PRIMARY KEY,
                        Member_Name TEXT NOT NULL,
                        Member_Pass TEXT NOT NULL,
                        Member_Sex TEXT,
                        Member_Age INT,
                        Member_Register DATETIME,
                        Member_Status INT
                        );
                    ''')
        # 创建管理员表Admin
        dbc.execute('''
                    CREATE TABLE IF NOT EXISTS Admin(
                        Admin_Id INTEGER PRIMARY KEY,
                        Admin_Name TEXT NOT NULL,
                        Admin_Pass TEXT NOT NULL,
                        Admin_Sex TEXT,
                        Admin_Age INT,
                        Admin_Status INT
                        );
                    ''')
        # 创建图书信息表Book_Info
        dbc.execute('''
                    CREATE TABLE IF NOT EXISTS Book_Info(
                        Book_Id INTEGER PRIMARY KEY autoincrement,
                        Book_Name TEXT NOT NULL,
                        Book_Author TEXT,
                        Book_Description TEXT,
                        Book_Cover BLOB,
                        Book_Status INT
                        );
                    ''')
        # 创建图书商品表Book_Good
        # 这里的Member_ID是售卖人ID
        dbc.execute('''
                    CREATE TABLE IF NOT EXISTS Book_Good(
                        Good_Id INTEGER PRIMARY KEY autoincrement,
                        Book_Id INT NOT NULL,
                        Member_Id INT NOT NULL,
                        Good_Value TEXT,
                        Good_Description TEXT,
                        Good_Picture BLOB,
                        Buyer_Id INT,
                        Order_Date datetime,
                        Ship_Address TEXT,
                        Good_Status INT
                        );
                    ''')
    print("[DB] Init ok.")


# 用户注册
def register(username: str, password: str) -> bool:
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Member_Name FROM Member WHERE Member_Name=?", (username,))
        result = dbc.fetchone()

        if not result:
            current_app.logger.info(f"[DB] register: {username}")
            newID = random.randint(100000, 999999)
            dbc.execute(
                "INSERT OR REPLACE INTO Member VALUES (?, ?, ?, ?, ?, ?, ?)",
                (newID, username, hashlib.md5(password.encode()).hexdigest(), None, None, datetime.datetime.now(), 0)
            )
            current_app.logger.info(f"[DB] register: Generated memberID {newID}")
            return True
        return False


# 用户登录
def login(username: str, password: str) -> tuple[int, str]:
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute(
            "SELECT Member_Id, Member_Name FROM Member WHERE Member_Name=? AND Member_Pass=?",
            (username, hashlib.md5(password.encode()).hexdigest())
        )
        result = dbc.fetchone()

    if not result:
        current_app.logger.warning(f"[DB] login: Record not found {username}")
        return None
    current_app.logger.info(f"[DB] login: {username} -> {result[0]}")
    return result


# 用户列表
def getUserList():
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Member_Id, Member_Name, Member_Register, Member_Status FROM Member")
        result = dbc.fetchall()
    current_app.logger.info(f"[DB] getUserList: {len(result)} records")
    return [{
        "memberId": memberId,
        "memberName": memberName,
        "registerTime": registerTime,
        "memberStatus": memberStatus,
    }for memberId, memberName, registerTime, memberStatus in result]


# 新建图书
def createBook(bookName: str, bookAuthor: str, bookDescription: str, bookCover: str):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute(
            "INSERT INTO Book_Info VALUES (?, ?, ?, ?, ?, ?)",
            (None, bookName, bookAuthor, bookDescription, base64.b64decode(bookCover.encode()), 0)
        )

    current_app.logger.info(f"[DB] createBook: {bookName} OK")
    return True


# 获取图书列表
def getBookList():
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Book_Id, Book_Name, Book_Author, Book_Description, Book_Cover FROM Book_Info")
        result = dbc.fetchall()
    current_app.logger.info(f"[DB] getBookList: {len(result)} records")
    return [{
        "bookId": bookId,
        "bookName": bookName,
        "bookAuthor": bookAuthor,
        "bookDescription": bookDescription,
        "bookCover": base64.b64encode(bookCover).decode(),
    }for bookId, bookName, bookAuthor, bookDescription, bookCover in result]


def getMenberInfo(memberId: int):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Member_Name FROM Member WHERE Member_Id=?", (memberId,))
        result = dbc.fetchone()

    if result:
        return result[0]
    return None


def getBookInfo(bookId: int):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Book_Id, Book_Name, Book_Author, Book_Description, Book_Cover FROM Book_Info WHERE Book_Id=?", (bookId,))
        result = dbc.fetchone()

    if result:
        bookId, bookName, bookAuthor, bookDescription, bookCover = result
        return {
            "bookId": bookId,
            "bookName": bookName,
            "bookAuthor": bookAuthor,
            "bookDescription": bookDescription,
            "bookCover": base64.b64encode(bookCover).decode(),
        }
    return None


# 新建商品
def createGood(memberId: int, bookId: int, goodValue: str, goodDescription: str, goodPicture: str):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute(
            "INSERT INTO Book_Good VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (None, bookId, memberId, goodValue, goodDescription, base64.b64decode(goodPicture.encode()), None, None, None, 0)
        )

    current_app.logger.info(f"[DB] createGood: {memberId} {bookId} OK")
    return True


# 获取商品列表
def getGoodList(bookId: int):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        if bookId > 0: 
            dbc.execute("SELECT Good_Id, Member_Id, Good_Value, Good_Description, Good_Picture FROM Book_Good WHERE Book_Id=? AND Buyer_Id is NULL", (bookId,))
        else:
            dbc.execute("SELECT Good_Id, Member_Id, Good_Value, Good_Description, Good_Picture FROM Book_Good")
        result = dbc.fetchall()
    current_app.logger.info(f"[DB] getGoodList: {bookId} {len(result)} records")
    return [{
        "goodId": goodId,
        "memberName": getMenberInfo(memberId),
        "goodValue": goodValue,
        "goodDescription": goodDescription,
        "goodPicture": base64.b64encode(goodPicture).decode(),
    }for goodId, memberId, goodValue, goodDescription, goodPicture in result]


# 新建订单
def createOrder(memberId: int, goodId: int, address: str):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute(
            "UPDATE Book_Good SET Buyer_Id=?, Order_Date=?, Ship_Address=? WHERE Good_Id=?",
            (memberId, datetime.datetime.now(), address, goodId)
        )
    current_app.logger.info(f"[DB] createOrder: {memberId} {goodId} OK")
    return True


# 获取订单列表
def getMyOrder(memberId: int):
    with sqlite3.connect(DB_PATH) as db:
        dbc = db.cursor()
        dbc.execute("SELECT Good_Id, Member_Id, Good_Value, Good_Description, Good_Picture, Order_Date, Ship_Address FROM Book_Good WHERE Buyer_Id=?", (memberId,))
        result = dbc.fetchall()
    current_app.logger.info(f"[DB] getMyOrder: {memberId} {len(result)} records")
    return [{
        "goodId": goodId,
        "memberName": getMenberInfo(memberId),
        "goodValue": goodValue,
        "goodDescription": goodDescription,
        "goodPicture": base64.b64encode(goodPicture).decode(),
        "orderDate": orderDate,
        "address": address,
    }for goodId, memberId, goodValue, goodDescription, goodPicture, orderDate, address in result]


# # 用户ID查询用户个人信息（用户个人信息界面使用）
# def Select_Member_Message(Member_Id:int)->tuple[int,str,str,int,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             SELECT Member_Id,Member_Name,Member_Sex,Member_Age,Member_Register,Member_Status 
#             FROM Member 
#             WHERE Member_Id=?
#             ''',
#             (Member_Id)
#         )
#         result=dbc.fetchone()

#     if not result:
#         current_app.logger.warning(f"[DB] Select_Member_Message: Record not found Member_ID {Member_Id}")
#         return None
#     current_app.logger.info(f"[DB] Select_Member_Message: {Member_Id} -> {result[0]}")
#     return result

# #用户修改个人信息（用户个人信息界面使用）
# def Update_Member_Message(Member_Id:int,Member_Name:str,Member_Sex:str,Member_Age:int,Member_Register:str,Member_Status:int)->tuple[int,str,str,int,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             UPDATE Member
#             SET Member_Name=?,Member_Sex=?,Member_Age=?,Member_Register=?,Member_Status=?
#             WHERE Member_Id=?
#             ''',
#             (Member_Name,Member_Sex,Member_Age,Member_Register,Member_Status,Member_Id)
#         )
#         result=dbc.fetchone()
#     #这里只写了查询不到的情况，可能还有插入失败的情况
#     if not result:
#         current_app.logger.warning(f"[DB] Update_Member_Message: Record not found Member_ID{Member_Id}")
#         return None
#     current_app.logger.info(f"[DB] Update_Member_Message: {Member_Id} -> {result[0]}")
#     return result

# # 管理员ID查询个人信息（管理员个人信息界面使用）
# def Select_Admin_Message(Admin_Id:int)->tuple[int,str,str,int,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             SELECT Admin_Id,Admin_Name,Admin_Sex,Admin_Age,Admin_Status 
#             FROM Admin 
#             WHERE _Id=?
#             ''',
#             (Admin_Id)
#         )
#         result=dbc.fetchone()

#     if not result:
#         current_app.logger.warning(f"[DB] Select_Admin_Message: Record not found Admin_ID {Admin_Id}")
#         return None
#     current_app.logger.info(f"[DB] Select_Admin_Message: {Admin_Id} -> {result[0]}")
#     return result

# # 管理员信息修改（管理员个人界面使用）
# def Update_Member_Message(Admin_Id:int,Admin_Name:str,Admin_Sex:str,Admin_Age:int,Admin_Status:int)->tuple[int,str,str,int,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             UPDATE Admin
#             SET Admin_Name=?,Admin_Sex=?,Admin_Sex=?,Admin_Age=?,Admin_Status=?
#             WHERE Admin_Id=?
#             ''',
#             (Admin_Name,Admin_Sex,Admin_Age,Admin_Status,Admin_Id)
#         )
#         result=dbc.fetchone()
#     #这里只写了查询不到的情况，可能还有插入失败的情况
#     if not result:
#         current_app.logger.warning(f"[DB] Update_Admin_Message: Record not found Admin_ID{Admin_Id}")
#         return None
#     current_app.logger.info(f"[DB] Update_Admin_Message: {Admin_Id} -> {result[0]}")
#     return result

# # 图书信息查询
# def Select_Book_Info(Book_Id:int)->tuple[int,str,str,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             SELECT Book_Id,Book_Name,Book_Publish,Writer_Name,Book_Status 
#             FROM Book_Info 
#             WHERE Book_Id=?
#             ''',
#             (Book_Id)
#         )
#         result=dbc.fetchone()

#     if not result:
#         current_app.logger.warning(f"[DB] Select_Book_Info: Record not found Book_ID {Book_Id}")
#         return None
#     current_app.logger.info(f"[DB] Select_Book_Info: {Book_Id} -> {result[0]}")
#     return result

# # 图书信息修改
# def Update_Book_Info(Book_Id:int,Book_Name:str,Book_Publish:str,Writer_name:str,Book_Status:int)->tuple[int,str,str,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             UPDATE Book_Info
#             SET Book_Name=?,Book_Publish=?,Writer_name=?,Book_Status=?
#             WHERE Book_Id=?
#             ''',
#             (Book_Name,Book_Publish,Writer_name,Book_Status,Book_Id)
#         )
#         result=dbc.fetchone()
#     #这里只写了查询不到的情况，可能还有插入失败的情况
#     if not result:
#         current_app.logger.warning(f"[DB] Update_Book_Info: Record not found Book_ID{Book_Id}")
#         return None
#     current_app.logger.info(f"[DB] Update_Book_Info: {Book_Id} -> {result[0]}")
#     return result

# # 图书商品查询
# def Select_Book_Good(Good_Id:int)->tuple[int,int,str,int,str,float,int,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             SELECT Good_ID,Book_Id,Book_Name,Member_Id,Member_Name,Good_Value,Good_picture,Good_Status 
#             FROM Book_Good
#             WHERE Good_Id=?
#             ''',
#             (Good_Id)
#         )
#         result=dbc.fetchone()

#     if not result:
#         current_app.logger.warning(f"[DB] Select_Book_Good: Record not found Gook_ID {Good_Id}")
#         return None
#     current_app.logger.info(f"[DB] Select_Book_Good: {Good_Id} -> {result[0]}")
#     return result

# # 图书商品修改
# def Update_Book_Good(Good_Id:int,Book_Id:int,Book_Name:str,Member_Id:int,Member_name:str,Good_Value:float,Good_Picture:int,Good_Status:int)->tuple[int,int,str,int,str,float,int,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             UPDATE Book_Good
#             SET Book_Id=?,Book_Name=?,Member_Id=?,Member_name=?,Good_value=?,Good_Picture=?,Good_Status=?
#             WHERE Good_Id=?
#             ''',
#             (Book_Id,Book_Name,Member_Id,Member_name,Good_Value,Good_Picture,Good_Status,Good_Id)
#         )
#         result=dbc.fetchone()
#     #这里只写了查询不到的情况，可能还有插入失败的情况
#     if not result:
#         current_app.logger.warning(f"[DB] Update_Book_Good: Record not found Good_ID{Good_Id}")
#         return None
#     current_app.logger.info(f"[DB] Update_Book_Good: {Good_Id} -> {result[0]}")
#     return result

# # 订单表查询
# def Select_Order_Message(Order_Id:int)->tuple[int,int,str,float,int,str,str,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             SELECT Order_Id,Good_ID,Book_Name,Good_value,Member_Id,Member_Name,Ship_Adress,Order_Date,Order_Status
#             FROM Order
#             WHERE Order_Id=?
#             ''',
#             (Order_Id)
#         )
#         result=dbc.fetchone()

#     if not result:
#         current_app.logger.warning(f"[DB] Select_Order_Message: Record not found Order_ID {Order_Id}")
#         return None
#     current_app.logger.info(f"[DB] Select_Order_Message: {Order_Id} -> {result[0]}")
#     return result

# # 订单表修改
# def Update_Order_Message(Order_Id:int,Good_Id:int,Book_Name:str,Good_Value:float,Member_Id:int,Member_name:str,Ship_Adress:str,Order_Date:str,Order_Status:int)->tuple[int,int,str,float,int,str,str,str,int]:
#     with sqlite3.connect(DB_PATH) as db:
#         dbc=db.cursor()
#         dbc.execute(
#             '''
#             UPDATE Order
#             SET Good_Id=?,Book_Name=?,Good_Value=?,Member_Id=?,Member_name=?,Ship_Adress=?,Order_Date=?,Order_Status=?
#             WHERE Order_Id=?
#             ''',
#             (Good_Id,Book_Name,Good_Value,Member_Id,Member_name,Ship_Adress,Order_Status,Order_Id)
#         )
#         result=dbc.fetchone()
#     #这里只写了查询不到的情况，可能还有插入失败的情况
#     if not result:
#         current_app.logger.warning(f"[DB] Update_Order: Record not found Order_ID{Order_Id}")
#         return None
#     current_app.logger.info(f"[DB] Update_Order: {Order_Id} -> {result[0]}")
#     return result

DB_PATH = ".\\db.sqlite"
init()
