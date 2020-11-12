import sqlite3
def bookSearch(request):
    m_connect = sqlite3.connect("sb.db")
    m_cursor = m_connect.cursor()
    m_cursor.execute('SELECT * FROM books')
    booklist = m_cursor.fetchall()
    print(booklist)
#    results = []
#    request = request.lower()
#    for book in bookList:
#        title = str(book[0]).lower()
#        isbn = str(book[1]).lower()
#        author = str(book[2]).lower()
#        code = str(book[3]).lower()
#        tags = tuple(book[4])
#        if request in title or request in isbn or request in author or request in code or request in tags:
#            results.append(book)
#    return results
bookSearch("g")
