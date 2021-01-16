# -*- coding: utf8 -*-
"""Установка кодировки."""


# TODO: Remove Spaghetti Code
# TODO: Settings content
# TODO: Create testcases for testing
# TODO: Add ranks for users
# TODO: Recreate MyBooks and Search structure
# TODO: Interface Update
# TODO: Add User and ISBN class support
# TODO: Backticks in execSQL function calls
# TODO: Add Log files
# TODO: Add documentation and docstrings
# TODO: Rewrite execSQL calls
# Kivy imports

import re

import kivy
from kivy.config import Config
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.toast import toast

import pymysql
# No imports after this line!


# System configs
Config.set("graphics", "resizable", "false")
Config.set("graphics", "width", 450)
Config.set("graphics", "height", 800)
kivy.require("2.0.0")
Window.size = (450, 800)
# No system settings and configs after this line!


# Functions
def generateModalTextBook(book):
    """Создание текста модальных окон книг."""
    owner = book[0]
    id = book[2]
    isbn = book[3]
    author = book[5]
    description = book[6]
    tags = showTags(book[7])
    station = book[8]
    text = []
    text.append("Автор: " + author)
    text.append("ISBN: " + isbn)
    text.append("ID: " + id)
    text.append("Описание: " + description)
    text.append("Теги: " + tags)
    if station != "The book was taken":
        text.append("Станция: " + station)

    else:
        request = 'SELECT name, surname FROM users WHERE email = ' + cwq(owner)
        ownerText = execSQL(request)
        ownerText = " ".join(ownerText)
        text.append("Владелец: " + ownerText)
    return "\n\n".join(text)


def cwq(string):
    """Обертывание строки кавычками."""
    return '"' + str(string) + '"'


def execSQL(sql, one=True, debugOutput=False, args=[]):
    """Выполнение SQL-запросов."""
    if args:
        for i in range(len(args)):
            args[i] = cwq(args[i])
        sql = sql.format(*args)

    if debugOutput:
        print(sql)
    connection = pymysql.connect(host="localhost",
                                 user="libextapp",
                                 password="userpass1234",
                                 db="bookcrossing",
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
    """Создание текста модальных окон новостей."""
    request = 'SELECT * FROM info WHERE id = ' + id
    news = execSQL(request)
    bookModal = MDDialog(title=news[0],
                         type="custom",
                         text=news[1],
                         buttons=[MDFlatButton(text="OK")],
                         size_hint=(0.7, None))
    bookModal.open()


def processLongTitle(text, processTo):
    """Обработка длинных строк."""
    if len(text) > processTo:
        return text[:processTo] + "..."
    else:
        return text


def hasThisBook(mail, book, reqType="book_id"):
    """Определение, есть ли у пользователя книга."""
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
    """Проверка, является ли строка ID книги."""
    text = str(text)
    request = 'SELECT * FROM books WHERE book_id = ' + cwq(text)
    result = execSQL(request)
    if result is None:
        return False
    else:
        return True


def isISBN(text):
    """Проверка, является ли строка ISBN книги."""
    text = reduceISBN(text)
    if len(text) not in (10, 13):
        return False
    if isValid(text):
        return True


def reduceISBN(isbn):
    """Приведение ISBN к числовому виду для последующей проверки."""
    reducedISBN = "".join(isbn.split("-"))
    return reducedISBN


def encodeTagsLine(tags):
    """Превращение кортежа тегов в 1 строку."""
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
    tags.append("book")
    tags = list(set(tags))
    return "^".join(tags)


def decodeTagsLine(tags):
    """Превращение строки тегов в 1 кортеж."""
    return tags.split("^")


def showTags(tags):
    """Визуальное отображение тегов."""
    tags = tags.split("^")
    toShow = []
    for tag in tags:
        tag = "#" + tag
        toShow.append(tag)
    return ", ".join(toShow)


def my_books():
    """Получение книг, принадлежащих пользователю."""
    mail = App.get_running_app().email
    request = 'SELECT * FROM books WHERE owner = ' + cwq(mail)
    result = None
    try:
        result = execSQL(request, one=False)

    except pymysql.Error as err:
        App.get_running_app().show_dialog(DBERR + str(err))

    return result


def modalview(b_id):
    """Получение информации для отображения на модальном окне книги."""
    request = 'SELECT * FROM books WHERE book_id = ' + cwq(str(b_id))
    result = None
    try:
        result = execSQL(request)
    except pymysql.Error as err:
        App.get_running_app().show_dialog(DBERR + str(err))
    return result


def modal():
    """Функция-ссылка: см.App.get_running_app().show_book_dialog()."""
    App.get_running_app().show_book_dialog()


def f_btn_book(self, a_id):
    """Функция-ссылка: см. modal()."""
    App.get_running_app().current_book_id = a_id
    modal()


def bookSearch(request):
    """Поиск книги по введенным данным."""
    bookList = execSQL('SELECT * FROM books', one=False)

    results = []
    request = request.lower()
    for book in bookList:
        tags = tuple(decodeTagsLine(book[7]))
        for point in book:
            point = str(point).lower()
            if isISBN(point):
                point = reduceISBN(point)
            if request in point:
                results.append(book)
        if request in tags:
            results.append(book)
    return list(set(results))


def splitISBN(isbn):
    """Приведение ISBN в числовой вид."""
    isbn = list(isbn.split("-"))
    isbn = list("".join(isbn).strip())
    return "".join(isbn)


def divideToCheck(isbn):
    """Деление ISBN на значимую и контрольную части."""
    return (isbn[:-1], isbn[-1])


def checkISBN(isbn, checkDigit):
    """Проверка ISBN на соответствие правилам."""
    try:
        sum = 0
        ######################################
        if len(isbn) == 9:
            for i in range(10, 1, -1):
                isbnNum = int(isbn[10 - i])
                sum += isbnNum * i
            sum %= 11
            if checkDigit == "X":
                checkDigit = 10
            if (int(checkDigit) + sum) % 11 == 0:
                return True
            else:
                return False
        ######################################
        elif len(isbn) == 12:
            if checkDigit == "X":
                checkDigit = 10
            indexes = [1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3]
            for i in range(len(isbn)):
                sum += (int(isbn[i]) * indexes[i])
            sum = sum % 10
            if (int(checkDigit) + sum) % 10 == 0:
                return True
            else:
                return False
        else:
            return False
    except Exception:
        return False


def isValid(isbn):
    """Выполняет все операции с ISBN от сырой строки до проверки."""
    isbn = splitISBN(isbn)
    return checkISBN(divideToCheck(isbn)[0], checkDigit=divideToCheck(isbn)[1])


def isValidEmail(email):
    """Проверяет email на следование правилам. Будет заменена re.match()."""
    def isValidHost(host):
        if "." not in host:
            return False
        hostValidSymbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
                           "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower() + \
                           "0123456789" + "-" + "."
        for i in host:
            if i not in hostValidSymbols:
                return False
        return True

    def isValidUser(user):
        if user.startswith('"') and user.endswith('"'):
            quoted = True
        else:
            quoted = False
        userValidSymbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + \
                           "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower() + \
                           "0123456789" + "!#$%&'*+-/=?^_`{|}~"
        for i in user:
            if i not in userValidSymbols:
                return False
        if not quoted and ".." in user:
            return False
        if user.startswith(".") or user.endswith("."):
            return False

        if not quoted:
            for i in user:
                if i in '(),:;<>@[\\]"':
                    return False
        return True

    email = email.split("@")
    user = email[0]
    host = email[1]
    if isValidUser(user) and isValidHost(host):
        return True
    return False


def upgradeRank(rank, count=1):
    """Увеличивает ранг пользователя на count."""
    rank = int(rank)
    rank += count
    return str(rank)


def getNameAndSurname(email):
    """Возвращает имя и фамилию пользователя по email."""
    name, surname = tuple(execSQL("SELECT name, surname "
                                  "FROM users WHERE email = "
                                  + cwq(email)))
    return name, surname


def give_book(book, station, type="book_id", show_station_dialog=False):
    """Сдача книги на станцию."""
    if App.get_running_app().dialog:
        App.get_running_app().close_dlg("instance")

    if show_station_dialog:
        App.get_running_app().show_station_text_dialog()

    try:
        if type == "auto":
            if isISBN(book):
                type = "isbn"
            else:
                type = "id"
        if type == "isbn":
            execSQL('UPDATE books SET owner = "None", '
                    + 'station = {} WHERE isbn = {}',
                    args=[station, book],
                    debugOutput=True)
        elif type == "book_id":
            execSQL('UPDATE books SET owner = "None", '
                    + 'station = {} WHERE book_id = {}',
                    args=[station, book],
                    debugOutput=True)
    except Exception as e:
        print("TAKE_BOOK EXCEPTION:", e)
    toast(SUCCESS)
    App.get_running_app().root.get_screen('MyBooks').bnav.switch_tab("MyBooks")
    App.get_running_app().close_station_text_dialog("instance")


def take_book(book, user, type="book_id"):
    """Взятие книги пользователем."""
    if App.get_running_app().dialog:
        App.get_running_app().close_dlg("instance")

    try:
        if type == "auto":
            if isISBN(book):
                type = "isbn"
            else:
                type = "id"
        if type == "isbn":
            execSQL('UPDATE books SET owner = {}, '
                    + 'station = "The book was taken" WHERE isbn = {}',
                    args=[user, book],
                    debugOutput=True)
        elif type == "book_id":
            execSQL('UPDATE books SET owner = {}, '
                    + 'station = "The book was taken" WHERE book_id = {}',
                    args=[user, book],
                    debugOutput=True)
    except Exception as e:
        print("TAKE_BOOK EXCEPTION:", e)

    toast(SUCCESS)


def bookOnStation(book, type="isbn"):
    """Проверка того, лежит ли книга на станции."""
    try:
        if type == "auto":
            if isISBN(book):
                type = "isbn"
            else:
                type = "id"
        if type == "isbn":
            place = execSQL('SELECT station FROM books WHERE isbn = {}',
                            args=[book])
        elif type == "book_id":
            place = execSQL('SELECT station FROM books WHERE book_id = {}',
                            args=[book])
        if place[0] == "The book was taken":
            return False
        else:
            return True
    except Exception as e:
        print("BOOK ON STATION EXCEPTION:", e)
# No functions after this line!


# Classes of the screens
class Annot(Screen):
    """Первый загрузочный экран."""

    def on_enter(self):
        """Выполняет загрузку данных."""
        Clock.schedule_once(self.load)

    def load(self, dt):
        """Выполняет загрузку данных."""
        global dataLoaded
        if not dataLoaded:
            print("data loading...")
            print("going Loading...")
            dataLoaded = True
            self.manager.current = "Loading"
        else:
            self.manager.current = "Loading"


class Loading(Screen):
    """Второй загрузочный экран."""

    def toLogin(self):
        """Выполняет преход на другой экран."""
        App.get_running_app().screenStack = []
        print("toLogin")
        self.manager.current = "Login"


class Login(Screen):
    """Экран входа."""

    def clearEmail(self):
        """Выполняет очистку поля email."""
        App.get_running_app().email = None

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Login")

    def checkToLoading(self):
        """Выполняет проверку перехода на другой экран."""
        global firstEnter
        if firstEnter:
            firstEnter = False
            self.manager.current = "Loading"

    def switch(self, btn):
        """Выполняет переход на экран MyBooks."""
        App.get_running_app().email = self.mail.text
        request = 'SELECT * FROM users WHERE email = ' + cwq(self.mail.text)
        m_record = execSQL(request)
        if m_record is None:
            self.mail.text = ''
            App.get_running_app().show_dialog(EMNF)
        else:
            if not self.mail.text:
                App.get_running_app().show_dialog(EMNC)
            else:
                self.defineRank()
                self.manager.current = 'MyBooks'

    def defineRank(self):
        """Выполняет определение ранга пользователя."""
        mail = cwq(self.mail.text)
        user = execSQL('SELECT * FROM users WHERE email = ' + mail)
        App.get_running_app().rank = user[-1]
        print(user[-1])


class MyBooks(Screen):
    """Главный экран с BottomNavigation."""

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("MyBooks")

    def __init__(self, **kwargs):
        """Стандартный метод инициализации объекта класса Screen."""
        super(MyBooks, self).__init__(**kwargs)

    def my_book(self, btn):
        """Отображение книг на экране."""
        self.bookLayout.clear_widgets()
        self.bookLayout.bind(minimum_height=self.bookLayout.setter('height'))
        try:
            books = my_books()
            if books != ():
                k = 0
                for i in books:
                    k = k + 1
                    cnt = (processLongTitle(str(i[5]), 20) + " : "
                           + processLongTitle(str(i[4]), 20))
                    Btn = Button(background_color=[0.9, 0.9, 0.9, 1],
                                 color=(0, 0, 0, 1),
                                 text="  " + str(k) + ") " + cnt,
                                 text_size=(self.width, 30),
                                 halign="left",
                                 background_normal="")

                    m_book_id = i[2]
                    Btn.bind(on_release=lambda x,
                             m_book_id=m_book_id: f_btn_book(self, m_book_id))
                    self.bookLayout.add_widget(Btn)

            else:
                self.bookLayout.clear_widgets()
                self.bookLayout.add_widget(MDLabel(
                                        text="У вас нет книг,\nно есть время, "
                                             "чтобы взять их!",
                                        font_size=20))

        except AttributeError:
            self.manager.current = 'Login'
            App.get_running_app().show_dialog("Вы не выполнили вход")
        except Exception as e:
            print("AN EXCEPTION OCCURRED", e)


class Add(Screen):
    """Экран добавления книг в БД."""

    def clearInput(self):
        """Очистка всех полей."""
        self.isbn.text = ''
        self.kod.text = ''
        self.title.text = ''
        self.author.text = ''
        self.description.text = ''
        self.tags.text = ''

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Add")

    def addBook(self, g):
        """Добавление книги в БД."""
        try:
            isbn_ok = isValid(self.isbn.text)
            mail = App.get_running_app().email
            s_data = execSQL('SELECT * FROM stations WHERE id = '
                             + cwq(self.kod.text))

            if not (self.isbn.text
                    and self.title.text
                    and self.author.text
                    and self.description.text
                    and self.tags.text
                    and self.kod.text):
                App.get_running_app().show_dialog(NOTFILLED)
            elif not isbn_ok:
                self.isbn.text = ''
                App.get_running_app().show_dialog(ISBNNC)
            elif s_data == []:
                App.get_running_app().show_dialog(STANF)
                self.kod.text = ''
                return
            else:
                try:
                    table = execSQL('SELECT * from books WHERE isbn = '
                                    + cwq(self.isbn.text), one=False)
                    tags = encodeTagsLine(self.tags.text)
                    if table == ():
                        tableLength = len(execSQL('SELECT * FROM books',
                                                  one=False))
                        reducedISBN = reduceISBN(self.isbn.text)
                        execSQL('INSERT INTO books VALUES ('
                                + cwq(mail) + ', '
                                + cwq("None") + ', '
                                + cwq(tableLength + 1) + ', '
                                + cwq(reducedISBN) + ', '
                                + cwq(self.title.text) + ', '
                                + cwq(self.author.text) + ', '
                                + cwq(self.description.text) + ', '
                                + cwq(tags) + ', '
                                + cwq(self.kod.text) + ') ')

                        toast(SUCCESS)
                        return
                    else:
                        App.get_running_app().show_dialog(ALREXS)

                except pymysql.Error as err:
                    App.get_running_app().show_dialog(DBERR)
                    print(err)
                else:
                    self.clearInput()
        except AttributeError as Error:
            print(Error)
            self.clearInput()
            self.manager.current = 'Login'
            App.get_running_app().show_dialog(NOTLOG)
        except IndexError:
            App.get_running_app().show_dialog(NOTFILLED)


class Search(Screen):
    """Экран поиска книг."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Search")

    def __init__(self, **kwargs):
        """Стандартный метод инициализации объекта класса Screen."""
        super(Search, self).__init__(**kwargs)

    def search(self):
        """Отображение результатов поиска."""
        try:
            h = 'height'
            self.bookLayout.bind(minimum_height=self.bookLayout.setter(h))
            self.bookLayout.clear_widgets()
            row_height = 30
            books = bookSearch(self.searchTextInput.text)
            if books != []:

                self.bookLayout.add_widget(Label(text='Книги:',
                                                 text_size=(self.width,
                                                            row_height),
                                                 font_size=20,
                                                 halign='left'))
                k = 0
                for i in books:
                    k += 1
                    Btn = Button(background_color=[0.9, 0.9, 0.9, 1],
                                 color=(0, 0, 0, 1),
                                 background_normal="",
                                 text="  " + str(k) + ") "
                                      + processLongTitle(str(i[5]), 20) + " : "
                                      + processLongTitle(str(i[4]), 20),
                                 text_size=(self.width, row_height),
                                 halign='left',
                                 font_size=17,)
                    m_book_id = i[2]
                    Btn.bind(on_release=lambda x, m_book_id=m_book_id:
                             f_btn_book(self, m_book_id))
                    self.bookLayout.add_widget(Btn)
                self.bookLayout.add_widget(Widget())
            else:
                self.bookLayout.clear_widgets()
                self.bookLayout.add_widget(Label(text="Ничего не найдено :-("))

        except UnboundLocalError:
            return


class Set(Screen):
    """Экран настроек."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Set")


class SignUp(Screen):
    """Экран регистрации."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("SignUp")

    def click(self, btn):
        """Регистрайия пользователя."""
        App.get_running_app().email = self.mail.text
        strPattern = '(^|\\s)[-a-z0-9_.]+@([-a-z0-9]+\\.)+[a-z]{2,6}(\\s|$)'
        pattern = re.compile(strPattern)
        is_valid = pattern.match(self.mail.text)
        m_record = execSQL('SELECT * FROM users WHERE email = '
                           + cwq(self.mail.text))
        if m_record is None:
            if not (self.familia.text
                    and self.nam.text
                    and self.mail.text
                    and self.class1.text):
                App.get_running_app().show_dialog(NOTFILLED)
            elif not is_valid:
                self.mail.text = ''
                App.get_running_app().show_dialog(EMNC)
            elif self.class1.text in ["5", "6", "7", "8", "9", "10", "11"]:
                try:
                    execSQL('INSERT INTO users VALUES (' + cwq(self.nam.text)
                            + ', ' + cwq(self.familia.text) + ', '
                            + cwq(self.class1.text) + ', '
                            + cwq(self.mail.text) + ', ' + cwq("0") + ')')
                except pymysql.Error as err:
                    App.get_running_app().show_dialog(DBERR)
                    print(err)
                else:
                    self.manager.current = 'MyBooks'
                    App.get_running_app().show_dialog('Hello ' + self.nam.text)
            else:
                self.class1.text = ''
                App.get_running_app().show_dialog(NOTFILLED)
        else:
            self.mail.text = ''
            App.get_running_app().show_dialog(ALREXSUSER)


class Profile(Screen):
    """Экран профиля пользователя."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        if App.get_running_app().screenStack[-1] != "Profile":
            App.get_running_app().screenStack.append("Profile")

    def editProfile(self):
        """Обновление профиля."""
        self.manager.current = "UpdateProfile"

    def deleteProfile(self):
        """Удаление профиля."""
        self.manager.current = "DeleteProfile"

    def logout(self):
        """Выход из учетной записи."""
        App.get_running_app().email = None
        self.manager.current = "Login"

    def initProfile(self):
        """Инициализация надписей."""
        pair = getNameAndSurname(App.get_running_app().email)
        self.nameLabel.text = pair[0]
        self.surnameLabel.text = pair[1]


class UpdateProfile(Screen):
    """Экран обновления профиля пользователя."""

    def prepareInputs(self):
        """Заполняет поля нужными данными."""
        user = App.get_running_app().email
        self.mail.text = user
        result = execSQL('SELECT * FROM users WHERE email = ' + cwq(user))
        self.nam.text = result[0]
        self.familia.text = result[1]
        self.class1.text = result[2]

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("UpdateProfile")

    def click1(self, btn):
        """Метод обновления данных в БД."""
        App.get_running_app().email = self.mail.text
        email_ok = isValidEmail(self.mail.text)
        m_record = execSQL('SELECT * FROM users WHERE email = '
                           + cwq(self.mail.text))
        if m_record is None:
            App.get_running_app().show_dialog(EMNF)
        else:
            if not (self.familia.text and self.nam.text
                    and self.mail.text and self.class1.text):
                App.get_running_app().show_dialog(NOTFILLED)
            elif not email_ok:
                self.mail.text = ''
                App.get_running_app().show_dialog(EMNC)
            elif self.class1.text in list("123456789") + ["10", "11"]:
                try:
                    execSQL('UPDATE users SET name = ' + cwq(self.nam.text)
                            + ', surname = ' + cwq(self.familia.text)
                            + ', class = ' + cwq(self.class1.text)
                            + ', email = ' + cwq(self.mail.text)
                            + ' WHERE email = ' + cwq(self.mail.text))
                except pymysql.Error:
                    App.get_running_app().show_dialog(DBERR)

                else:
                    App.get_running_app().show_dialog(SVD)
            else:
                App.get_running_app().show_dialog(NOTFILLED)


class AboutProblem(Screen):
    """Экран отправки отзывов."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("AboutProblem")

    def ClickOk(self, btn):
        """Добавляет отзыв в БД."""
        try:
            mail = App.get_running_app().email
            if not self.feedback.text:
                App.get_running_app().show_dialog("Напишите ваш отзыв")
            else:
                try:
                    text = self.feedback.text
                    execSQL('INSERT INTO feedback VALUES (' + cwq(mail)
                            + ', ' + cwq(text) + ')')
                except pymysql.Error:
                    App.get_running_app().show_dialog(DBERR)
                else:
                    self.feedback.text = ''
                    App.get_running_app().show_dialog("Спасибо за отзыв!")
        except AttributeError:
            self.manager.current = 'Login'
            App.get_running_app().show_dialog(NOTLOG)
        except Exception as e:
            print(e)


class Spravka(Screen):
    """Справка о приложении."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Spravka")


class AboutTheApp(Screen):
    """Экран с информацией о приложении."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("AboutTheApp")


class Information(Screen):
    """Экран с новостями."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("Information")

    def showNews(self):
        """Отображение новостей на экране."""
        self.newsLayout.clear_widgets()
        news = execSQL('SELECT * FROM info', one=False)
        self.newsLayout.bind(minimum_height=self.newsLayout.setter('height'))
        for i in news:
            Btn = Button(text=i[1],
                         halign='left',
                         background_normal="",
                         color=[0, 0, 0, 1],
                         background_color=[0.9, 0.9, 0.9, 1])
            newID = i[0]
            Btn.bind(on_release=lambda x, id=newID: modalNews(id))
            self.newsLayout.add_widget(Btn)

    def offer(self):
        """Указывает контакты для обращения."""
        App.get_running_app().show_dialog(text="""Чтобы предложить новость,
                                                  свяжитесь с нами по почте
                                                  makegym1505v2.0@gmail.com""",
                                          size=0.7)


class AboutDevelopers(Screen):
    """Экран о разработчиках."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        App.get_running_app().screenStack.append("AboutDevelopers")


class DeleteProfile(Screen):
    """Экран удаления профиля."""

    def back(self):
        """Стандартный метод возвращения на предыдущий экран."""
        del App.get_running_app().screenStack[-1]
        self.manager.current = App.get_running_app().screenStack[-1]

    def stack(self):
        """Стандартный метод добавления экрана в стек."""
        if App.get_running_app().screenStack[-1] != "DeleteProfile":
            App.get_running_app().screenStack.append("DeleteProfile")

    def delete(self):
        """Стандартный метод возвращения на предыдущий экран."""
        if self.checkbox.active:
            try:
                userEmail = App.get_running_app().email
                execSQL('DELETE FROM users WHERE email = ' + cwq(userEmail))
                App.get_running_app().show_dialog("Профиль успешно удален!")
                self.manager.current = "Login"
            except Exception as e:
                App.get_running_app().screenStack = []
                print(e)
                App.get_running_app().show_dialog(DBERR)
                self.manager.current = "Set"
        else:
            App.get_running_app().show_dialog("""Пожалуйста,
                                                 отметьте галочку""")
# No screen classes after this line!


# Widget and layout classes
class TextDialogContent(BoxLayout):
    """Пустой класс, вся информация в .kv файле."""

    pass


class CustomAppException(Exception):
    """Исключение."""

    pass
# No widget and layout classes after this line!


# Global variables with their comments
ISBNNF = "ISBN не найден"
ISBNNC = "ISBN содержит ошибку"
IDNF = "ID не найден"
IDNC = "ID содержит ошибку"
STANF = "Станция не найдена"
BNF = "Книга не найдена"
EMNF = "Email не найден"
EMNC = "Email содержит ошибку"
NOTYOURS = "Эта книга не ваша!"
NOTLOG = "Пожалуйста, выполните вход"
NOTFILLED = "Вы заполнили не все поля"
ALRHAS = "У вас уже есть эта книга"
SUCCESS = "Успешно!"
DBERR = "Ошибка базы данных. Проверьте подключение к интернету."
IDISBNNC = "ID или ISBN содержит ошибку"
ALREXS = "Эта книга уже есть в базе."
ALREXSUSER = "Пользователь с этим email уже зарегистрирован."
SVD = "Данные сохранены"
firstEnter = True
dataLoaded = False
ranking = {10: "Student",
           50: "Librarian",
           100: "Booklover",
           200: "Top Reader",
           500: "Writer"}


# No global vars after this line!
# The Screenmanager
# DO NOT MODIFY
class Screens(ScreenManager):
    """Главный менеджер экранов."""

    email = ''

    def __init__(self, **kwargs):
        """Инициализация."""
        super(Screens, self).__init__(**kwargs)

    def build(self):
        """Создание менеджера экранов."""
        sm = ScreenManager()
        App.get_running_app().sm = sm
# The App class


class Bookcrossing(MDApp):
    """Основной класс приложения."""

    current_book_id = ""
    text_dialog = None
    dialog = None

    def show_book_dialog(self):
        """Открытие модальных окон книг."""
        user = App.get_running_app().email
        book_id = App.get_running_app().current_book_id
        if book_id == "" or book_id is None:
            return None
        book = modalview(book_id)
        if book is None:
            return None

        if bookOnStation(book_id, type="book_id"):
            actionButton = MDRaisedButton(
                        text="Взять книгу",
                        on_release=lambda x: take_book(book_id, user))
        else:
            actionButton = MDRaisedButton(
                        text="Сдать книгу",
                        on_release=lambda x:
                        App.get_running_app().show_station_text_dialog())

        self.dialog = MDDialog(title=book[4],
                               type="custom",
                               text=generateModalTextBook(book),
                               buttons=[actionButton,
                                        MDFlatButton(text="OK",
                                                     on_press=self.close_dlg)],
                               size_hint=(0.7, 0.5))
        self.dialog.open()

    def show_dialog(self, text, size=0.5):
        """Открытие модальных окон."""
        self.dialog = MDDialog(
            title=text,
            buttons=[MDFlatButton(text="OK",
                                  text_color=self.theme_cls.primary_color,
                                  on_release=self.close_dlg)],
            size_hint_x=size)
        self.dialog.open()

    def show_station_text_dialog(self):
        """Открытие модальных окон станции."""
        OKButton = MDRaisedButton(
            text="OK",
            on_release=lambda x: Clock.schedule_once(
                lambda x: give_book(
                    book=App.get_running_app().current_book_id,
                    station=self.text_dialog.content_cls.text_field.text), .1))

        cancelButton = MDFlatButton(text="ОТМЕНА",
                                    on_release=self.close_station_text_dialog)

        self.text_dialog = MDDialog(title="Код станции:",
                                    type="custom",
                                    content_cls=TextDialogContent(),
                                    size_hint=(0.7, 0.4),
                                    buttons=[cancelButton, OKButton])
        self.text_dialog.open()

    def close_dlg(self, instance):
        """Закрытие модальных окон."""
        if self.dialog:
            self.dialog.dismiss()

    def close_station_text_dialog(self, instance):
        """Закрытие модальных окон."""
        if self.text_dialog:
            self.text_dialog.dismiss()

    def build(self):
        """Создание App."""
        self.m = Screens(transition=NoTransition())
        return self.m

    def toApp(self, dt):
        """Домашний экран."""
        self.m.current = "MyBooks"


if __name__ == "__main__":
    Bookcrossing().run()
