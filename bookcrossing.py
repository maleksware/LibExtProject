# -*- coding: utf-8 -*-

#TODO: Remove Spaghetti Code


#TODO: Settings content
#TODO: Create camera
#TODO: Create testcases for testing
#TODO: Add ranks for users
#TODO: Send the db to a server
#TODO: Recreate MyBooks and Search structure
#TODO: Repaint arrows
#TODO: GiveAndTake options
#TODO: Recreate Login screen
#TODO: Interface Update
#TODO: Add the option of taking books right from the modal window

# Kivy imports

import kivy
from kivymd.app import MDApp
from kivy.config import Config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors import RectangularElevationBehavior, FocusBehavior
import pymysql
from re import *
import smtplib
# No imports after this line!

# System configs
Config.set("graphics", "resizable", "false")
Config.set("graphics", "width", 450)
Config.set("graphics", "height", 800)
kivy.require("1.11.1")
Window.size = (450,800)
# No system settings and configs after this line!

# Global variables with their comments
firstEnter = True
dataLoaded = False
ranking = {10: "Student", 50: "Librarian", 100: "Booklover", 200: "Top Reader", 500: "Writer"}
# No global vars after this line!

# Functions
def generateModalTextBook(book):
    owner = book[0]
    id = book[2]
    isbn = book[3]
    author = book[5]
    description = book[6]
    tags = showTags(book[7])
    station = book[8]
    text = []
    text.append("Author: " + author)
    text.append("ISBN: " + isbn)
    text.append("ID: " + id)
    text.append("Description: " + description)
    text.append("Tags: " + tags)
    if station != "The book was taken":
        text.append("Station: " + station)

    else:
        request = 'SELECT name, surname FROM users WHERE email = ' + cwq(owner)
        ownerText = execSQL(request)
        ownerText = " ".join(ownerText)
        text.append("Owner: " + ownerText)
    return "\n\n".join(text)

def cwq(string):
    return '"' + str(string) + '"'

def execSQL(sql, one= True, debugOutput= False):
    if debugOutput:
        print(sql)
    connection = pymysql.connect(host = "localhost",
                                 user = "root",
                                 password = "userpass1234",
                                 db = "bookcrossing",
                                 cursorclass=pymysql.cursors.Cursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if sql.upper().startswith("SELECT"):
                if one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        connection.commit()
    except Exception as e:
        print("AN EXCEPTION OCCURRED WHILE REQUESTING:")
        print(e)

    finally:
        connection.close()

def modalNews(id):
    request = 'SELECT * FROM info WHERE id = ' + id
    news = execSQL(request)
    bookModal = MDDialog(title= news[0], type= "custom", text= news[1], buttons= [MDFlatButton(text="OK")], size_hint= (0.7, None))
    bookModal.open()



def processLongTitle(text, processTo):
    if len(text) > processTo:
        return text[:processTo] + "..."
    else:
        return text

def hasThisBook(mail, book, reqType="book_id"):
    book = str(book)
    if reqType == "book_id":
        request = 'SELECT * FROM books WHERE book_id = ' + cwq(book)
    elif reqType == "isbn":
        request = 'SELECT * FROM books WHERE isbn = ' + cwq(book)
    else:
        raise CustomAppException("reqType not in ('book_id', 'isbn')")
    book = execSQL(request)
    if book[0] == mail:
        return True
    return False

def isID(text):
    try:
        text = str(text)
        request = 'SELECT * FROM books WHERE book_id = ' + cwq(text)
        result = execSQL(request)
        if result == None:
            return False
        else:
            return True
    except:
        return False

def isISBN(text):
    try:
        text = reduceISBN(text)
        if len(text) not in (10, 13):
            return False
        if isValid(text):
            return True
    except:
        return False

def reduceISBN(isbn):
    reducedISBN = isbn
    reducedISBN = "".join(reducedISBN.split("-"))
    return reducedISBN

def encodeTagsLine(tags):

    tags = tags.split()
    newTags = []
    for i in tags:

        i = i.lower()
        i = list(i)
        if "#" in i:
            i.remove("#")
        if "," in i:
            i.remove(",")
        newTags.append("".join(i))
    tags = list(newTags)
    return "^".join(tags)

def decodeTagsLine(tags):
    return tags.split("^")

def showTags(tags):
    tags = tags.split("^")
    toShow = []
    for tag in tags:
        tag = "#" + tag
        toShow.append(tag)
    return ", ".join(toShow)

def my_books():
    mail = App.get_running_app().email
    request = 'SELECT * FROM books WHERE owner = ' + cwq(mail)
    result = None
    try:
        result = execSQL(request, one=False)

    except pymysql.Error as err:
        App.get_running_app().show_popup("Database Error:" + str(err))

    return result

def modalview(b_id):
    request = 'SELECT * FROM books WHERE book_id = ' + cwq(str(b_id))
    result = None
    try:
        result = execSQL(request)
    except pymysql.Error as err:
        App.get_running_app().show_popup("Database Error:" + str(err))
    return result

def modal():
    book_id = App.get_running_app().current_book_id
    if book_id == "" or book_id == None:
        return
    book = modalview(book_id)
    if book == None:
        return None
    bookModal = MDDialog(title= book[4], type= "custom", text= generateModalTextBook(book), buttons= [MDFlatButton(text="OK")], size_hint= (0.7, None))
    bookModal.open()

def f_btn_book(self,a_id):
    App.get_running_app().current_book_id = a_id
    modal()

def bookSearch(request):
    bookList = execSQL('SELECT * FROM books', one = False)

    results = []
    request = request.lower()
    for book in bookList:
        put = str(book[0]).lower()
        read = str(book[1]).lower()
        book_id = str(book[2]).lower()
        isbn = reduceISBN(str(book[3])).lower()
        title = str(book[4]).lower()
        author = str(book[5]).lower()
        description = str(book[6]).lower()
        station = str(book[8]).lower()

        tags = tuple(decodeTagsLine(book[7]))

        if (request in title) or (request in isbn) or (request in author) or (request in station) or (request in tags) or (request in put) or (request in read) or (request in book_id) or (request in description):
            results.append(book)

    return results

def splitISBN(isbn):
    isbn = list(isbn.split("-"))
    isbn = list("".join(isbn).strip())
    return "".join(isbn)

def divideToCheck(isbn):
    return (isbn[:-1], isbn[-1])

def checkISBN(isbn, checkDigit):
    sum = 0
    ######################################
    if len(isbn) == 9:
        for i in range(10,1,-1):
            isbnNum = int(isbn[10-i])
            sum += isbnNum * i
        sum %= 11
        if checkDigit == "X":
            checkDigit = 10
        if (int(checkDigit)+sum) % 11 == 0:
            return True
        else:
            return False
    ######################################
    elif len(isbn) == 12:
        if checkDigit == "X":
            checkDigit = 10
        indexes = [1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3]
        for i in range(len(isbn)):
            sum += (int(isbn[i])*indexes[i])
        sum = sum % 10
        if (int(checkDigit) + sum) % 10 == 0:
            return True
        else:
            return False
    else:
        return False

def isValid(isbn):
    isbn = splitISBN(isbn)
    return checkISBN(divideToCheck(isbn)[0],checkDigit = divideToCheck(isbn)[1])

def isValidEmail(email):
    def isValidHost(host):
        if not "." in host:
            return False
        hostValidSymbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower() + "0123456789" + "-" + "."
        for i in host:
            if i not in hostValidSymbols:
                return False
        return True

    def isValidUser(user):
        if user.startswith('"') and user.endswith('"'):
            quoted = True
        else:
            quoted = False
        userValidSymbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower() + "0123456789" + "!#$%&'*+-/=?^_`{|}~"
        for i in user:
            if i not in userValidSymbols:
                return False
        if not quoted and ".." in user:
            return False
        if user.startswith(".") or user.endswith("."):
            return False

        if not quoted:
            for i in user:
                if i in '(),:;<>@[\]"':
                    return False
        return True






    try:
        email = email.split("@")
        user = email[0]
        host = email[1]
        if isValidUser(user) and isValidHost(host):
            return True

    except:
        return False
    return False

def upgradeRank(rank, count=1):
    rank = int(rank)
    rank += count
    return str(rank)

def getNameAndSurname(email):
    name, surname = tuple(execSQL("SELECT name, surname FROM users"))
    return name, surname
# No functions after this line!

# Classes of the screens
class Annot(Screen):
    def on_enter(self):
        Clock.schedule_once(self.load)
    def load(self, dt):
        global dataLoaded
        if dataLoaded == False:
            print("data loading...")
            print("going Loading...")
            dataLoaded = True
            self.manager.current = "Loading"
        else:
            self.manager.current = "Loading"

class Loading(Screen):
    def toLogin(self):
        App.get_running_app().screenStack = []
        print("toLogin")
        self.manager.current = "Login"

class Login(Screen):
    def clearEmail(self):
        App.get_running_app().email = None

    def stack(self):
        App.get_running_app().screenStack.append("Login")

    def checkToLoading(self):
        global firstEnter
        if firstEnter == True:
            firstEnter = False
            self.manager.current = "Loading"

    def switch(self, btn):
        App.get_running_app().email = self.mail.text
        request = 'SELECT * FROM users WHERE email = ' + cwq(self.mail.text)
        m_record = execSQL(request)
        if m_record == None:
            self.mail.text = ''
            App.get_running_app().show_popup('Email not found')
        else:
            if not self.mail.text:
                App.get_running_app().show_popup('Your email is not correct')
            else:
                self.defineRank()
                self.manager.current = 'MyBooks'

    def defineRank(self):
        user = execSQL('SELECT * FROM users WHERE email = ' + cwq(self.mail.text))
        App.get_running_app().rank = user[-1]
        print(user[-1])

class MyBooks(Screen):
    def stack(self):
        App.get_running_app().screenStack.append("MyBooks")

    def __init__(self, **kwargs):
        super(MyBooks, self).__init__(**kwargs)


    def my_book(self,btn):
        self.bookLayout.clear_widgets()
        self.bookLayout.bind(minimum_height=self.bookLayout.setter('height'))
        try:
            mail = App.get_running_app().email
            row_height = 30
            books = my_books()
            if books != ():
                k = 0

                for i in books:
                    k = k + 1
                    Btn = Button(background_color=[0.9, 0.9, 0.9, 1],
                                color=(0, 0, 0, 1),
                                text = "  " + str(k) + ") " + processLongTitle(str(i[5]), 20) + " : " + processLongTitle(str(i[4]), 20),
                                text_size = (self.width, 30),
                                halign="left",
                                background_normal="")

                    m_book_id = i[2]
                    Btn.bind(on_release= lambda x, m_book_id = m_book_id: f_btn_book(self, m_book_id))
                    self.bookLayout.add_widget(Btn)


            else:
                self.bookLayout.clear_widgets()
                self.bookLayout.add_widget(MDLabel(text = "You have no books, \nbut you have time to take them!", font_size = 20))

        except AttributeError:
              self.manager.current = 'Login'
              App.get_running_app().show_popup("You didn't sign up or sign in. Please do it")
        except Exception as e:
            print("AN EXCEPTION OCCURRED", e)

class GiveAndTake(Screen):
    def clearInput(self):
        self.code.text = ""
        self.isbn.text = ""

    def stack(self):
        App.get_running_app().screenStack.append("GiveAndTake")
    def give(self):
        book = self.isbn.text
        station = self.code.text
        try:
            if station == "":
                self.take()
                return

            isbn_ok = isValid(book)
            mail = App.get_running_app().email
            if isISBN(book):
                if isValid(book):
                    book = reduceISBN(book)
                    request = 'SELECT * FROM books WHERE isbn = ' + cwq(book)
                    result = execSQL(request)
                    if result == None:
                        App.get_running_app().show_popup("No such book found :(")
                        return
                    elif result[0] != mail:
                        App.get_running_app().show_popup("This book isn't yours! \nYou can log in or sign up in Settings")
                        return
                    else:
                        request = 'SELECT * FROM stations WHERE id = ' + cwq(station)
                        dataStation = execSQL(request, one = False)

                        if dataStation == ():
                            App.get_running_app().show_popup("Hmm,\nwe didn't find that station.")
                            self.code.text = ""
                            return
                        execSQL('UPDATE books SET owner = "None" WHERE isbn = ' + cwq(book))
                        execSQL('UPDATE books SET station = ' + cwq(station) + ' WHERE isbn = ' + cwq(book))
                        self.clearInput()

                        toast("Successfully!")
                        return
                else:
                    App.get_running_app().show_popup("This ISBN isn't correct")
                    return
            elif isID(book):
                try:
                    c_record = execSQL('SELECT * FROM books WHERE book_id = ' + cwq(book))
                    if c_record == None:
                        App.get_running_app().show_popup("No such book found :(")
                        return
                    elif c_record[0] != mail:
                        App.get_running_app().show_popup("This book isn't yours! \nYou can log in or sign up in Settings")
                        return
                    else:
                        dataStation = execSQL('SELECT * FROM stations WHERE id = ' + cwq(station), one=False)

                        if dataStation == ():
                            App.get_running_app().show_popup("Hmm,\nwe didn't find that station.")
                            self.code.text = ""
                            return
                        execSQL('UPDATE books SET owner = "None" WHERE book_id = ' + cwq(str(book)))
                        execSQL('UPDATE books SET station = ' + cwq(station) + ' WHERE book_id = ' + cwq(book))
                        self.clearInput()
                        toast("Successfully!")
                        return
                except:
                    App.get_running_app().show_popup("Your ID isn't correct")
                    return
            else:
                App.get_running_app().show_popup("The ID or ISBN isn't correct.")
                return


        except AttributeError:
             self.manager.current = 'Login'
             App.get_running_app().show_popup("You didn't sign up or sign in. Please do it")
             return
        except IndexError:
             App.get_running_app().show_popup("You didn't write something.")
             return
        except UnboundLocalError:
            return


    def take(self):
        book = self.isbn.text
        if book == "":
            toast("You didn't write something")
        try:
            if isISBN(book):
                if isValid(book):
                    mail = App.get_running_app().email
                    result = execSQL('SELECT * FROM books WHERE isbn = ' + cwq(book))
                    if result == None:
                        App.get_running_app().show_popup("This book doesn't exist")
                    else:
                        try:
                            if result[0] == "None":
                                execSQL('UPDATE books SET owner = ' + cwq(mail) +' WHERE isbn = ' + cwq(str(book)))
                                execSQL('UPDATE books SET station = "The book was taken" WHERE isbn = ' + cwq(str(book)))
                                self.clearInput()
                                toast("Successfully!")
                                return
                            elif not hasThisBook(mail, book, reqType="isbn"):
                                App.get_running_app().show_popup("This book isn't yours! \nYou can log in or sign up in settings.")
                                return
                            else:
                                App.get_running_app().show_popup("You already have this book!")
                        except pymysql.Error as err:
                            App.get_running_app().show_popup("Database Error")
                            print(err)

                else:
                    App.get_running_app().show_popup("The ISBN isn't correct")
                    return
            elif isID(book):
                mail = App.get_running_app().email
                result = execSQL('SELECT * FROM books WHERE book_id = ' + cwq(str(book)))
                if result == None:
                    App.get_running_app().show_popup("This book doesn't exist")
                else:
                    try:
                        if result[0] == "None":

                            execSQL('UPDATE books SET owner = ' + cwq(mail) + ' WHERE book_id = ' + cwq(book))
                            execSQL('UPDATE books SET station = "The book was taken" WHERE book_id = ' + cwq(str(book)))
                            self.isbn.text = ''
                            toast("Successfully!")
                            return
                        elif not hasThisBook(mail, book, reqType="book_id"):
                            App.get_running_app().show_popup("This book isn't yours! \nYou can log in or sign up in settings.")
                        else:
                            App.get_running_app().show_popup("You already have this book!")
                    except pymysql.Error as err:
                        App.get_running_app().show_popup("Database Error")
                        print(err)


            else:
                App.get_running_app().show_popup("The ID or ISBN isn't correct")
        except AttributeError:
            self.manager.current = 'Login'
            App.get_running_app().show_popup("You didn't sign up or sign in. Please do it")
        except IndexError:
            App.get_running_app().show_popup("You didn't write all.")
        except UnboundLocalError:
            return

class Add(Screen):
    def clearInput(self):
        self.isbn.text = ''
        self.kod.text = ''
        self.title.text = ''
        self.author.text = ''
        self.description.text = ''
        self.tags.text = ''
    def stack(self):
        App.get_running_app().screenStack.append("Add")
    def addBook(self, g):

        try:
            isbn_ok = isValid(self.isbn.text)
            mail = App.get_running_app().email
            s_data = execSQL('SELECT * FROM stations WHERE id = ' + cwq(self.kod.text))


            if not (self.isbn.text) or not (self.title.text) or not (
                   self.author.text) or not self.description.text or not self.tags.text or not self.kod.text:
                    App.get_running_app().show_popup("You didn't write something.")
            elif isbn_ok == False:
                    self.isbn.text = ''
                    App.get_running_app().show_popup("Your isbn isn't correct")
            elif s_data == []:
                App.get_running_app().show_popup("Hmm,\nwe didn't find this station")
                self.kod.text = ''
                return
            else:
                try:
                    table = execSQL('SELECT * from books WHERE isbn = ' + cwq(self.isbn.text), one=False)
                    tags = encodeTagsLine(self.tags.text)
                    if table == ():
                        tableLength = len(execSQL('SELECT * FROM books', one= False))
                        reducedISBN = reduceISBN(self.isbn.text)
                        execSQL('INSERT INTO books (put_by, owner, book_id, isbn, title, author, description, tags, station) VALUES (' + cwq(mail) + ', ' + cwq("None") + ', ' + cwq(tableLength + 1) + ', ' + cwq(reducedISBN) + ', ' + cwq(self.title.text) + ', ' + cwq(self.author.text) + ', ' + cwq(self.description.text) + ', ' + cwq(tags) + ', ' + cwq(self.kod.text) + ') ')

                        toast("Successfully!")
                        return
                    else:
                        App.get_running_app().show_popup("This book already exists")

                except pymysql.Error as err:
                    App.get_running_app().show_popup("Database Error")
                    print(err)
                else:
                    self.clearInput()
        except AttributeError as Error:
            print(Error)
            self.clearInput()
            self.manager.current = 'Login'
            App.get_running_app().show_popup("You didn't sign up or sign in. Please do it")
        except IndexError:
            App.get_running_app().show_popup("You didn't write all.")

class Ok(Screen):
    def stack(self):
        App.get_running_app().screenStack.append("Ok")
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

class Search(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        App.get_running_app().screenStack.append("Search")

    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)

    def search(self):
        try:
            self.bookLayout.bind(minimum_height=self.bookLayout.setter('height'))
            self.bookLayout.clear_widgets()
            mail = App.get_running_app().email
            row_height = 30
            books = bookSearch(self.searchTextInput.text)
            if books != []:

                self.bookLayout.add_widget(Label(text='Books:', text_size= (self.width, row_height),font_size = 20, halign = 'left'))
                k = 0
                for i in books:
                    k += 1
                    Btn = Button(background_color=[0.9, 0.9, 0.9, 1],
                                color=(0, 0, 0, 1),
                                background_normal="",
                                text= "  " + str(k) + ") " + processLongTitle(str(i[5]), 20) + " : " + processLongTitle(str(i[4]), 20),
                                text_size = (self.width,row_height),
                                halign = 'left',font_size = 17,
                                )
                    m_book_id = i[2]
                    Btn.bind(on_release= lambda x, m_book_id = m_book_id : f_btn_book(self, m_book_id))
                    self.bookLayout.add_widget(Btn)
                self.bookLayout.add_widget(Widget())
            else:
                self.bookLayout.clear_widgets()
                self.bookLayout.add_widget(Label(text="Nothing was found"))

        except UnboundLocalError:
            return

class Set(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        App.get_running_app().screenStack.append("Set")

class SignUp(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        App.get_running_app().screenStack.append("SignUp")
    def click(self, btn):
        App.get_running_app().email = self.mail.text
        pattern = compile( '(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)' )
        is_valid = pattern.match( self.mail.text )
        m_record = execSQL('SELECT * FROM users WHERE email = ' + cwq(self.mail.text))
        if m_record == None:
            if not (self.familia.text) or not (self.nam.text) or not (self.mail.text) or not self.class1.text:
                App.get_running_app().show_popup( "You didn't write all." )
            elif not is_valid:
                self.mail.text = ''
                App.get_running_app().show_popup( "Your email isn't correct" )
            elif self.class1.text in ["5", "6", "7", "8", "9", "10", "11"]:
                try:
                    execSQL('INSERT INTO users (name, surname, class, email, rank) VALUES (' + cwq(self.nam.text) + ', ' + cwq(self.familia.text) + ', ' + cwq(self.class1.text) + ', ' + cwq(self.mail.text) + ', ' + cwq("0") + ')')
                except pymysql.Error as err:
                    App.get_running_app().show_popup( "Database Error" )
                    print(err)
                else:
                    self.manager.current = 'MyBooks'
                    App.get_running_app().show_popup('Hello ' + self.nam.text)
            else:
                self.class1.text = ''
                App.get_running_app().show_popup( "Write the number of your class." )
        else:
            self.mail.text = ''
            App.get_running_app().show_popup( "This user already exists." )

class Profile(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        if App.get_running_app().screenStack[-1] != "Profile":
            App.get_running_app().screenStack.append("Profile")
    def editProfile(self):
        self.manager.current = "UpdateProfile"
    def deleteProfile(self):
        self.manager.current = "DeleteProfile"
    def logout(self):
        App.get_running_app().email = None
        self.manager.current = "Login"
    def getRank(self):
        return "levo"
    def initProfile(self):
        pair = getNameAndSurname(App.get_running_app().email)
        self.nameLabel.text = pair[0]
        self.surnameLabel.text = pair[1]

class UpdateProfile(Screen):
    def prepareInputs(self):
        user = App.get_running_app().email
        self.mail.text = user
        result = execSQL('SELECT * FROM users WHERE email = ' + cwq(user))

        self.nam.text = result[0]
        self.familia.text = result[1]
        self.class1.text = result[2]
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        App.get_running_app().screenStack.append("UpdateProfile")
    def click1(self,btn):
        App.get_running_app().email = self.mail.text
        email_ok = isValidEmail( self.mail.text )
        m_record = execSQL( 'SELECT * FROM users WHERE email = ' + cwq(self.mail.text))
        if m_record == None:
            App.get_running_app().show_popup("This user doesn't exist.")
        else:


            if not (self.familia.text) or not (self.nam.text)  or not (
                    self.mail.text) or not self.class1.text :
                App.get_running_app().show_popup("You didn't write all.")
            elif email_ok == False:
                self.mail.text = ''
                App.get_running_app().show_popup( 'Your email is not correct' )
            elif self.class1.text in list("123456789") + ["10", "11"]:
                try:
                    execSQL('UPDATE users SET name = ' + cwq(self.nam.text) + ', surname = ' + cwq(self.familia.text) + ', class = ' + cwq(self.class1.text) + ', email = ' + cwq(self.mail.text) + ' WHERE email = ' + cwq(self.mail.text))
                except pymysql.Error as err:
                    App.get_running_app().show_popup("Database Error")

                else:
                    App.get_running_app().show_popup('Saved!')
            else:
                App.get_running_app().show_popup("Write the number of your class.")

class AboutProblem(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        App.get_running_app().screenStack.append("AboutProblem")
    def ClickOk(self, btn):
        try:
            mail = App.get_running_app().email
            if not self.feedback.text:
                App.get_running_app().show_popup("Write your comment !!!.")
            else:
                try:
                    sender = "Our email"
                    recipient = "Our email"
                    password = "Our password of email"
                    subject = "Письмо от пользователя: "+mail
                    text =  self.feedback.text

                    smtp_server = smtplib.SMTP_SSL( "smtp.mail.ru", 465 )
                    smtp_server.login( sender, password )
                    message = "Subject: {}\n\n{}".format( subject, text )
                    smtp_server.sendmail( sender, recipient, message.encode( 'utf-8' ) )
                    smtp_server.close()
                    execSQL('INSERT INTO feedback (postedBy, feedback) VALUES (' + cwq(mail) + ', ' + cwq(self.feedback.text) + ')')
                except pymysql.Error as err:
                    App.get_running_app().show_popup("Database Error")
                else:
                    self.feedback.text = ''
                    App.get_running_app().show_popup("Your feedback was sent")
        except AttributeError:
            self.manager.current = 'Login'
            App.get_running_app().show_popup("You didn't sign up or sign in. Please do it")
        except Exception as e:
            print(e)

class Spravka(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        App.get_running_app().screenStack.append("Spravka")

class AboutAttachment(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        App.get_running_app().screenStack.append("AboutAttachment")

class Information(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        App.get_running_app().screenStack.append("Information")

    def showNews(self):
        self.newsLayout.clear_widgets()
        news = execSQL('SELECT * FROM info', one= False)
        self.newsLayout.bind(minimum_height=self.newsLayout.setter('height'))
        for i in news:
            Btn = Button(text= i[1],
                        halign= 'left',
                        background_normal= "",
                        color= [0, 0, 0, 1],
                        background_color= [0.9, 0.9, 0.9, 1])
            newID = i[0]
            Btn.bind(on_release= lambda x, id = newID : modalNews(id))
            self.newsLayout.add_widget(Btn)
    def offer(self):
        App.get_running_app().show_popup(text= "To offer news, please, \ncontact us using \nsupport@codinghurricane.org", size= 0.7)

class AboutDevelopers(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        App.get_running_app().screenStack.append("AboutDevelopers")

class DeleteProfile(Screen):
    def back(self):
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]
    def stack(self):
        if App.get_running_app().screenStack[-1] != "DeleteProfile":
            App.get_running_app().screenStack.append("DeleteProfile")
    def delete(self):
        if self.checkbox.active == True:
            try:
                execSQL('DELETE FROM users WHERE email = ' + cwq(App.get_running_app().email))
                App.get_running_app().show_popup("The profile was\nsuccessfully deleted!")
                self.manager.current = "Login"
            except Exception as e:
                App.get_running_app().screenStack = []
                print(e)
                App.get_running_app().show_popup("An error occured.")
                self.manager.current = "Set"
        else:
            App.get_running_app().show_popup("Please click this checkbox to delete\nthe profile.")
# No screen classes after this line!

# Widget and layout classes
class CustomAppException(Exception):
    pass

# No widget and layout classes after this line!

# The Screenmanager
# DO NOT MODIFY
class Screens(ScreenManager):
    email = ''
    def __init__(self, **kwargs):
        super(Screens, self).__init__(**kwargs)
    def build(self):
        sm = ScreenManager()

# The App class
class Bookcrossing(MDApp):
    current_book_id = ""
    def show_popup(self, text, size=0.5):
        self.popup = MDDialog(
            title=text,
            buttons=[MDFlatButton(text="OK",
                text_color=self.theme_cls.primary_color,
                on_release=self.close_popup)],
            size_hint_x = size)
        self.popup.open()
    def close_popup(self, instance):
        self.popup.dismiss()
    def build(self):
        self.m = Screens(transition=NoTransition())
        return self.m
    def toApp(self, dt):
        self.m.current = "MyBooks"

if __name__ == "__main__":
    Bookcrossing().run()
