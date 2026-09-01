import csv
import random
from datetime import datetime, timedelta

filename = 'medical_noshow.csv'
neighbourhoods = ['JARDIM DA PENHA', 'MATA DA PRAIA', 'BENTO FERREIRA', 'JESUS DE NAZARETH', 'MARUIPE', 'SANTA MARTHA', 'SANTO ANDRE']
genders = ['F', 'M']
yes_no = ['Yes', 'No']

base_date = datetime(2016, 5, 1)

with open(filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'PatientId', 'AppointmentID', 'Gender', 'ScheduledDay', 
        'AppointmentDay', 'Age', 'Neighbourhood', 'Scholarship', 
        'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 
        'SMS_received', 'No-show'
    ])
    
    for i in range(1, 1200):
        patient_id = random.randint(10000000, 99999999)
        appointment_id = 5000000 + i
        gender = random.choice(genders)
        sched_delta = random.randint(1, 20)
        appt_date = base_date + timedelta(days=random.randint(1, 30))
        sched_date = appt_date - timedelta(days=sched_delta)
        age = random.randint(0, 95)
        neighbourhood = random.choice(neighbourhoods)
        scholarship = 1 if random.random() < 0.15 else 0
        hipertension = 1 if (age > 45 and random.random() < 0.4) else 0
        diabetes = 1 if (age > 45 and random.random() < 0.2) else 0
        alcoholism = 1 if (age > 18 and random.random() < 0.08) else 0
        handcap = 1 if random.random() < 0.03 else 0
        sms = 1 if sched_delta > 3 and random.random() < 0.6 else 0
        
        # احتمالية عدم الحضور (No-show)
        no_show_prob = 0.25
        if sms == 1:
            no_show_prob -= 0.08
        if age < 20 or age > 65:
            no_show_prob -= 0.05
        if sched_delta > 10:
            no_show_prob += 0.10
            
        no_show = 'Yes' if random.random() < max(0.05, min(0.6, no_show_prob)) else 'No'
        
        writer.writerow([
            patient_id,
            appointment_id,
            gender,
            sched_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            appt_date.strftime('%Y-%m-%dT00:00:00Z'),
            age,
            neighbourhood,
            scholarship,
            hipertension,
            diabetes,
            alcoholism,
            handcap,
            sms,
            no_show
        ])

print("Created medical_noshow.csv successfully.")