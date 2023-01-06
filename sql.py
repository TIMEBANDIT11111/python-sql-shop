import pyodbc
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from functools import partial

###LOGGING INTO SQL SERVER####
cnxn_str = ("Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-T1901FO;"
            "Database=MARKET;"
            "UID=Pytest2;"
            "PWD=Pytest2;"
            "trusted_connection=yes")
cnxn = pyodbc.connect(cnxn_str)
cursor = cnxn.cursor()
login = Tk()
login.geometry("240x100+900+300")

def panellogin():
    loginkey=False
    details=[]
    inputusername=username.get()
    inputpassword=password.get()
    cursor.execute("SELECT * FROM dbo.Logins")
    for row in cursor:
        details.append(row)
    for i in details:
        if i[1]==inputusername and i[2]==inputpassword:
            login.destroy()
            loginkey=True
            mainpanel(i[0])
            break
    if loginkey==False:
        messagebox.showinfo("login","Login Unsuccesful")

def register():
    registerkey=True
    details = []
    inputusername = username.get()
    inputpassword = password.get()
    if len(inputpassword)<3 or len(inputusername)<3:
        messagebox.showinfo("Register", "Username and Password should be at least 3 characters long")
        registerkey=False
    cursor.execute("SELECT * FROM dbo.Logins")
    for row in cursor:
        details.append(row)
    for i in details:
        if i[1]==inputusername and registerkey==True:
            messagebox.showinfo("Register","User Already Exists")
            registerkey=False
            break
    if registerkey==True:
        cursor.execute(f"INSERT INTO dbo.Logins (username,password,balance) VALUES ('{inputusername}','{inputpassword}','1000')")
        cnxn.commit()
        messagebox.showinfo("Register", "Register Succesful")

def refreshuserdetails(userid):
    userdetails=[]
    cursor.execute(f"SELECT * FROM dbo.Logins where ID='{userid}'")
    for row in cursor:
        userdetails.append(row)
    userid = userdetails[0][0]
    username = userdetails[0][1]
    balance=userdetails[0][3]
    return userid,username,balance

def logout():
    exit()

def refreshuserbal(panel,newbal):
    BalFrame = Frame(panel, width=180, height=30, bg='light grey')
    BalFrame.place(x=1120, y=2)

    BalanceLabel = Label(BalFrame, background='light grey', text=f"Balance: ${newbal}")
    BalanceLabel.config(font=("Arial", 14))
    BalanceLabel.place(x=0, y=0)

def buy(cartinfo,userid,products,cart,panel):
    sessionuserinfo=refreshuserdetails(userid)
    sessionsubtotal=0
    for item in products:
        for cartitem in cartinfo:
            if item[0]==cartitem[2]:
                sessionsubtotal+=item[3]
    if sessionuserinfo[2]>=sessionsubtotal and sessionsubtotal!=0:
        newbal=sessionuserinfo[2]-sessionsubtotal
        cursor.execute(f"UPDATE dbo.Logins SET balance='{newbal}' WHERE ID='{userid}'")
        for id in cartinfo:
            cursor.execute(f"DELETE FROM dbo.Cart where ID={id[0]}")
        cnxn.commit()
        cart.destroy()
        refreshuserbal(panel,newbal)
        messagebox.showinfo("Payment", "Payment Succesful")
    else:
        messagebox.showinfo("Payment", "Payment Unsuccesful")

def callback(slidervar,categvar,userdetails,panel,val):
    slidervar=slidervar.get()
    categvar=categvar.get()
    refreshproducts(slidervar,categvar,userdetails,panel)


def refreshcart(cartinfo,products,cart,userid,panel):
    subtotal=0
    # main frame
    main_cart_frame = Frame(cart, width=100, height=400)
    main_cart_frame.place(x=5, y=5)
    my_cart_canvas = Canvas(main_cart_frame, width=375, height=440, bg='light grey')
    my_cart_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    my_scrollbar = ttk.Scrollbar(main_cart_frame, orient=VERTICAL, command=my_cart_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)
    my_cart_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_cart_canvas.bind('<Configure>', lambda e: my_cart_canvas.configure(scrollregion=my_cart_canvas.bbox("all")))
    second_frame_cart = Frame(my_cart_canvas)
    my_cart_canvas.create_window((0, 0), window=second_frame_cart, anchor="nw")
    for product in range(len(cartinfo)):
        iteminfo=[]
        for item in products:
            if cartinfo[product][2]==item[0]:
                iteminfo.append(item)
                subtotal+=iteminfo[0][3]
        #creating frames for every item
        curframe_cart=Frame(second_frame_cart, bg='grey', width=360, height=150)
        curframe_cart.grid(pady=10, padx=10)
        #creating item name text
        productName=Label(curframe_cart,background='light grey', text = f"Name: {iteminfo[0][1]}")
        productName.config(font=("Arial", 12))
        productName.place(x=2, y=2)
        #creating item category text
        productCateg=Label(curframe_cart,background='light grey', text = f"Category: {iteminfo[0][2]}")
        productCateg.config(font=("Arial", 12))
        productCateg.place(x=2, y=32)
        #creating item price text
        productPrice=Label(curframe_cart,background='light grey', text = f"Price: ${iteminfo[0][3]}")
        productPrice.config(font=("Arial", 12))
        productPrice.place(x=2, y=120)
        #creating add to cart button
        removeCartbtn = ttk.Button(curframe_cart, text="Remove", command=partial(deletefromcart,cartinfo,userid,cart,products,product,panel))
        removeCartbtn.place(x=270, y=60)
    #total text
    total_text_frame = Frame(cart, width=200, height=40)
    total_text_frame.place(x=0, y=460)
    TotalCost = Label(total_text_frame,background='light grey' ,text = f"Total=${subtotal}")
    TotalCost.config(font =("Arial", 14))
    TotalCost.place(x=8,y=8)
    #payment button
    payment_button = ttk.Button(cart, text="BUY", command=partial(buy,cartinfo,userid,products,cart,panel))
    payment_button.place(x=310,y=470)

def refreshproducts(slidervar,categvar,userdetails,panel):
    # main frame
    currow=0
    currcolumn=0
    products=getproducts(slidervar,categvar)
    main_frame = Frame(panel, bg="grey", width=1270, height=500)
    main_frame.place(x=5, y=170)
    my_canvas = Canvas(main_frame, width=1250, height=500, bg='light grey')
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    second_frame = Frame(my_canvas)
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")
    # list products
    for product in range(len(products)):
        # creating frames for every item
        curframe = Frame(second_frame, bg='grey', width=200, height=200)
        curframe.grid(row=currow, column=currcolumn, pady=5, padx=5)
        # creating item name text
        productName = Label(curframe, background='light grey', text=f"Name: {products[product][1]}")
        productName.config(font=("Arial", 12))
        productName.place(x=2, y=2)
        # creating item category text
        productCateg = Label(curframe, background='light grey', text=f"Category: {products[product][2]}")
        productCateg.config(font=("Arial", 12))
        productCateg.place(x=2, y=32)
        # creating item price text
        productPrice = Label(curframe, background='light grey', text=f"Price: ${products[product][3]}")
        productPrice.config(font=("Arial", 12))
        productPrice.place(x=2, y=170)
        # creating add to cart button
        addCartbtn = ttk.Button(curframe, text="Add To Cart",command=partial(addtocart, userdetails[0], products[product]))
        addCartbtn.place(x=120, y=170)
        # aligning frames
        if currcolumn == 6:
            currcolumn = 0
            currow += 1
        else:
            currcolumn += 1

def getproducts(slidervar,categvar):
    if categvar=='All':
        categvar=''

    if type(slidervar)!=int:
        slidervar=0
    products = []
    cursor.execute(f"SELECT * FROM dbo.Products WHERE Category like '%{categvar}%' and  Price >= '{slidervar}' ")
    for row in cursor:
        products.append(row)
    return products

def addtocart(userid,product):
    cursor.execute(f"INSERT INTO dbo.Cart (UserID,ProductID) VALUES ('{userid}','{product[0]}')")
    cnxn.commit()
    messagebox.showinfo("Cart", "Item Added To Cart Succesfully!")

def getcartinfo(userid):
    cart = []
    cursor.execute(f"SELECT * FROM dbo.Cart where UserID='{userid}'")
    for row in cursor:
        cart.append(row)
    return cart

def deletefromcart(cartinfo,userid,cart,products,product,panel):
    cursor.execute(f"DELETE FROM dbo.Cart where ID='{cartinfo[product][0]}'")
    cnxn.commit()
    newcartinfo=getcartinfo(userid)
    refreshcart(newcartinfo,products,cart,userid,panel)
#//////////////////LOGIN-REGISTER BOX////////////////////#
#username
login.resizable(0,0)
login.title("Login")
username_label = ttk.Label(login, text="Username:")
username=StringVar(value='admin')
# username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
username_label.place(x=5,y=5)
username_entry = ttk.Entry(login,textvariable=username)
username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)
# password
password_label = ttk.Label(login, text="Password:")
password_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
password=StringVar(value='pass')
password_entry = ttk.Entry(login,textvariable=password,  show="*")
password_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
# login button
login_button = ttk.Button(login, text="Login",command=panellogin)
login_button.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
#register button
register_button = ttk.Button(login, text="Register",command=register)
register_button.grid(column=0, row=3, sticky=tk.E, padx=5, pady=5)
#///////////////////////////////////////////////#
#//////////////////MAIN PANEL///////////////////#
def mainpanel(userid):
    global slidervar
    global categvar
    userdetails=refreshuserdetails(userid)
    panel=Tk()
    panel.geometry("1280x720")
    panel.resizable(0,0)
    panel.title("Shop")
    #welcome text
    WelcomeLabel = Label(panel,background='light grey' ,text = f"Welcome {userdetails[1]}")
    WelcomeLabel.config(font =("Arial", 14))
    WelcomeLabel.place(x=2,y=2)
    #balance text
    BalFrame=Frame(panel,width=180,height=30,bg='light grey')
    BalFrame.place(x=1120,y=2)

    BalanceLabel = Label(BalFrame,background='light grey', text = f"Balance: ${userdetails[2]}")
    BalanceLabel.config(font =("Arial", 14))
    BalanceLabel.place(x=0,y=0)
    #cart button
    CartButton = ttk.Button(panel, text="Cart", command=partial(showcart,userdetails[0],panel))
    CartButton.place(x=1120,y=30)
    #logout button
    LogoutButton = ttk.Button(panel, text="Exit", command=partial(logout))
    LogoutButton.place(x=1200,y=30)
    #select categories
    slidervar=IntVar()
    categvar = StringVar()
    categvar.set("All")
    optmenu = tk.OptionMenu(panel,categvar,'All','Tech','Food','Wearable','Hobby','Kitchen',command=partial(callback,slidervar,categvar,userdetails,panel))
    optmenu.place(x=5,y=130)
    refreshproducts(slidervar,'All',userdetails,panel)
    #price slider
    SliderFrame=Frame(panel,width=400,height=80)
    SliderFrame.place(x=120, y=85)
    slider = Scale(master=SliderFrame,resolution=10,variable=slidervar, from_=0, to=600, length=250, orient=HORIZONTAL,command=partial(callback,slidervar,categvar,userdetails,panel))
    slider.place(x=55,y=30)
    SliderMin=Label(SliderFrame, text = f"Price >")
    SliderMin.place(x=5,y=30)
    #category text
    ctgrLabel = Label(panel ,text = f"Category")
    ctgrLabel.config(font =("Arial", 12))
    ctgrLabel.place(x=5,y=105)

#///////////////////////////////////////////////#
#//////////////////CART PANEL///////////////////#
def showcart(userid,panel):
    cart = Tk()
    cart.geometry("400x500+1100+190")
    cart.resizable(0, 0)
    cart.title("Shopping Cart")
    products = getproducts(0,'All')
    cartinfo=getcartinfo(userid)
    cart.grab_set()
    refreshcart(cartinfo,products,cart,userid,panel)
#///////////////////////////////////////////////#
mainloop()