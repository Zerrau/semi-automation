# !/usr/bin/python
# -*- coding: utf-8 -*-
import random

from mysql import connector

HOST = '192.168.0.3'
DB = 'p17_testspb'
PORT = '3306'
USER = 'dbuser'
PASSWORD = 'dbpassword'

db = connector.connect(host=HOST, user=USER, passwd=PASSWORD, database=DB, port=PORT)
db_cursor = db.cursor()

policy_num = random.randint(1000000000000, 9999999999999)
contact_num = random.randint(89900000000, 89999999999)
snils_num = random.randint(00000000000, 99999999999)


def get_stmt(stmt):
    db_cursor.execute(stmt)
    db.commit()
    return db_cursor.lastrowid


def get_client_id():
    add_client_stmt = u"""
    INSERT INTO Client(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, 
                       `lastName`, `firstName`, `patrName`,
                        `birthDate`, `birthTime`, `sex`, `SNILS`, `bloodNotes`, `growth`, `weight`,
                       `embryonalPeriodWeek`, `birthPlace`, `diagNames`, `chartBeginDate`, `notes`, `IIN`, 
                       `isUnconscious`, `chronicalMKB`)
    VALUES ('2020-02-12T18:29:40', 614, '2020-02-12T18:29:40', 614, 'Тест', 'Тест', 'Тест', '1999-07-25', '00:00:00',
            1, '{snils_num}', '', '0', '0', '0', '', '', '2020-02-12', '', '', 0, '')""".format(snils_num=snils_num)
    result = get_stmt(add_client_stmt)
    return result


def add_client_policy(client_id):
    client_policy_stmt = u"""
    INSERT INTO ClientPolicy(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                             `client_id`, `insurer_id`, `policyType_id`, `policyKind_id`, `serial`, `number`, `begDate`,
                             `endDate`, `name`, `note`, `insuranceArea`)
    VALUES ('2020-02-17T11:09:42', 877, '2020-02-17T11:09:42', 877, 0, {client_id}, 3307, 1, 3, 'ЕП', 
    '6124156121456124', '2020-02-17', '2200-01-01', 'РОСНО', 'СПБ', '{policy_num}')""".format(client_id=client_id,
                                                                                              policy_num=policy_num)
    result = get_stmt(client_policy_stmt)
    return result


def add_client_contract(client_id):
    client_contact_stmt = u"""
    INSERT INTO ClientContact(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `deleted`,
                              `client_id`, `contactType_id`, `isPrimary`, `contact`,`notes`)
    VALUES ('2020-02-17T11:09:42', 877, '2020-02-17T11:09:42', 877, 0, {client_id}, 3, 1, '{contact_num}','')
    """.format(client_id=client_id, contact_num=contact_num)
    result = get_stmt(client_contact_stmt)
    return result


def add_client_address(client_id, address_id):
    client_address_stmt = u"""
    INSERT INTO ClientAddress(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `client_id`, 
    `type`, `address_id`, `district_id`, `isVillager`,`freeInput`)
    VALUES ('2020-02-17T11:28:00', 614, '2020-02-17T11:28:00', 614, {client_id}, 0, {address_id}, 1, 0,'')
    """.format(client_id=client_id, address_id=address_id)
    result = get_stmt(client_address_stmt)
    return result


def get_address_house_id():
    address_house_stmt = u"""
    INSERT INTO AddressHouse(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `KLADRCode`,
                             `KLADRStreetCode`, `number`, `corpus`)
    VALUES ('2020-02-17T11:28:00', 614, '2020-02-17T11:28:00', 614, '7800000000000', '78000000000241800', '1', '1')"""
    result = get_stmt(address_house_stmt)
    return result


def get_address_id(address_house_id):
    add_address_stmt = u"""
    INSERT INTO Address(`createDatetime`, `createPerson_id`, `modifyDatetime`, `modifyPerson_id`, `house_id`, `flat`)
    VALUES ('2020-02-17T11:28:00', 614, '2020-02-17T11:28:00', 614, {address_house_id}, '1')
    """.format(address_house_id=address_house_id)
    result = get_stmt(add_address_stmt)
    return result


# def checkSNILSEntered(self):
#     SNILS = unformatSNILS(forceStringEx(self.edtSNILS.text()))
#     if SNILS:
#         if len(SNILS) != 11:
#             self.checkInputMessage(u'CНИЛС', True, self.edtSNILS)
#             return False
#         elif not checkSNILS(SNILS):
#             fixedSNILS = formatSNILS(fixSNILS(SNILS))
#             res = QtGui.QMessageBox.question(self,
#                                              u'Внимание!',
#                                              u'СНИЛС указан с ошибкой.\nПравильный СНИЛС %s\nИсправить?' % fixedSNILS,
#                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
#                                              QtGui.QMessageBox.Yes)
#             if res == QtGui.QMessageBox.Yes:
#                 self.edtSNILS.setText(fixedSNILS)
#             else:
#                 self.edtSNILS.setFocus(QtCore.Qt.ShortcutFocusReason)
#                 return False
#     return True


client_id = get_client_id()
client_policy = add_client_policy(client_id)
client_contract = add_client_contract(client_id)
address_house_id = get_address_house_id()
address_id = get_address_id(address_house_id)
client_address = add_client_address(client_id, address_id)
printed_client = u'Client_id = {client_id}'.format(client_id=client_id)
print(printed_client)
