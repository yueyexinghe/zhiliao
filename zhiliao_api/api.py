from flask import Blueprint, request, Response
import jwt
import db
import json
import datetime
import functools


api_blueprint = Blueprint("api", __name__, url_prefix="/api")

KEY = "asdasdasdasdasdasdasdasdasd"


def createToken(memberId):
    HEADERS = {
        "typ": "jwt",
        "alg": "HS256"
    }
    payload = {
        "memberId": memberId,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    result = jwt.encode(payload=payload, key=KEY, algorithm="HS256", headers=HEADERS)
    return result


def checkToken(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            token = request.cookies.get("token")
            payload = jwt.decode(token, KEY, algorithms=["HS256"])
        except Exception as e:
            return {"msg": "请先登录"}, 403
        return f(payload["memberId"], *args, **kwargs)
    return wrap


@api_blueprint.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    if db.register(username, password):
        return {"msg": "注册成功"}
    else:
        return {"msg": "注册失败: 用户已存在"}, 400


@api_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    userInfo = db.login(username, password)
    if userInfo:
        memberId, memberName = userInfo
        token = createToken(memberId)
        resp = Response(json.dumps({"data": {"memberId": memberId}, "msg": "登录成功"}))
        resp.set_cookie("token", token)
        return resp
    else:
        return {"msg": "用户名或密码错误"}, 403


@api_blueprint.route("/logout", methods=["POST"])
@checkToken
def logout(memberId):
    if memberId:
        return {"msg": "退出成功"}


@api_blueprint.route("/createbook", methods=["POST"])
@checkToken
def createBook(memberId):
    data = request.get_json()
    bookName = data.get("bookName", "")
    bookAuthor = data.get("bookAuthor", "")
    bookDescription = data.get("bookDescription", "")
    bookCover = data.get("bookCover", "")
    if not bookName:
        return {"msg": "书名不可为空"}, 400
    if not bookCover:
        return {"msg": "图片不可为空"}, 400
    if db.createBook(bookName, bookAuthor, bookDescription, bookCover):
        return {"msg": "新建图书成功"}
    else:
        return {"msg": "新建图书失败"}, 500


@api_blueprint.route("/getbooklist", methods=["POST"])
def getBookList():
    return {"data": db.getBookList()}


@api_blueprint.route("/creategood", methods=["POST"])
@checkToken
def createGood(memberId):
    data = request.get_json()
    bookId = data.get("bookId", "")
    goodValue = data.get("goodValue", "")
    goodDescription = data.get("goodDescription", "")
    goodPicture = data.get("goodPicture", "")
    if not goodPicture:
        return {"msg": "图片不可为空"}, 400
    if db.createGood(memberId, bookId, goodValue, goodDescription, goodPicture):
        return {"msg": "新建商品成功"}
    else:
        return {"msg": "新建商品失败"}, 500


@api_blueprint.route("/getgoodlist", methods=["POST"])
def getGoodList():
    data = request.get_json()
    bookId = data.get("bookId", 0)
    return {"data": db.getGoodList(bookId)}


@api_blueprint.route("/createorder", methods=["POST"])
@checkToken
def createOrder(memberId):
    data = request.get_json()
    goodId = data.get("goodId", "")
    address = data.get("address", "")
    if not address:
        return {"msg": "地址不可为空"}, 400
    if db.createOrder(memberId, goodId, address):
        return {"msg": "订单创建成功"}
    else:
        return {"msg": "订单创建失败"}, 500


@api_blueprint.route("/getmyorder", methods=["POST"])
@checkToken
def getMyOrder(memberId):
    return {"data": db.getMyOrder(memberId)}


@api_blueprint.route("/getuserlist", methods=["POST"])
@checkToken
def getUserList(memberId):
    return {"data": db.getUserList()}
