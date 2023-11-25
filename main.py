from flask import Flask, request, render_template, redirect, session
import pymongo
import base64
from bson.objectid import ObjectId 
from datetime import date
db_client = pymongo.MongoClient("mongodb://localhost:27017")
db = db_client["Greenaries"]

app = Flask(__name__)

app.secret_key = 'super secret key'

cart_list = []

@app.route('/upload_product', methods=['GET', "POST"])
def uploadProduct():
    is_post = False
    product_post = False
    if request.method == "POST":
        is_post = True
        form_data = request.form
        image = form_data["product_image"]
        title = form_data["product_name"]
        price = form_data["product_price"]
        category = form_data["product_category"]
        size = form_data["product_size"]
        newProduct = { "image_url": image , "title": title, "price": price, "category": category, "size": size}
        if len(image) > 0 and len(title) > 0 and int(price) > 0:
            db.product_list.insert_one(newProduct)
            product_post = True
    return render_template("uploadProduct.html", **locals())

@app.route('/upload_blog', methods=['GET', "POST"])
def uploadBlog():
    is_post = False
    blog_post = False
    if request.method == "POST":
        is_post = True
        form_data = request.form
        image = form_data["blog_image"]
        title = form_data["blog_title"]
        author = form_data["blog_author"]
        blog = form_data["blog"]
        today = date.today()
        today = str(today)
        print(today)
        newBlog = { "image_url": image , "title": title, "blog": blog, "author": author, "date": today}
        if len(image) > 0 and len(title) > 0:
            db.blog_list.insert_one(newBlog)
            blog_post = True
    return render_template("uploadBlogs.html", **locals())


@app.route('/products', methods=['GET', "POST"])
def products():
    allProducts = []
    showProducts = []
    for product in db.product_list.find():
        allProducts.append(product)
    if request.method == "POST":
        form_data = request.form
        if "search_btn" in form_data:
            query = form_data["search_btn"]
            for product in allProducts:
                if query.lower() in product["title"].lower() or query in product["category"].lower() or query in product["size"].lower():
                    showProducts.append(product)
    else:
        showProducts = allProducts
    return render_template("products.html", **locals())

@app.route('/blogs', methods=['GET', "POST"])
def blogs():
    allBlogs = []
    showBlogs = []
    for blog in db.blog_list.find():
        allBlogs.append(blog)
    if request.method == "POST":
        form_data = request.form
        query = form_data["search_btn"]
        for blog in allBlogs:
            if query.lower() in blog["title"].lower() or query in blog["author"].lower() or query in blog["blog"].lower():
                showBlogs.append(blog)
    else:
        showBlogs = allBlogs
    return render_template("blogs.html", **locals())


@app.route('/manage_products', methods=['GET', "POST"])
def manage_products():
    allProducts = []
    for product in db.product_list.find():
        allProducts.append(product)
    return render_template("manageProducts.html", **locals())


@app.route('/manage_blogs', methods=['GET', "POST"])
def manage_blogs():
    allBlogs= []
    for blog in db.blog_list.find():
        allBlogs.append(blog)
    return render_template("manageBlogs.html", **locals())


@app.route('/delete//product/<string:id>', methods=['GET', "POST"])
def delete_products(id):
    is_deleted = False
    required_product = db.product_list.find_one({"_id": ObjectId(id)}) 
    if required_product is not None:
        db.product_list.delete_one({"_id": ObjectId(id)}) 
        is_deleted = True
        return redirect("/manage_products")

@app.route('/delete//blog/<string:id>', methods=['GET', "POST"])
def delete_blogs(id):
    is_deleted = False
    required_blog = db.blog_list.find_one({"_id": ObjectId(id)}) 
    if required_blog is not None:
        db.blog_list.delete_one({"_id": ObjectId(id)}) 
        is_deleted = True
        return redirect("/manage_blogs")


@app.route('/edit/product/<string:id>', methods=['GET', "POST"])
def edit_products(id):
    is_post = False
    required_product = db.product_list.find_one({"_id": ObjectId(id)}) 
    prev_image_url = required_product["image_url"]
    prev_title = required_product["title"]
    prev_price = required_product["price"]
    prev_category = required_product["category"]
    prev_size = required_product["size"]
    if request.method == "POST":
        is_post = True
        form_data = request.form
        image = form_data["product_image"]
        title = form_data["product_name"]
        price = form_data["product_price"]
        category = form_data["product_category"]
        size = form_data["product_size"]
        updatedProduct = { "image_url": image , "title": title, "price": price, "category": category, "size": size}
        db.product_list.delete_one({"_id": ObjectId(id)}) 
        db.product_list.insert_one(updatedProduct) 
        return redirect("/manage_products")
    return render_template("editProduct.html", **locals())


@app.route('/product/details/<string:id>', methods=['GET', "POST"])
def detail_products(id):
    product = db.product_list.find_one({"_id": ObjectId(id)})
    return render_template("singleProduct.html", **locals())


@app.route('/blog/details/<string:id>', methods=['GET', "POST"])
def detail_blogs(id):
    blog = db.blog_list.find_one({"_id": ObjectId(id)})
    return render_template("singleBlog.html", **locals())


@app.route('/login', methods=['GET', "POST"])
def login():
    user = None
    if request.method == "POST" :
        form_data = dict(request.form)
        username = form_data["username"]
        password = form_data["pass"]
        check_user = db.users.find_one({"username": username})
        if check_user is None:
            return "caseA"
        else:
            user = db.users.find_one({"username": username, "password": password})

        if user is None:
            return "caseB"
        else:
            session["logged_in"] = True
            session["username"] = username
            return "caseC"
        
    return render_template("login.html", **locals())


@app.route('/register', methods=['GET', "POST"])
def register():
    if request.method == "POST" :
        form_data = dict(request.form)
        username = form_data["username"]
        password = form_data["pass"]
        password2 = form_data["pass2"]
        email = form_data["email"]
        userName = db.users.find_one({"username": username})
        userEmail = db.users.find_one({"email": email})
        newUser = {"username": username, "password": password, "email": email}
        validation = 0
        print(newUser)
        if userName is not None:
            validation = validation + 1
            return "caseA"
        if password != password2:
            validation = validation + 1
            return "caseB"
        if len(password) < 6:
            validation = validation + 1
            return "caseC"
        if userEmail is not None:
            validation = validation + 1
            return "caseD"
        
        if validation < 1:
            session["logged_in"] = True
            session["username"] = username
            db.users.insert_one(newUser)
            return "caseE"
            

    return render_template("register.html", **locals())

@app.route('/logout', methods=['GET', "POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route('/addDiscount', methods=['GET', "POST"])
def add_discount():
    is_post = False
    c_post = False
    if request.method == "POST":
        is_post = True
        form_data = request.form
        code = form_data["code"]
        amount = form_data["amount"]
        newCoupon = { "code": code , "amount": amount}
        if len(code) > 0 and len(amount) > 0:
            db.coupon_list.insert_one(newCoupon)
            c_post = True
    return render_template("addDiscount.html", **locals())


@app.route('/cart/<string:id>', methods=['GET', "POST"])
def add_cart(id):
    added = False
    if "logged_in" in session:
        product = db.product_list.find_one({"_id": ObjectId(id)})
        cart_list.append(product) 
        added = True
    else:
        return redirect("/login")
    
    return render_template("singleProduct.html", **locals())

@app.route('/cart', methods=['GET', "POST"])
def cart():
    promo_available = True
    discount_per = 0
    if request.method == "POST":
        form_data = request.form
        code = form_data["code"]
        coupon = db.coupon_list.find_one({"code": code})
        if coupon is not None:
            promo_available = True
            discount_per = coupon["amount"]    
            discount_per = float(discount_per)    
    print(discount_per)
    cart = cart_list
    cart_size = len(cart)
    subTotal = 0.0
    total = 0.0
    if "logged_in" in session:
        for prod in cart_list:
            subTotal = subTotal + int(prod["price"])
        if discount_per > 0:
            subTotal = subTotal - (subTotal * discount_per)
        total = subTotal + 200
        return render_template("cart.html", **locals())
    else:
        return redirect("/login")


 
@app.route('/remove/<string:id>', methods=['GET', "POST"])
def remove_cart(id):
    print(len(cart_list))
    for i in range(0, len(cart_list)):
         if cart_list[i]["_id"] == ObjectId(id):
            del cart_list[i]
            break
    return redirect("/cart")

@app.route('/', methods=['GET', "POST"])
def index():
    plants = []
    tools = []
    blogs = []
    for product in db.product_list.find():
        if product["category"] == "indoor" or product["category"] == "outdoor":
            plants.append(product)
        elif product["category"] == "tools":
            tools.append(product)
    for blog in db.blog_list.find():
            blogs.append(blog)           
    showProduct = plants[0:6]
    showTools = tools[0:6]
    showBlogs = blogs[0:4]
    return render_template("homePage.html", **locals())


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5007)
    #serve(app, host='127.0.0.1', port=5002)
    #serve(app, host='0.0.0.0', port=80)