# !/usr/bin/python
# -*- coding: utf-8 -*-
# Version: 2.0
import random

from mysql import connector

# SETTINGS
HOST = '192.168.0.3'
DB = 'ptd5_1110'
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
snils_num = random.randint(00000000000, 99999999999)
rand_house = random.randint(1, 200)
rand_yer = random.randint(1970, 1999)
rand_mon = random.randint(1, 12)
rand_day = random.randint(1, 28)

# PATIENT DATA:
lastName = u'Васильев'
firstName = u'Василий'
patrName = u'Васильевич'


# FUNCTIONS:
def get_stmt(stmt):
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
        result += (9-i)*int(SNILS[i])
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
    return (raw+'0'*11)[:9] + calcSNILSCheckCode(raw)


def checkSNILSEntered(SNILS):
    check = checkSNILS(SNILS)
    if check:
        return SNILS
    else:
        return fixSNILS(SNILS)


def get_rand_date():
    rand_date = '{yer}-{mon}-{day}'.format(yer=rand_yer, mon=rand_mon, day=rand_day)
    return rand_date


def get_client_id():
    snils = checkSNILSEntered(snils_num)
    birthDate = get_rand_date()
    add_client_stmt = u"""
INSERT INTO Client(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, 
                   `lastName`, `firstName`, `patrName`,
                    `birthDate`, `birthTime`, `sex`, `SNILS`, `bloodNotes`, `growth`, `weight`,
                   `embryonalPeriodWeek`, `birthPlace`, `diagNames`, `chartBeginDate`, `notes`, 
                   `IIN`, `isUnconscious`, `chronicalMKB`)
VALUES ('2020-02-12T18:29:40', 1, '2020-02-12T18:29:40', 1, 
        '{lastName}', '{firstName}', '{patrName}', 
        '{birthDate}', '00:00:00', 1, '{snils}', '', '0', '0', 
        '0', 'СПБ', '', '2020-02-12', '', 
        '', 0, '')""".format(lastName=lastName, firstName=firstName, patrName=patrName,
                             birthDate=birthDate, snils=snils)
    result = get_stmt(add_client_stmt)
    return result


def add_client_policy(client_id):
    client_policy_stmt = u"""
INSERT INTO ClientPolicy(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                         `client_id`, `insurer_id`, `policyType_id`, `policyKind_id`, `serial`, `number`, `begDate`,
                         `endDate`, `name`, `note`, `insuranceArea`)
VALUES ('2020-02-17T11:09:42', 1, '2020-02-17T11:09:42', 1, 0, {client_id}, 3307, 1, 3, 'ЕП', 
'{policy_num}', '2020-02-17', '2200-01-01', 'РОСНО', 'СПБ', '7800000000000')""".format(
        client_id=client_id, policy_num=policy_num)
    result = get_stmt(client_policy_stmt)
    return result


def add_client_contract(client_id):
    client_contact_stmt = u"""
INSERT INTO ClientContact(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                          `client_id`, `contactType_id`, `isPrimary`, `contact`,`notes`)
VALUES ('2020-02-17T11:09:42', 1, '2020-02-17T11:09:42', 1, 0, 
        {client_id}, 3, 1, '{contact_num}','mobile')""".format(
        client_id=client_id, contact_num=contact_num)
    result = get_stmt(client_contact_stmt)
    return result


def add_client_address(client_id, address_id):
    client_address_stmt = u"""
INSERT INTO ClientAddress(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `client_id`, 
`type`, `address_id`, `district_id`, `isVillager`,`freeInput`)
VALUES ('2020-02-17T11:28:00', 1, '2020-02-17T11:28:00', 1, {client_id}, 0, {address_id}, 1, 0,'')""".format(
        client_id=client_id, address_id=address_id)
    result = get_stmt(client_address_stmt)
    return result


def get_address_house_id():
    address_house_stmt = u"""
INSERT INTO AddressHouse(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `KLADRCode`,
                         `KLADRStreetCode`, `number`, `corpus`)
VALUES ('2020-02-17T11:28:00', 1, '2020-02-17T11:28:00', 1, '7800000000000', 
        '78000000000227000', '{number}', '1')""".format(number=rand_house)
    result = get_stmt(address_house_stmt)
    return result


def get_address_id(address_house_id):
    add_address_stmt = u"""
INSERT INTO Address(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `house_id`, `flat`)
VALUES ('2020-02-17T11:28:00', 1, '2020-02-17T11:28:00', 1, {address_house_id}, '1')""".format(
        address_house_id=address_house_id)
    result = get_stmt(add_address_stmt)
    return result


def add_event(client_id):
    add_event_stmt = u"""
INSERT INTO Event (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, deleted, externalId, eventType_id, 
org_id, client_id, setDate, isPrimary, `order`, payStatus, note, pregnancyWeek, totalCost)
VALUES (NOW(), 1, NOW(), 1, 0, '', 2, 1, {client_id}, DATE(NOW()), 1, 1, 0, 'note', 0, 0.0)
    """.format(client_id=client_id)
    result = get_stmt(add_event_stmt)
    return result


# MAGIC:
client_id = get_client_id()
client_policy = add_client_policy(client_id)
client_contract = add_client_contract(client_id)
address_house_id = get_address_house_id()
address_id = get_address_id(address_house_id)
client_address = add_client_address(client_id, address_id)
event_id = add_event(client_id)
printed_client = u'Client.id = {client_id}'.format(client_id=client_id)
printed_event = u'Event.id = {event_id}'.format(event_id=event_id)
print(printed_client)
print(printed_event)
