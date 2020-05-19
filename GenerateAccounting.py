#!/usr/bin/env python3
import csv
import os

STOCK_FILE = "stock.csv"
ORDERS_FILE = "orders.csv"
ITEM_SALES_FILE = "item_sales.csv"
ORDER_SALES_FILE = "order_sales.csv"
ITEM_FIELDS = ["Time", "Name", "Department", "Price (Stock)", "Price (eCommerce)", "Discount", "Order Tax", "Tax Details", "Cost"]
ORDER_FIELDS = ["Order Number", "Time", "Name", "Subtotal", "Total", "3.5% of Total"]

def getPath(fileName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)

def getStockEntry(field, sku):
    for stockItem in _stock:
        if stockItem['Store Code (SKU)'] == sku:
            return stockItem[field]
    return "NOT_FOUND"

def format(value):
    if (value == ''): value = 0
    return "{:.2f}".format(float(value))

def readOrdersAndStock():
    global _orders, _stock
    print("Reading " + ORDERS_FILE + "...")
    with open(getPath(ORDERS_FILE), newline='') as ordersFile:
        _orders = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(ordersFile, skipinitialspace=True)]
    print("Reading " + STOCK_FILE + "...")
    with open(getPath(STOCK_FILE), newline='') as stockFile:
        _stock = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(stockFile, skipinitialspace=True)]

def writeItemSales():
    print("Writing " + ITEM_SALES_FILE + "...")
    with open(getPath(ITEM_SALES_FILE), "w", newline='') as itemSalesFile:
        itemSalesWriter = csv.DictWriter(itemSalesFile, fieldnames = ITEM_FIELDS)
        itemSalesWriter.writeheader()
        for orderItem in _orders:
            itemSku = orderItem['sku'].strip('"')
            itemSalesWriter.writerow({ \
                'Time': orderItem['timestamp'], \
                'Name': orderItem['name'], \
                'Department': getStockEntry('Department', itemSku), \
                'Price (Stock)': format(getStockEntry('Price', itemSku)), \
                'Price (eCommerce)': format(orderItem['total']), \
                'Discount': format(orderItem['discount']), \
                'Order Tax': format(orderItem['order_tax']), \
                'Tax Details': format(orderItem['tax_details']), \
                'Cost': format(getStockEntry('Cost', itemSku)), \
            })

def writeOrderSales():
    print("Writing " + ORDER_SALES_FILE + "...")
    with open(getPath(ORDER_SALES_FILE), "w", newline='') as orderSalesFile:
        orderSalesWriter = csv.DictWriter(orderSalesFile, fieldnames = ORDER_FIELDS)
        orderSalesWriter.writeheader()
        previousOrderNumber = -1
        for orderItem in _orders:
            if orderItem['order_number'] == previousOrderNumber:
                continue #Skip orders already accounted for
            previousOrderNumber = orderItem['order_number']
            orderSalesWriter.writerow({ \
                'Order Number': orderItem['order_number'], \
                'Time': orderItem['timestamp'], \
                'Name': orderItem['shipto_person_name'], \
                'Subtotal': format(orderItem['order_subtotal']), \
                'Total': format(orderItem['order_total']), \
                '3.5% of Total': format(float(orderItem['order_total']) * 0.035), \
            })

try:
    readOrdersAndStock()
    writeItemSales()
    writeOrderSales()
    print("Files written successfully!")
except Exception as e:
    print(e)
input("Press Enter to exit...")
