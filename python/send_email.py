#!/usr/bin/env python
# -*- coding: us-ascii -*-

# Taken from a Stack-Overflow question.

import openpyxl, pprint

print('Opening Workbook...')
wb = openpyxl.load_workbook('C:/Users/Bijan/Desktop/Forest Baker #1-1H/Forest Baker #1-1H Email Cheat Sheet.xlsm' , data_only = True)
sheet = wb.get_sheet_by_name('Lateral_FlashLight')
sheet.title
print(sheet.title)
sheet['e10']
print(sheet['e10'].value)

degree_sign= u'\N{DEGREE SIGN}'


import openpyxl, pprint
print('Opening Workbook...')
print("")
wb = openpyxl.load_workbook('C:/Users/Bijan/Desktop/Forest Baker #1-1H/Forest Baker #1-1H Email Cheat Sheet.xlsm' , data_only = True)
sheet = wb.get_sheet_by_name('Lateral_FlashLight')
sheet.title
print(sheet.title)
print("")
sheet['e10']
well_name = sheet['e12'].value
well_value = sheet['f12'].value
rig_name = sheet['e13'].value
rig_value = sheet['f13'].value
plan_name = sheet['e14'].value
plan_value = sheet['f14'].value
md_name = sheet['e17'].value
md_value = str(sheet['f17'].value)
inc_name = sheet['e18'].value
inc_value = str(round(sheet['f18'].value, 2))
azm_name = sheet['e19'].value
azm_value = str(round(sheet['f19'].value, 2))
tvd_name = sheet['e20'].value
tvd_value = str(round(sheet['f20'].value, 2))
vs_name = sheet['e21'].value
vs_value = str(round(sheet['f21'].value, 2))
dls_name = sheet['e22'].value
dls_value = str(round(sheet['f22'].value, 2))
gamma_name = sheet['e23'].value
gamma_value = str(round(sheet['f23'].value, 2))
temp_name = sheet['e24'].value
temp_value = str(round(sheet['f24'].value, 2))
slide_name = sheet['e27'].value
slide_value = str(sheet['f27'].value)
tf_name = sheet['e28'].value
tf_value = str(sheet['f28'].value)
build_name = sheet['e29'].value
build_value = str(round(sheet['f29'].value, 2))
motor_name = sheet['e30'].value
motor_value = str(sheet['f30'].value)
up_name = sheet['e33'].value
up_value = str(sheet['f33'].value)
left_name = sheet['e34'].value
left_value = str(sheet['f34'].value)
pslide_name = sheet['e35'].value
pslide_value = str(sheet['f35'].value)
ptf_name = sheet['e36'].value
ptf_value = str(sheet['f36'].value)
fmd_name = sheet['e39'].value
fmd_value = str(sheet['f39'].value)
finc_name = sheet['e40'].value
finc_value = str(round(sheet['f40'].value, 2))
fazm_name = sheet['e41'].value
fazm_value = str(round(sheet['f41'].value, 2))
ftvd_name = sheet['e42'].value
ftvd_value = str(round(sheet['f42'].value, 2))
fvs_name = sheet['e43'].value
fvs_value = str(round(sheet['f43'].value, 2))
fgam_name = sheet['e44'].value
fgam_value = str(round(sheet['f44'].value, 2))


Subject = (sheet['e10'].value)

Comp = (    print(well_name , well_value ,), 
    print(rig_name , rig_value ,), 
    print(plan_name , plan_value ,), 
    print (""), 
    print(sheet['e16'].value ,), 
    print(md_name , md_value + u'\x27' ,), 
    print(inc_name , inc_value + u'\xb0' ,), 
    print(azm_name , azm_value + u'\xb0' ,), 
    print(tvd_name , tvd_value + u'\x27' ,), 
    print(vs_name , vs_value + u'\x27' ,), 
    print(dls_name , dls_value + u'\xb0' ,), 
    print(gamma_name , gamma_value +' API' ,), 
    print(temp_name , temp_value + u'\xb0' ,), 
    print(""), 
    print(sheet['e26'].value), 
    print(slide_name , slide_value + u'\x27'), 
    print(tf_name , tf_value + u'\xb0'), 
    print(build_name , build_value + u'\xb0'), 
    print(motor_name , motor_value + u'\xb0'), 
    print(""), 
    print(sheet['e32'].value), 
    print(up_name , up_value + u'\x27'), 
    print(left_name , left_value + u'\x27'), 
    print(ptf_name , ptf_value + u'\xb0'), 
    print(""), 
    print(sheet['e38'].value), 
    print(fmd_name , fmd_value + u'\x27'), 
    print(finc_name , finc_value + u'\xb0'), 
    print(fazm_name , fazm_value + u'\xb0'), 
    print(ftvd_name , ftvd_value + u'\x27'), 
    print(fvs_name , fvs_value + u'\x27'), 
    print(fgam_name , fgam_value +' API'))



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

fromaddr = "bijan.borazjani@gmail.com"
toaddr = "bijan.borazjani@gmail.com"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = Subject


body = Comp

msg.attach(MIMEText(body, 'plain'))

filename = "Capture.png"
attachment = open("c:\\users\\Bijan\\Desktop\\Capture.PNG", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "ragincajuns")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
