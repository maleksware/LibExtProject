# Чтобы проверить ISBN, используйте функцию isValid() с аргументом ISBN.
# Изначально ISBN может содержать дефисы, цифры и пробелы по сторонам.
# Валидатор учитывает длину ISBN.



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
        print("10 - DIGIT ISBN")
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
        print("13 - DIGIT ISBN")
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
    ########################################

def isValid(isbn):
    isbn = splitISBN(isbn)
    return checkISBN(divideToCheck(isbn)[0],checkDigit = divideToCheck(isbn)[1])
