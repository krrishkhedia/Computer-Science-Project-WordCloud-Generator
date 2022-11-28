#Import all required modules
import mysql.connector as sql
import pickle
from email_validator import validate_email, EmailNotValidError
from getpass import getpass
from os.path import exists
from os import remove,mkdir
from wordcloud import WordCloud, STOPWORDS
from shutil import copy2
from tkinter import *
from PIL import Image, ImageTk
from datetime import datetime
from prettytable import PrettyTable

#Initialize Database
def db_init():
    #Get database credentials freom user
    print("\n\nEnter The Database Details Below:")
    host = input("Hostname: ")
    user = input("Username: ")
    pwd = input("Password: ")
    db = input("Database Name: ")
    try:
        #Connnect to the given credentials
        conn = sql.connect(host = host, user = user, password = pwd, database = db)
        cur = conn.cursor()
        #Create table for users
        e = "CREATE TABLE USERS(UID INT(4) PRIMARY KEY, FIRST_NAME VARCHAR(15), LAST_NAME VARCHAR(15), EMAIL VARCHAR(40) NOT NULL UNIQUE, PASSWORD VARCHAR(30) NOT NULL, JOINED_AT DATETIME NOT NULL)"
        cur.execute(e)
        #Create table for storing wordclouds
        e = "CREATE TABLE WORDCLOUDS(WCID INT(4) PRIMARY KEY, WC_NAME VARCHAR(50) NOT NULL, WC_PATH VARCHAR(100) NOT NULL, WIDTH INT(4) NOT NULL, HEIGHT INT(4) NOT NULL, CREATION_TIME DATETIME NOT NULL, UID INT(4), FOREIGN KEY (UID) REFERENCES USERS(UID))"
        cur.execute(e)
        mkdir("output")
    except sql.Error as err:
        print("\nThe following error has occured with the given credentials:", err.msg)
        print("\nPlease Try Again!")
        db_init()
    else:
        print("\nDatabase Successfully Connected & Tables Created Successfully!")
        #Save the given credentials
        with open("config","wb") as file:
            db_config = {'hostname':host,'username':user,'password':pwd,'database':db}
            pickle.dump(db_config,file)
    finally:
        #Close database connection
        if conn.is_connected():
            cur.close()
            conn.close()

#Get the saved database credentials
def get_db_config():
    with open('config','rb') as file:
        db_config = pickle.load(file)
    return db_config

#Display the main menu
def main_menu():
    print("\n\nMain Menu:\n  1. Login\n  2. Signup\n  3. Exit")
    choice = int(input("Enter Your Choice(1,2,3): "))
    if choice == 1:
        login()
    elif choice == 2:
        signup()
    elif choice == 3:
        print("\nGoodBye!")
    else:
        print("\nYou entered a wrong number, please enter it correctly.")
        main_menu()

#Verify User Email
def verify_email(email):
    try:
        v = validate_email(email)
        email = v["email"]
        return True
    except EmailNotValidError as e:
        print("\n"+str(e))
        print("Please Try Again!")
        return False

#Validate Password
def validate_password(password):
    SpecialSym =['!','@','#','$','%','^','&','*','(',')','_','-','=','+','.',',','/','?','<','>',';',':','\'','"','[',']','\\','{','}','|','`','~']
    val = True
      
    if len(password) < 6:
        print('Password length should be at least 6')
        val = False
          
    if len(password) > 20:
        print('Password length should be not be greater than 20')
        val = False
          
    if not any(char.isdigit() for char in password):
        print('Password should have at least one numeral')
        val = False
          
    if not any(char.isupper() for char in password):
        print('Password should have at least one uppercase letter')
        val = False
          
    if not any(char.islower() for char in password):
        print('Password should have at least one lowercase letter')
        val = False
          
    if not any(char in SpecialSym for char in password):
        print('Password should have at least one special symbol')
        val = False
    
    return val

#Function for Login
def login():
    global user_id
    print("\nEnter your login details:")
    email = input("  Email Address: ")
    password = getpass("  Password (It will not be shown for security purpose): ")
    if verify_email(email):
        try:
            db_config = get_db_config()
            conn = sql.connect(host = db_config['hostname'], user = db_config['username'], password = db_config['password'], database = db_config['database'])
            cur = conn.cursor()
            e = "SELECT EMAIL FROM USERS WHERE EMAIL='"+email+"'"
            cur.execute(e)
            result = cur.fetchone()
            if not result == None:
                if result[0] == email:
                    e = "SELECT UID,EMAIL,PASSWORD FROM USERS WHERE EMAIL='"+email+"'"
                    cur.execute(e)
                    result = cur.fetchone()
                    if result[1] == email and result[2] == password:
                        print("\nUser Logged In Successfully!")
                        user_id = result[0]
                        sub_menu()
                    else:
                        print("\nThe email and password did not matched with the credentials in file. Please enter it correctly...")
                        login()
            else:
                print("\nUser does not exists, please signup or use another email address.")
                main_menu()
        except sql.Error as err:
            print("\nError:", err.msg)
            print("\nPlease Try Again!")
            main_menu()
        finally:
            if conn.is_connected():
                cur.close()
                conn.close()
    else:
        login()

#Function for SignUp
def signup():
    print("\nEnter the details of the user below:")
    fname = input("  First Name: ")
    lname = input("  Last Name: ")
    email = input("  Email Address: ")
    upassword = getpass("  Password (It will not be shown for security purpose): ")
    repeat_password = getpass("  Repeat Password: ")
    if verify_email(email):
        if upassword == repeat_password:
            val_pass = validate_password(upassword)
            if val_pass:
                try:
                    db_config = get_db_config()
                    conn = sql.connect(host = db_config['hostname'], user = db_config['username'], password = db_config['password'], database = db_config['database'])
                    cur = conn.cursor()
                    e = "SELECT EMAIL FROM USERS WHERE EMAIL='"+email+"'"
                    cur.execute(e)
                    result = cur.fetchone()
                    if not result:
                        e = "SELECT MAX(UID) FROM USERS"
                        cur.execute(e)
                        result = cur.fetchone()
                        if result[0] == None:
                            id = 1
                        else:
                            id = result[0]+1
                        #Creating a new user
                        e = "INSERT INTO USERS (UID,FIRST_NAME,LAST_NAME,EMAIL,PASSWORD,JOINED_AT) VALUES ("+str(id)+",'"+fname+"','"+lname+"','"+email+"','"+upassword+"',NOW())"
                        cur.execute(e)
                        conn.commit()
                    else:
                        print("User already exists, please login or use another email address.")
                        main_menu()
                except sql.Error as err:
                    print("\nError:", err.msg)
                    print("\nPlease Try Again!")
                    main_menu()
                else:
                    print("\nUser Account Successfully Created!")
                finally:
                    if conn.is_connected():
                        cur.close()
                        conn.close()
                    main_menu()
            else:
                signup()
        else:
            print("\nThe passwords didn't match...\nPlease Try Again!")
            signup()
    else:
        signup()

#Funtion to display the submenu
def sub_menu():
    print("\n\nWhat Do You Want To Do?\n  1. Create a new wordcloud\n  2. View previously created wordcloud\n  3. Export previously created wordcloud\n  4. Delete a previously created wordcloud\n  5. Logout")
    choice = int(input("Enter Your Choice(1,2,3,4,5): "))
    if choice == 1:
        create_wordcloud()
    elif choice == 2:
        view_wordcloud()
    elif choice == 3:
        export_wordcloud()
    elif choice == 4:
        del_wordcloud()
    elif choice == 5:
        print("\nUser logged out successfully!")
        main_menu()
    else:
        print("\nYou entered a wrong number, please enter it correctly.")
        sub_menu()

#Function to show the WordCloud image
def show_image(width, height, file_path, wordcloud_name):
    img_root = Tk()
    if width>1200:
        height = (1000*height)//width
        width = 1000
    img_root.geometry(str(int(width+30))+"x"+str(int(height+30)))
    img_root.title(wordcloud_name)
    img = Image.open(file_path)
    img_resized = img.resize((width,height))
    photo = ImageTk.PhotoImage(img_resized)
    img_label = Label(img_root,image=photo)
    img_label.place(relx=0.5,rely=0.5,anchor='center')
    img_root.mainloop()

#Function to create the WordCloud
def create_wordcloud():
    print("\nHow do you want to enter the text?\n  1. Pasting it here\n  2. From a text file (.txt)")
    choice = int(input("Enter Your Choice(1,2): "))
    if choice == 1:
        text = input("Enter your text (It must be in a single line): ")
    elif choice == 2:
        path_to_txt_file = input("Enter the path to the text file: ")
        path_to_txt_file = path_to_txt_file.replace("\"","").replace("\\","\\\\")
        if exists(path_to_txt_file):
            with open(path_to_txt_file, 'r') as file:
                text = file.read().replace("\n"," ")
        else:
            print("The file does not exists. \nPlease Try Again...")
            create_wordcloud()
    else:
        print("\nYou entered a wrong number, please enter it correctly.")
        create_wordcloud()
    
    stopwords = set(STOPWORDS)
    file_name = input("Enter The Name Of The WordCloud (Only for future reference): ")
    print("\nStyle the wordcloud with the available options:")
    width = int(input("  Width: "))
    height = int(input("  Height: "))
    bgcolor = input("  Background Color(Hex Value): ")
    margin = int(input("  Margin: "))
    min_font_size = int(input("  Minimum Font Size: "))
    creation_time = datetime.now()
    wordcloud_path = './output/IMG_'+creation_time.strftime("%Y%m%d_%H%M%S")+'.png'

    wordcloud = WordCloud(height=height, width=width, background_color=bgcolor, margin=margin, min_font_size=min_font_size).generate(text).to_file(wordcloud_path)
    show_image(width,height,wordcloud_path,file_name)
    
    choice = input("Do you want to export this wordcloud? ( YES | yes | Y | y     NO | no | N | n): ")
    #Save WordCloud in disk
    if choice in ["YES", "yes", "Y", "y"]:
        path_to_save = input("Enter the folder path to export the generated wordcloud: ")
        path_to_save = path_to_save.replace("\"","").replace("\\","\\\\")
        if ((not path_to_save.endswith("\\")) or (not path_to_save.endswith("/"))):
            if "\\" in path_to_save:
                path_to_save = path_to_save+"\\"
            elif "/" in path_to_save:
                path_to_save = path_to_save+"/"
        copy2(wordcloud_path, path_to_save+file_name+'.png')

    #Save WordCloud in database
    try:
        db_config = get_db_config()
        conn = sql.connect(host = db_config['hostname'], user = db_config['username'], password = db_config['password'], database = db_config['database'])
        cur = conn.cursor()
        e = "SELECT MAX(WCID) FROM WORDCLOUDS"
        cur.execute(e)
        result = cur.fetchone()
        if result[0] == None:
            id = 1
        else:
            id = result[0]+1
        e = "INSERT INTO WORDCLOUDS (WCID,WC_NAME,WC_PATH,WIDTH,HEIGHT,CREATION_TIME,UID) VALUES ("+str(id)+",'"+file_name+"','"+wordcloud_path+"',"+str(width)+","+str(height)+",'"+creation_time.strftime("%Y-%m-%d %H:%M:%S")+"',"+str(user_id)+")"
        cur.execute(e)
        conn.commit()
    except sql.Error as err:
        print("\nError:", err.msg)
        print("\nPlease Try Again!")
        sub_menu()
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
    
    sub_menu()

#Function to list the created wordcouds
def list_wordclouds():
    try:
        db_config = get_db_config()
        conn = sql.connect(host = db_config['hostname'], user = db_config['username'], password = db_config['password'], database = db_config['database'])
        cur = conn.cursor()
        e = "SELECT WCID,WC_NAME,WC_PATH,WIDTH,HEIGHT,CREATION_TIME FROM WORDCLOUDS WHERE UID="+str(user_id)
        cur.execute(e)
        result = cur.fetchall()
        if len(result)>0:
            table = PrettyTable(['S.No.','Name', 'Created At'])
            s_no = 1
            total = len(result)
            for row in result:
                row = list((s_no,row[1],row[5]))
                table.add_row(row)
                s_no += 1
            print("\nList of WordClouds created by you:")
            print(table)
        else:
            print("\nNo wordclouds created yet. Create one to see it here...")
            sub_menu()
    except sql.Error as err:
        print("\nError:", err.msg)
        print("\nPlease Try Again!")
        sub_menu()
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
    return total,result

#Function to view the selected WordCloud
def view_wordcloud():
    list = list_wordclouds()
    choice = int(input("\nEnter the S.No. of the wordcloud which you want to view: "))
    if choice<=list[0] and choice>0:
        #Show the requested WordCloud
        show_image(list[1][choice-1][3],list[1][choice-1][4],list[1][choice-1][2],list[1][choice-1][1])
        print("\nWordCloud with S.No. "+str(choice)+" viewed successfully!")
    else:
        print("\nPlease enter a valid S.No. Try Again...")
        view_wordcloud()
    sub_menu()

#Function to export the selected WordCloud
def export_wordcloud():
    list = list_wordclouds()
    choice = int(input("\nEnter the S.No. of the wordcloud which you want to export: "))
    #Export the requested WordCloud
    if choice<=list[0] and choice>0:
        path_to_save = input("\nEnter the folder path to export the generated wordcloud: ")
        path_to_save = path_to_save.replace("\"","").replace("\\","\\\\")
        if ((not path_to_save.endswith("\\")) or (not path_to_save.endswith("/"))):
            if "\\" in path_to_save:
                path_to_save = path_to_save+"\\"
            elif "/" in path_to_save:
                path_to_save = path_to_save+"/"
        copy2(list[1][choice-1][2], path_to_save+list[1][choice-1][1]+'.png')
        print("\nWordCloud exported successfully!")
    else:
        print("\nPlease enter a valid S.No. Try Again...")
        export_wordcloud()
    
    sub_menu()

#Function to delete the selected WordCloud
def del_wordcloud():
    list = list_wordclouds()
    choice = int(input("\nEnter the S.No. of the wordcloud which you want to delete: "))
    #Delete the requested WordCLoud
    if choice<=list[0] and choice>0:
        try:
            db_config = get_db_config()
            conn = sql.connect(host = db_config['hostname'], user = db_config['username'], password = db_config['password'], database = db_config['database'])
            cur = conn.cursor()
            e = "DELETE FROM WORDCLOUDS WHERE WCID="+str(list[1][choice-1][0])
            cur.execute(e)
            conn.commit()
            if exists(list[1][choice-1][2]):
                remove(list[1][choice-1][2])
        except sql.Error as err:
            print("\nError:", err.msg)
            print("\nPlease Try Again!")
            sub_menu()
        finally:
            if conn.is_connected():
                cur.close()
                conn.close()

        print("\nWordCloud with S.No. "+str(choice)+" deleted successfully!")
    else:
        print("\nPlease enter a valid S.No. Try Again...")
        del_wordcloud()

    sub_menu()