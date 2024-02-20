from django.shortcuts import render
from .models import Contact
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


from django.shortcuts import render
from .models import Contact

def scrap(request):
    person_details = None
    
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber')
        
        r = requests.get('https://www.iitb.ac.in/en/about-iit-bombay/contact-us')
        soup = BeautifulSoup(r.text, 'html.parser')
        contact_details_tags = soup.find_all('div', class_='contact-details')

        contact_details_list = []
        for contact_details_tag in contact_details_tags:
            text_content = contact_details_tag.get_text(strip=True)
            
            email_links = [a['href'] for a in contact_details_tag.find_all('a', href=True)]
            
            contact_details_list.append({
                'text_content': text_content,
                'web_links': email_links
            })

        contacts_data = []

        for contact_details in contact_details_list:
            data = {'Name/Profession': '', 'Address': '', 'Phone': '', 'Fax': '', 'Web': ''}

            # Extracting information based on patterns in text_content
            if 'Chairperson' in contact_details['text_content']:
                data['Name/Profession'] = 'Chairperson GATE'
            elif 'Chairman' in contact_details['text_content']:
                data['Name/Profession'] = 'Chairman,JEE (Advanced), UCEED & CEED'
                
            elif 'Prof' in contact_details['text_content']:
                data['Name/Profession'] = 'Prof.K.G.Suresh'
                
            elif '+91 (22) 2572 2545' in contact_details['text_content']:
                data['Name/Profession'] = 'IIT Bombay Office'
                

            # Extracting address, phone, fax, and email using regular expressions
            address_match = re.search(r'Address:(.*?)(Phone:|$)', contact_details['text_content'])
            data['Address'] = address_match.group(1).strip() if address_match else 'Department of Physics'
            data['Address'] = data['Address'].split(',')[0]

            phone_match = re.search(r'Phone:(.*?)(Fax:|$)', contact_details['text_content'])
            data['Phone'] = re.sub(r'[^0-9+/]', '', phone_match.group(1)) if phone_match else ''

            fax_match = re.search(r'Fax:(.*?)(E-?mail:|$)', contact_details['text_content'])
            data['Fax'] = re.sub(r'[^0-9+/]', '', fax_match.group(1)) if fax_match else ''

            data['Web'] = ', '.join(contact_details['web_links'])
            data['Web'] = data['Web'].split('.',1)[-1].split(',')[0]

            contacts_data.append(data)

        # Creating a DataFrame
        contacts_df = pd.DataFrame(contacts_data)

        contacts_df['Web'][1] = 'cvo.iitb.ac.in'
        contacts_df['Web'][0] = 'iitb.ac.in'

        for index, row in contacts_df.iterrows():
            Contact.objects.create(
                name_profession=row['Name/Profession'],
                address=row['Address'],
                phone=row['Phone'],
                fax=row['Fax'],
                email=row['Web']
            )

        if phone_number.isdigit() and any(phone_number in row['Phone'] for index, row in contacts_df.iterrows()):
            person_details = Contact.objects.filter(phone__contains=phone_number).first()

    return render(request, 'scrap_form.html', {'person_details': person_details})
