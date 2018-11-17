#!/usr/bin/env python 


import re
import time
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from xlsxwriter import Workbook


def get_decoded_string(unicode_string):
    return unidecode(unicode_string).strip().lstrip('"').rstrip('"')


def get_agency_profile_details(agency_name):
    """
        It return agency email id, state name, phone number
    """
    profile_url = 'https://clutch.co/profile/'
    profile_url = profile_url + agency_name
    print profile_url
    resp = requests.get(profile_url).content
    resp = BeautifulSoup(resp, 'html.parser')
    info_div = resp.find('div', {'class':'contact-dropdown-mpad'})
    #email = info_div.find('div', {'class':'field-item even'}).find('a')
    email = None  # TODO
    state = get_decoded_string(info_div.find('div', {'class':'city-name'}).text)
    phone = get_decoded_string(info_div.find('span', {'class':'contact-dropdown-phone-ico'}).text)

    return email, state, phone


def get_agencies(page=''):
    #main_url = 'https://clutch.co/agencies'
    #main_url = 'https://clutch.co/seo-firms'
    #main_url = 'https://clutch.co/directory/mobile-application-developers'
    #main_url = 'https://clutch.co/web-developers'
    #main_url = 'https://clutch.co/web-designers'
    #main_url = 'https://clutch.co/agencies/design'
    main_url = 'https://clutch.co/developers/ecommerce'
    
    if page != '':
        main_url = main_url + '?page={}'.format(page)
    print main_url

    resp = requests.get(main_url)

    # if requests is 200 then only going to process
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html.parser')
        return [str(agency.text).strip('\n') for agency in soup.find_all('h3')]

    # url/request failure returnin None
    return []


def get_agency_details(page='main'):
    """
       It returns agency name, description, email id, state name, phone number of all the 
       agencies listed in the provided webpage in a list of dictionaries data structure
    """
    print "Processing page : {}".format(page)
    #main_url = "https://clutch.co/seo-firms"
    #main_url = "https://clutch.co/directory/mobile-application-developers"
    #main_url = "https://clutch.co/web-developers"
    #main_url = 'https://clutch.co/web-designers'
    #main_url = 'https://clutch.co/agencies/design'
    main_url = 'https://clutch.co/developers/ecommerce'
    
    if page != 'main':
        main_url = main_url + '?page={}'.format(page)

    resp = requests.get(main_url).content
    resp = BeautifulSoup(resp, 'html.parser')
    agency_wise_details = []

    # get all div tag with class = 'col-xs-12 col-md-10 bordered-right provider-base-info'
    top_level_divs = resp.findAll('div', {'class':'col-xs-12 col-md-10 bordered-right provider-base-info'})
    top_level_links = resp.findAll('div', {'class':'col-xs-12 col-md-2 provider-link-details'})

    for top_div, top_div_link in zip(top_level_divs, top_level_links):
        try:
            # from div
            agency_name = get_decoded_string(top_div.find('h3', {'class':'company-name'}).text)
            #agency_description = get_decoded_string(top_div.findAll('p')[1].text) # TODO
            
            # from link
            #side_ul = top_div_link.find('ul', {'class':'nav nav-pills nav-stacked nav-right-profile'})
            #side_li = side_ul.findAll('li')[1]
            #profile_link = get_decoded_string(side_li.find('a',href=True)['href']).split('/')[2]
            #email, state, phone = get_agency_profile_details(profile_link)

            
            """agency_info_dict = {
                    'name' : agency_name,
                    'description' : agency_description,
                    'phone' : phone,
                    'email' : email,
                    'state' : state
            }"""
            agency_info_dict = {
                    'name' : agency_name
            }

            agency_wise_details.append(agency_info_dict)
        except Exception as e:
            #print e
            pass

    return agency_wise_details


def write_to_excel(data):
    ordered_list=["name"] #list object calls by index but dict object calls items randomly

    wb=Workbook("New File1.xlsx")
    ws=wb.add_worksheet("Agency Name") #or leave it blank, default name is "Sheet 1"

    first_row=0
    for header in ordered_list:
        col=ordered_list.index(header) # we are keeping order.
        ws.write(first_row,col,header) # we have written first row which is the header of worksheet also.

    row=1
    for player in data:
        for _key,_value in player.items():
            col=ordered_list.index(_key)
            ws.write(row,col,_value)
        row+=1 #enter the next row
    wb.close()


if __name__ == '__main__':
    start = time.time()
    # base url
    #main_url = 'https://clutch.co/agencies'
    #main_url = 'https://clutch.co/seo-firms'
    #main_url = 'https://clutch.co/directory/mobile-application-developers'
    #main_url = 'https://clutch.co/web-developers'
    #main_url = 'https://clutch.co/web-designers'
    #main_url = 'https://clutch.co/agencies/design'
    main_url = 'https://clutch.co/developers/ecommerce'

    # intial request
    resp = requests.get(main_url)

    if resp.status_code == 200:
        print "Going to parse the web content!"

    # storing response contents
    resp = resp.content

	# start manipulation of the DOM
    soup = BeautifulSoup(resp, 'html.parser')

	# get pagination info
    pagination = soup.findAll("li", {"class": "pager-current"})
    last_page = int(pagination[0].text.split(' ')[2])

	# getting all agencies from the base url
	#agencies = set(get_agencies())
    details = get_agency_details()

    try:
        for page in range(1,last_page+1):
            details.extend(get_agency_details(page))
    except KeyboardInterrupt:
        print "[WARN] :: Encountered keypress events!!!"\

    # write to excel
    print(len(details))
    write_to_excel(details)
    end = time.time()
    print "Elapsed time = {}".format(end-start)