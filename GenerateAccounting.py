#!/usr/bin/env python3
import csv
import math
import os

STOCK_FILE = "stock.csv"
ORDERS_FILE = "orders.csv"
ITEM_SALES_FILE = "item_sales.csv"
ORDER_SALES_FILE = "order_sales.csv"

def getPath(fileName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)

def readFromFile(fileName):
    data = []
    with open(getPath(fileName), newline='') as dataFile:
        data = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(dataFile, skipinitialspace=True)]
    return data

def getStockEntry(field, sku, stock):
    for stockItem in stock:
        if stockItem['Store Code (SKU)'] == sku:
            return stockItem[field]
    return "NOT_FOUND"

def toFloat(value):
    if (value == ''): value = 0
    return float(value)

def printFloat(value):
    return "{:.2f}".format(toFloat(value))

def printYesNo(value):
    return "Yes" if value else "NO!!!"

def writeItemSales(orders, stock):
    ITEM_FIELDS = ["Time", "Name", "Department", "Price (Stock)", "Price (eCommerce)", "Prices Equal?", "Tax Details", "Cost"]
    with open(getPath(ITEM_SALES_FILE), "w", newline='') as itemSalesFile:
        itemSalesWriter = csv.DictWriter(itemSalesFile, fieldnames = ITEM_FIELDS)
        itemSalesWriter.writeheader()
        for orderItem in orders:
            itemSku = orderItem['sku'].strip('"')
            stockPrice = toFloat(getStockEntry('Price', itemSku, stock))
            itemPrice = toFloat(orderItem['total'])
            arePricesEqual = math.isclose(stockPrice, itemPrice, rel_tol=1e-3)
            itemSalesWriter.writerow({ \
                'Time': orderItem['timestamp'], \
                'Name': orderItem['name'], \
                'Department': getStockEntry('Department', itemSku, stock), \
                'Price (Stock)': printFloat(getStockEntry('Price', itemSku, stock)), \
                'Price (eCommerce)': printFloat(orderItem['total']), \
                'Prices Equal?': printYesNo(arePricesEqual), \
                'Tax Details': orderItem['tax_details'], \
                'Cost': printFloat(getStockEntry('Cost', itemSku, stock)), \
            })

def writeOrderSales(orders, stock):
    ORDER_FIELDS = ["Order Number", "Time", "Name", "Subtotal", "Discount", "Tax", "Reported Total", "Expected Total", "Totals Equal?"]
    with open(getPath(ORDER_SALES_FILE), "w", newline='') as orderSalesFile:
        orderSalesWriter = csv.DictWriter(orderSalesFile, fieldnames = ORDER_FIELDS)
        orderSalesWriter.writeheader()
        previousOrderNumber = -1
        for orderItem in orders:
            if orderItem['order_number'] == previousOrderNumber:
                continue #Skip orders already accounted for
            previousOrderNumber = orderItem['order_number']
            expectedTotal = toFloat(orderItem['order_subtotal']) - toFloat(orderItem['discount']) + toFloat(orderItem['order_tax'])
            areTotalsEqual = math.isclose(expectedTotal, toFloat(orderItem['order_total']), rel_tol=1e-3)
            orderSalesWriter.writerow({ \
                'Order Number': orderItem['order_number'], \
                'Time': orderItem['timestamp'], \
                'Name': orderItem['shipto_person_name'], \
                'Subtotal': printFloat(orderItem['order_subtotal']), \
                'Discount': printFloat("-"+orderItem['discount']), \
                'Tax': printFloat(orderItem['order_tax']), \
                'Reported Total': printFloat(orderItem['order_total']), \
                'Expected Total': printFloat(expectedTotal), \
                'Totals Equal?': printYesNo(areTotalsEqual), \
            })

try:
    print("Reading " + ORDERS_FILE + "...")
    orders = readFromFile(ORDERS_FILE)
    print("Reading " + STOCK_FILE + "...")
    stock = readFromFile(STOCK_FILE)
    print("Writing " + ITEM_SALES_FILE + "...")
    writeItemSales(orders, stock)
    print("Writing " + ORDER_SALES_FILE + "...")
    writeOrderSales(orders, stock)
    print("Files written successfully!")
except Exception as e:
    print(e)
input("Press Enter to exit...")
