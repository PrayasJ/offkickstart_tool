from firebase import firebase
import sys
import datetime
import csv
from google.colab import files
import pandas as pd

firebase = firebase.FirebaseApplication('https://offkicksinc.firebaseio.com', None)

if sys.argv[1] == '--help':
    print("\n\tNo, LOL isn't Lots of Love, get out.")
    print("\tNote: If any input has multiple words put it in quotes, for example,\n")
    print("\t\tpython app.py -add_user \"Rahil Mulani\" \"Some Place\" 123456789 abc@xyz.com\n")
    print('\t-add_user\n')
    print('\t\tRequires Name, Location, Contact Number, Email\n')
    print('\t\tExample: python app.py -add_user randomName randomLocation 123456789 email@domain.com\n')
    print('\t-add_product\n')
    print('\t\tRequires Product ID, Size, Cost, Price, Points\n')
    print('\t\tExample: python app.py -add_product "Air Jordan 1" High 5000 6000 100\n')
    print('\t-purchase\n')
    print("\t\tRequires User ID, Product Name, Size, Quantity.\n\t\tIf no Quantity is specified it defaults to 1.\n")
    print('\t\tExample: python app.py -purchase OK20001 "Air Jordan 1" High')
    print('\t\tExample: python app.py -purchase OK20001 "Air Jordan 1" Medium 4\n')
    print('\t-list\n')
    print('\t\tproducts\n')
    print('\t\t\tSaves product list in the working directory.\n')
    print('\t\t\tExample: python app.py -list products\n')
    print('\t\tusers\n')
    print('\t\t\tSaves list of clients in the working directory.\n')
    print('\t\t\tExample: python app.py -list users\n')
    print('\t\tpurchases\n')
    print('\t\t\tSaves list of purchases by the specified user in the working directory.\n')
    print('\t\t\tRequires User ID')
    print('\t\t\tExample: python app.py -list purchases OK20003')

if sys.argv[1] == '-add_user':
    name = sys.argv[2]
    locat = sys.argv[3]
    c_no = sys.argv[4]
    email = sys.argv[5]
    data = firebase.get('/', '')
    curr_year = str(datetime.datetime.now().year)[2:4]
    try:
        data = [value for key, value in data.items() if key[2:4] == str(curr_year)]
    except:
        pass
    _id = "OK"+str(curr_year)+str(len(data)+1).zfill(3)
    out =  { 'Name': name,
          'Location': locat,
          'Contact': c_no,
          'Email': email,
          'Total_points': 0
          }
    firebase.patch('/'+_id,out)

if sys.argv[1] == '-purchase':
    _id = sys.argv[2]
    prod_name = sys.argv[3]
    prod_size = sys.argv[4]
    prod_quantity = 1
    try:
        prod_quantity = int(sys.argv[5])
    except:
        pass
    data = firebase.get('/'+_id, '')
    points = int(data['Total_points'])
    points += int(firebase.get('/Products/'+prod_name+'/'+prod_size+'/Points', ''))*int(prod_quantity)
    tot_prod = 'Purchase_0'
    try:
        tot_prod = 'Purchase_'+str(len(firebase.get('/'+_id+'/purchases','')))
    except:
        pass
    out = { 'Name': prod_name,
            'Size': prod_size,
            'Quantity': prod_quantity,
            'Amount': prod_quantity * int(firebase.get('/Products/'+prod_name+'/'+prod_size+'/Price', '')), 
            'DOP': datetime.datetime.now().strftime('%y-%m-%d %a %H:%M:%S')
    }
    firebase.patch('/'+_id, {'Total_points': points})
    firebase.patch('/'+_id+'/purchases/'+tot_prod ,out)

if sys.argv[1] == '-add_product':
    prod_id = sys.argv[2]
    prod_size = sys.argv[3]
    prod_cost = int(sys.argv[4])
    prod_price = int(sys.argv[5])
    prod_point = int(sys.argv[6])
    out = { prod_size : {'Points': prod_point, 'Cost': prod_cost, 'Price': prod_price} }
    firebase.patch('/Products/'+prod_id,out)

if sys.argv[1] == '-list':
    data_file = ''
    fname = ''
    data = []
    if sys.argv[2] == 'products':
        #data_file = open('product_list.csv', 'w', newline = '')
        fname = 'product_list.csv'
        temp = firebase.get('/Products', '')
        data.append(['ID','Size','Price','Cost','Points'])
        for key,value in temp.items():
            for key2,values2 in value.items():
                data.append([key, key2, values2['Price'], values2['Cost'], values2['Points']])
    if sys.argv[2] == 'users':
        #data_file = open('user_list.csv', 'w', newline = '')
        temp = firebase.get('/', '')
        fname = 'user_list.csv'
        data.append(['ID','Name','Location','Contact','Email','Points'])
        temp.pop('Products','None')
        for key,value in temp.items():
            data.append([key, value['Name'], value['Location'], value['Contact'], value['Email'], value['Total_points']])
    if sys.argv[2] == 'purchases':
        _id = sys.argv[3]
        #data_file = open(_id+'_list.csv', 'w', newline = '')
        fname = _id+'_list.csv'
        temp = firebase.get('/'+_id+'/purchases', '')
        data.append(['Purchase ID', 'Name', 'Size', 'Quantity', 'Amount', 'Date'])
        for key, value in temp.items():
            data.append([key, value['Name'], value['Size'], value['Quantity'], value['Amount'], value['DOP']])

    #csv_writer = csv.writer(data_file) 
    #for l in data:
    #    csv_writer.writerow(l)
    #data_file.close()
    df = pd.DataFrame(data)
    df.to_csv(fname)
    files.download(fname)
