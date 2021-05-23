#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Marco'
import json
from config import Cfg
import psycopg2
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return "%s" % o
        super(DecimalEncoder, self).default(o)


def get_actions(network_id, account_id):
    """
    get data from indexer
    """
    conn = psycopg2.connect(
        database=Cfg.NETWORK[network_id]["INDEXER_DSN"],
        user=Cfg.NETWORK[network_id]["INDEXER_UID"],
        password=Cfg.NETWORK[network_id]["INDEXER_PWD"],
        host=Cfg.NETWORK[network_id]["INDEXER_HOST"],
        port=Cfg.NETWORK[network_id]["INDEXER_PORT"])
    cur=conn.cursor() 

    sql1 = (
        "select " 
        "included_in_block_timestamp as timestamp, " 
        "args->>'method_name' as method_name, " 
        "convert_from(decode(args->>'args_base64', 'base64'), 'UTF8')::json as args, " 
        "args->>'deposit' as deposit " 
        "from action_receipt_actions join receipts using(receipt_id) " 
    )
    sql2 = "where (action_kind = 'FUNCTION_CALL' and receiver_account_id = '%s' " % Cfg.NETWORK[network_id]["REF_CONTRACT"]
    sql3 = "and predecessor_account_id = '%s') order by timestamp desc limit 10" % account_id 
    sql = "%s %s %s" % (sql1, sql2, sql3)

    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()

    json_ret = json.dumps(rows, cls=DecimalEncoder)
    return json_ret
    

if __name__ == '__main__':
    print("#########MAINNET###########")
    print(get_actions("MAINNET", "reffer.near"))
    print("#########TESTNET###########")
    print(get_actions("TESTNET", "pika8.testnet"))
