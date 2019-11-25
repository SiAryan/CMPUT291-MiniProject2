from bsddb3 import db
from datetime import datetime, timedelta

symbols = [':', '<', '>', '>=', '<=', '=']
keyDict = {
    'subj' : 'te.idx',
    'body' : 'te.idx',
    'cc' : 'em.idx',
    'bcc' : 'em.idx',
    'to' : 'em.idx',
    'from' : 'em.idx',
    'date' : 'da.idx',
}

dateformat = '%Y/%m/%d'

def termsDatabase(): 
    database = db.DB()
    #database.set_flags(db.DB_DUP)
    DB_File = 'te.idx'
    database.open(DB_File, None, db.DB_BTREE)
    
    return database
    
    
def emailsDatabase():
    database = db.DB()
    #database.set_flags(db.DB_DUP)
    DB_File = 'em.idx'
    database.open(DB_File, None, db.DB_BTREE)    
    return database
    

def recsDatabase():
    database = db.DB()
    #database.set_flags(db.DB_DUP)
    DB_File = 're.idx'
    database.open(DB_File, None, db.DB_HASH)
    return database
    

def datesDatabase():
    database = db.DB()
    #database.set_flags(db.DB_DUP)
    DB_File = 'da.idx'
    database.open(DB_File, None, db.DB_BTREE)
    return database
    
def equality(key, values):
    results = []
    x = keyDict.get(key)
    
    for i in values:
        if x == 'te.idx':
            database = termsDatabase()
            curs = database.cursor()
            if key == 'subj':
                iter = curs.set(b's-'+i.encode("utf-8"))
                #print("{0:b}".format(b's-'+i.encode("utf-8")))
            elif key == 'body':
                iter = curs.set(b'b-'+i.encode("utf-8"))

        elif x == 'em.idx':
            database = emailsDatabase()
            curs = database.cursor()
            if key == 'cc':
                iter = curs.set(b'cc-'+i.encode("utf-8"))
            elif key == 'bcc':
                iter = curs.set(b'bcc-'+i.encode("utf-8"))
            elif key == 'to':
                iter = curs.set(b'to-'+i.encode("utf-8"))
            elif key == 'from':
                iter = curs.set(b'from-'+i.encode("utf-8"))
                
        elif x == 'da.idx':
                database = datesDatabase()
                curs = database.cursor()
                iter = curs.set(i.encode("utf-8"))
                
        #print(result)
        #iter = curs.first()
        if iter!=None:
            results.append(iter[1].decode("utf-8"))
            for i in range(curs.count()-1):
                iter = curs.next_dup()
                results.append(iter[1].decode("utf-8"))
                
        #print(results)
        #return results

        #while iter:
        #    print(curs.count())
        #    print((iter[0].decode("utf-8"), iter[1].decode("utf-8")))
        #        
        #    dup = curs.next_dup()
        #    while(dup!=None):
        #        print(dup)
        #        dup = curs.next_dup()
        #    iter = curs.next()

    curs.close()
    database.close()
        
        
        #results.append(result)
        #results.append(i)
    
    return results
   
def rangeQ(key, value, operator):
    results = []
    x = keyDict.get(key)
    if x == 'da.idx':
        database = datesDatabase()
        curs = database.cursor()
        if operator == '>':
            newObject = datetime.strptime(value, dateformat) + timedelta(days=1)
            value = newObject.strftime(dateformat)
            iter = curs.set_range(value.encode("utf-8"))
            while (iter != None):
                results.append(iter[1].decode("utf-8"))
                iter = curs.next()
                
            #print(results)
            return results
            
        elif operator == '>=':
            iter = curs.set_range(value.encode("utf-8"))
            
            while (iter != None):
                results.append(iter[1].decode("utf-8"))
                iter = curs.next()
                
            #print(results)
            return results
        elif operator == '<':
            iter = curs.set_range(value.encode("utf-8"))
            iter = curs.first()
            while(iter !=None):
                if(str(iter[0].decode("utf-8"))>=value): 
                    break
                results.append(iter[1].decode("utf-8"))
                iter = curs.next()
            #print(results)
            return results
        elif operator == '<=':
            iter = curs.first()
            while(iter !=None):
                if(str(iter[0].decode("utf-8"))>value): 
                    break
                results.append(iter[1].decode("utf-8"))
                iter = curs.next()
            #print(results)
            return results
        

def doBoth(key):
    results = []
    database = termsDatabase()
    curs = database.cursor()
    iter = curs.set(b's-'+key.encode("utf-8"))
    if iter!=None:
            results.append(iter[1].decode("utf-8"))
            for i in range(curs.count()-1):
                iter = curs.next_dup()
                results.append(iter[1].decode("utf-8"))

    iter = curs.set(b'b-'+key.encode("utf-8"))
    if iter!=None:
            results.append(iter[1].decode("utf-8"))
            for i in range(curs.count()-1):
                iter = curs.next_dup()
                results.append(iter[1].decode("utf-8"))

    curs.close()
    database.close()
    return results


def lookup(query):
    results = []
    k = True
    querytype = ''
    key = ''
    value = ''
    values = []
    operators = []
    for char in query:
        if char in symbols:
            k = False
            if char == ':':
                querytype = 'equality'
            elif char == '>' or char == '<':
                querytype = 'range'
                operators.append(char)
            elif char == '=' and operators:
                querytype = 'range'
                operators[0] = operators[0] + char
            elif char == '=' and not(operators):
                querytype = 'equality'

        elif k:
            key = key + char.lower()
        elif not(k):
            if char == '-':
                values.append(value) 
                value = ''
            else:
                value = value + char.lower()
    values.append(value)
    #print(values)
    #print(operators)
    #print(querytype)
    if querytype == 'equality':
        #equality(key, values)
         results = equality(key, values)
    elif querytype == 'range':
        results = rangeQ(key, values[0], operators[0])
    elif querytype == '':
        results = doBoth(key)


    return results
    
    


def getQueries():
    while (True):
        results = []
        query = input("enter the query below:\n")
        if query == 'q':
            break
        query = query.split(' ')
        while '' in query:
            query.remove('')
        #print(query)
        formatted = []
        for i in range(len(query)):
            if query[i] in symbols:
                formatted.append(''.join([query[i-1],query[i],query[i+1]]))
            elif (query[i][0] in symbols and len(query[i]) > 1):
                formatted.append(''.join([query[i-1], query[i]]))
            elif (query[i][-1] in symbols and len(query[i]) > 1):
                formatted.append(''.join([query[i], query[i+1]]))
            elif (':' in query[i] and query[i][0] != ':' and query[i][-1] != ':'):
                formatted.append(query[i])
            elif ('<' in query[i] and query[i][0] != '<' and query[i][-1] != '<'):
                formatted.append(query[i])
            elif ('>' in query[i] and query[i][0] != '>' and query[i][-1] != '>'):
                formatted.append(query[i])
            elif ('>=' in query[i] and query[i][0] != '>=' and query[i][-1] != '>='):
                formatted.append(query[i])
            elif ('<=' in query[i] and query[i][0] != '<=' and query[i][-1] != '<='):
                formatted.append(query[i])
            elif ('=' in query[i] and query[i][0] != '=' and query[i][-1] != '='):
                formatted.append(query[i])
            elif ('%' == query[i][-1]):
                formatted.append(query[i])
            elif (':' not in query[i] and '>' not in query[i] and '<' not in query[i] and '<=' not in query[i] and '>=' not in query[i] and '=' not in query[i]):
                #formatted[-1] = '-'.join([formatted[-1], query[i]])
                formatted.append(query[i])
        print(formatted)

        #for i in formatted:
        #    lookup(i)

        for i in formatted:
            results.append(lookup(i))
        
        for i in results:
            print(str(i)+'\n')    
        
        op = set.intersection(*map(set,results))

        if op:
            for i in op:
                print(i)
        else:
            print('None')



if __name__ == "__main__":
    termsDatabase()
    emailsDatabase()
    recsDatabase()
    datesDatabase()
    getQueries()
    