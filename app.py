# pip install flask
from flask import Flask, render_template, request
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perform_scrapping', methods=['POST'])
def perform_scrapping():
    if request.method == 'POST':
        try:
            searchString = request.form.get('content').replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            
            check = flipkart_html.find_all('div', {'class':"_3uTeW4"})
            if len(check)!=0:  # Check if the list is empty
                return 'Sorry, no results found!\n Please check the spelling or try searching for something else'
                
            else:
                response=flipkart_html.find_all('nav', {'class':"yFHi8N"})[0].find_all('a',{'class':'ge-49M'})
                for i in response:
                    flipkart_page="https://www.flipkart.com"+ i['href'] # every page
                    urlclient=uReq(flipkart_page)
                    flipkart_page1=urlclient.read()
                    flipkart_html=bs(flipkart_page1, 'html.parser')
                    bigbox=flipkart_html.find_all('div',{'class':"_13oc-S"})
                    rating=[]
                    user_name=[]
                    head_comments=[]
                    detail_comments=[]
                    for i in bigbox:
                        url2="https://www.flipkart.com"+ i.div.div.a['href']# single page
                        urlclient2=uReq(url2)
                        flipkart_page2=urlclient2.read()
                        product_html=bs(flipkart_page2, 'html.parser')
                        review_num = product_html.find('div', {'class':"_3UAT2v _16PBlm"}).text.split(' ')[1]
                        link_element = product_html.find('span', string="All {} reviews".format(review_num))
                        if link_element is not None:
                            link = link_element.find_parent('a')['href']
                            comment_link="https://www.flipkart.com"+link
                            urlclient3=uReq(comment_link)
                            flipkart_page3=urlclient3.read()
                            product_html2=bs(flipkart_page3, 'html.parser')
                            num_page = product_html2('nav',{'class': "yFHi8N"})[0].find_all('a',{'class':'ge-49M'})
                            for i in num_page:
                                comment_link= "https://www.flipkart.com"+ i['href']
                                comment_req=requests.get(comment_link)
                                comment_html=bs(comment_req.text,'html.parser')
                                rating_html=comment_html.find_all('div', {'class':"_3LWZlK _1BLPMq"})
                                name = comment_html.find_all('div',{'class':"row _3n8db9"})
                                head_comment_html = comment_html.find_all('p',{'class':"_2-N8zT"})
                                detail_comment_html = comment_html.find_all('div',{'class':"t-ZTKy"})

                                for i in rating_html:
                                    rating.append (str(i.text.strip()))
                                for i in name:
                                    user_name.append(str(i.div.find('p',{'class':"_2sc7ZR _2V5EHH"}).text.strip()))
                                for i in head_comment_html:
                                    head_comments.append(str(i.text.strip()))
                                for i in detail_comment_html:
                                    detail_comments.append(str(i.text.strip()))
                        else:
                            print("Link element not found.")
                        # Create a Pandas DataFrame to store the data
                        data = {'Ratings': rating, 'Name': name, 'Head_Comments': head_comments, 'Detail_comments': detail_comments}
                        df = pd.DataFrame(data)

                        # Save the data to an Excel file
                        df.to_excel('flipkart_products.xlsx', index=False)
                    return 'successfull'


            
        except Exception as e:
            logging.info(e)
            return 'Error: ' + str(e)
    else:
        return render_template('index.html')

app.run(debug=True) 