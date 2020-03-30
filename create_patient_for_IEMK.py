# !/usr/bin/python
# -*- coding: utf-8 -*-
# Version: 3.0
import random

from mysql import connector

# SETTINGS
HOST = '192.168.0.204'  # pacs
DB = 's12'
PORT = '3306'
USER = 'dbuser'
PASSWORD = 'dbpassword'

# DATA-BASE SETTINGS
db = connector.connect(host=HOST, user=USER, passwd=PASSWORD, database=DB, port=PORT)
db_cursor = db.cursor()
DB_DEBUG = True

# RANDOM DATA:
policy_num = random.randint(1000000000000000, 9999999999999999)
contact_num = random.randint(89900000000, 89999999999)
snils_num = random.randint(10000000000, 99999999999)
rand_pas_num = random.randint(100000, 999999)
rand_house = random.randint(1, 200)
rand_yer = random.randint(1970, 1999)
rand_mon = random.randint(1, 12)
rand_day = random.randint(1, 28)

# PATIENT DATA:
lastName = u'Тест'
firstName = u'Тест'
patrName = u'Тест'
policy_type_name = u'ОМС'  # ОМС/ДМС
diagnosis_mkb = u'D00.0'


# FUNCTIONS:
def select_stmt(stmt):
    if DB_DEBUG:
        print stmt
    db_cursor.execute(stmt)
    fetch_all = db_cursor.fetchall()
    return list(i for i in fetch_all)


def insert_stmt(stmt):
    if DB_DEBUG:
        print stmt
    db_cursor.execute(stmt)
    db.commit()
    return db_cursor.lastrowid


def unformatSNILS(SNILS):
    return str(SNILS).replace('-', '').replace(' ', '')


def calcSNILSCheckCode(SNILS):
    result = 0
    for i in xrange(9):
        result += (9 - i) * int(SNILS[i])
    result = result % 101
    if result == 100:
        result = 0
    return '%02.2d' % result


def checkSNILS(SNILS):
    raw = unformatSNILS(SNILS)
    if len(raw) == 11:
        return raw[:9] <= '001001998' or raw[-2:] == calcSNILSCheckCode(raw)
    return False


def fixSNILS(SNILS):
    raw = unformatSNILS(SNILS)
    return (raw + '0' * 11)[:9] + calcSNILSCheckCode(raw)


def checkSNILSEntered(SNILS):
    check = checkSNILS(SNILS)
    if check:
        return SNILS
    else:
        return fixSNILS(SNILS)


def get_rand_date():
    rand_date = '{yer}-{mon}-{day}'.format(yer=rand_yer, mon=rand_mon, day=rand_day)
    return rand_date


def get_rand_serial():
    first_serial = random.randint(19, 99)
    second_serial = random.randint(10, 99)
    serial = u'{f} {s}'.format(f=first_serial, s=second_serial)
    return serial


def set_person_id():
    personIdStmt = u"""
SELECT id
FROM Person where lastName like '%админ%' or lastName like '%виста%' AND org_id IS NOT NULL
LIMIT 1"""
    result = select_stmt(personIdStmt)
    return result[0][0]


def get_client_id():
    person_id = set_person_id()
    snils = checkSNILSEntered(snils_num)
    birthDate = get_rand_date()
    add_client_stmt = u"""
INSERT INTO Client(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, 
                   `lastName`, `firstName`, `patrName`,
                    `birthDate`, `birthTime`, `sex`, `SNILS`, `bloodNotes`, `growth`, `weight`,
                   `embryonalPeriodWeek`, `birthPlace`, `diagNames`, `chartBeginDate`, `notes`, 
                   `IIN`, `isUnconscious`, `chronicalMKB`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, 
        '{lastName}', '{firstName}', '{patrName}', 
        '{birthDate}', '00:00:00', 1, '{snils}', '', '0', '0', 
        '0', 'СПБ', '', '2020-02-12', '', 
        '', 0, '')""".format(lastName=lastName, firstName=firstName, patrName=patrName,
                             birthDate=birthDate, snils=snils, person_id=person_id)
    result = insert_stmt(add_client_stmt)
    return result


def get_document_type():
    document_type_stmt = u"""
SELECT rbDocumentType.id 
FROM rbDocumentType 
WHERE rbDocumentType.name LIKE '%паспорт%'
ORDER BY id
LIMIT 1"""
    result = select_stmt(document_type_stmt)
    return result[0][0]


def get_client_document(client_id):
    person_id = set_person_id()
    document_type = get_document_type()
    serial = get_rand_serial()
    number = rand_pas_num
    date = get_rand_date()
    add_document_stmt = u"""
INSERT INTO ClientDocument(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`, 
`client_id`, `documentType_id`, `serial`, `number`, `date`, `origin`) 
VALUES (NOW(), {person_id}, NOW(), {person_id}, 0, 
{client_id}, {document_type}, '{serial}', '{number}', '{date}', 'УФМС России')""".format(
        client_id=client_id, document_type=document_type, serial=serial, number=number, date=date, person_id=person_id)
    result = insert_stmt(add_document_stmt)
    return result


def get_format_policy():
    policyTypeStmt = u"""
SELECT id
FROM rbPolicyType
WHERE rbPolicyType.name LIKE '%{policy_type_name}%'
ORDER BY id
LIMIT 1""".format(policy_type_name=policy_type_name)
    result = select_stmt(policyTypeStmt)
    return result[0][0]


def add_client_policy(client_id):
    person_id = set_person_id()
    policyType = get_format_policy()
    client_policy_stmt = u"""
INSERT INTO ClientPolicy(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                         `client_id`, `insurer_id`, policyType_id, `policyKind_id`, `serial`, `number`, `begDate`,
                         `endDate`, `name`, `note`, `insuranceArea`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, 0, {client_id}, 3307, {policyType}, 3, 'ЕП', 
'{policy_num}', '2020-02-17', '2200-01-01', 'РОСНО', 'СПБ', '7800000000000')""".format(
        client_id=client_id, policy_num=policy_num, policyType=policyType, person_id=person_id)
    result = insert_stmt(client_policy_stmt)
    return result


def add_client_contact(client_id):
    person_id = set_person_id()
    client_contact_stmt = u"""
INSERT INTO ClientContact(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                          `client_id`, `contactType_id`, `isPrimary`, `contact`,`notes`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, 0, 
        {client_id}, 3, 1, '{contact_num}','mobile')""".format(
        client_id=client_id, contact_num=contact_num, person_id=person_id)
    result = insert_stmt(client_contact_stmt)
    return result


def add_client_address(client_id, address_id):
    person_id = set_person_id()
    client_address_stmt = u"""
INSERT INTO ClientAddress(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `client_id`, 
`type`, `address_id`, `district_id`, `isVillager`,`freeInput`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, {client_id}, 0, {address_id}, 1, 0,'')""".format(
        client_id=client_id, address_id=address_id, person_id=person_id)
    result = insert_stmt(client_address_stmt)
    return result


def get_address_house_id():
    person_id = set_person_id()
    address_house_stmt = u"""
INSERT INTO AddressHouse(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `KLADRCode`,
                         `KLADRStreetCode`, `number`, `corpus`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, '7800000000000', 
        '78000000000227000', '{number}', '1')""".format(number=rand_house, person_id=person_id)
    result = insert_stmt(address_house_stmt)
    return result


def get_address_id(address_house_id):
    person_id = set_person_id()
    add_address_stmt = u"""
INSERT INTO Address(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `house_id`, `flat`)
VALUES (NOW(), {person_id}, NOW(), {person_id}, {address_house_id}, '1')""".format(
        address_house_id=address_house_id, person_id=person_id)
    result = insert_stmt(add_address_stmt)
    return result


def get_person_org():
    org_stmt = u"""
SELECT org_id 
FROM Person 
WHERE (lastName LIKE '%админ%' OR lastName LIKE '%виста%') AND org_id IS NOT NULL 
LIMIT 1"""
    result = select_stmt(org_stmt)
    return result[0][0]


def get_eventType():
    eventType = u"""
SELECT id
FROM EventType
WHERE name LIKE '%Лечебно-диагностический%'
ORDER BY id
LIMIT 1"""
    result = select_stmt(eventType)
    return result[0][0]


def add_event(client_id):
    person_id = set_person_id()
    org_id = get_person_org()
    eventType = get_eventType()
    add_event_stmt = u"""
INSERT INTO Event (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, deleted, externalId, eventType_id, 
org_id, client_id, setDate, isPrimary, `order`, payStatus, note, pregnancyWeek, totalCost)
VALUES (NOW(), {person_id}, NOW(), {person_id}, 0, '', {eventType}, 
{org_id}, {client_id}, DATE(NOW()), 1, 1, 0, 'note', 0, 0.0)""".format(
        eventType=eventType, org_id=org_id, client_id=client_id, person_id=person_id)
    result = insert_stmt(add_event_stmt)
    return result


def add_diagnosis(client_id):
    person_id = set_person_id()
    diagnosis_stmt = u"""
INSERT INTO Diagnosis(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, 
`client_id`, `diagnosisType_id`, `character_id`, `MKB`, `MKBEx`, `endDate`, `person_id`) 
VALUES (NOW(), {person_id}, NOW(), {person_id}, 
{client_id}, 2, 3, '{diagnosis_mkb}', '', DATE(NOW()), {person_id})""".format(
        client_id=client_id, diagnosis_mkb=diagnosis_mkb, person_id=person_id)
    result = insert_stmt(diagnosis_stmt)
    return result


def add_diagnostic(event_id, diagnosis_id):
    person_id = set_person_id()
    diagnostic_stmt = u"""
INSERT INTO Diagnostic(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`, 
`event_id`, `diagnosis_id`, `TNMS`, `diagnosisType_id`, `character_id`, `person_id`, `result_id`, `setDate`, `endDate`) 
VALUES (NOW(), {person_id}, NOW(), {person_id}, 0, 
{event_id}, {diagnosis_id}, '', 2, 3, {person_id}, 22, DATE(NOW()), DATE(NOW()))""".format(
        event_id=event_id, diagnosis_id=diagnosis_id, person_id=person_id)
    result = insert_stmt(diagnostic_stmt)
    return result


# MAGIC:
client_id = get_client_id()
client_document = get_client_document(client_id)
client_policy = add_client_policy(client_id)
client_contact = add_client_contact(client_id)
address_house_id = get_address_house_id()
address_id = get_address_id(address_house_id)
client_address = add_client_address(client_id, address_id)
event_id = add_event(client_id)
diagnosis_id = add_diagnosis(client_id)
diagnostic_id = add_diagnostic(event_id, diagnosis_id)
printed_client = u'Client.id = {client_id}'.format(client_id=client_id)
printed_event = u'Event.id = {event_id}'.format(event_id=event_id)
print(u'-----')
print(printed_client)
print(printed_event)
