# ユーザー情報をCSVなどから読み込んで成功した後：

session["user_id"] = user["id"]

# ここが重要！ IDで親か子か判断して「親なら parent をセット」
if user["id"] == "KING1192":
    session["role"] = "parent"
elif user["id"].endswith("A") or user["id"].endswith("B") or user["id"].endswith("C"):
    session["role"] = "child"
else:
    session["role"] = "grandchild"
