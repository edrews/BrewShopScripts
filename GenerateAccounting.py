#!/usr/bin/env python3
'''
1.3.0
- Customize sales-by-item.csv to add:
  - eCommerce quantity sold for each item
  - Total quantity sold
  - Append items if they don't already exist
- Use input folders instead of single input CSV's
- Tolerate not finding order items in stock file
1.2.0
- Searching stock entries now by both Name *and* SKU since neither is sufficient on its own
1.1.1
- Including quantity in COGS calculation
1.1.0
- Better error reporting for missing SKUs
- Changed order name to email since it's always there
- Added support for order delivery fee
- Multiplying stock price by item quantity when comparing totals
1.0.0
- Initial Shopkeep accounting script
'''

import csv
import math
import os

STOCK_FOLDER = "stock"
ORDERS_FOLDER = "orders"
SALES_BY_ITEM_FOLDER = "sales-by-item"
ITEM_SALES_FILE = "out-item-sales.csv"
ORDER_SALES_FILE = "out-order-sales.csv"
TOTAL_SALES_FILE = "out-total-sales-by-item.csv"

def getPath(fileName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)

def readFromFile(fileName):
    data = []
    with open(getPath(fileName), newline='') as dataFile:
        data = [{k: str(v) for k, v in row.items()}
            for row in csv.DictReader(dataFile, skipinitialspace=True)]
    return data

def readFromFolder(folderName):
    allData = []
    folderPath = getPath(folderName)
    for fileName in os.listdir(folderPath):
        filePath = os.path.join(folderPath, fileName)
        with open(filePath, newline='') as dataFile:
            data = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(dataFile, skipinitialspace=True)]
        allData.extend(data)
    return allData

def getStockEntry(field, itemSku, itemName, stock):
    for stockItem in stock:
        if stockItem['Name'].strip() == itemName.strip() or stockItem['Store Code (SKU)'] == itemSku:
            return stockItem[field]
    raise Exception("Neither \"" + itemName + "\" or its SKU \"" + itemSku + "\" was not found in the stock CSV files")

def getOrderQuantityOfItem(itemName, orders):
    itemCount = 0
    for orderItem in orders:
        if orderItem['name'].strip() == itemName.strip():
            itemCount += toFloat(orderItem['quantity'])
    return itemCount

def getQuantityOfAllOrderItems(orders):
    itemCount = 0
    for orderItem in orders:
        itemCount += toFloat(orderItem['quantity'])
    return itemCount

def toFloat(value):
    if (value == ''): value = 0
    return float(value)

def printFloat(value):
    return "{:.2f}".format(toFloat(value))

def printYesNo(value):
    return "Yes" if value else "NO!!!"

def writeItemSold(orderItem, stock, itemSalesWriter):
    itemSku = orderItem['sku'].strip('"')
    itemName = orderItem['name']
    try:
        stockPrice = toFloat(getStockEntry('Price', itemSku, itemName, stock))
        itemCost = toFloat(getStockEntry('Cost', itemSku, itemName, stock))
        department = getStockEntry('Department', itemSku, itemName, stock)
    except Exception as e:
        print(e)
        stockPrice = 0
        itemCost = 0
        department = "NOT_AVAILABLE"
    itemQuantity = toFloat(orderItem['quantity'])
    reportedTotal = toFloat(orderItem['total'])
    arePricesEqual = math.isclose(stockPrice * itemQuantity, reportedTotal, abs_tol=0.001)
    itemSalesWriter.writerow({ \
        'Time': orderItem['timestamp'], \
        'Name': itemName, \
        'Department': department, \
        'Price (Stock)': printFloat(stockPrice), \
        'Quantity': printFloat(itemQuantity), \
        'Total Expected': printFloat(stockPrice * itemQuantity), \
        'Total Reported (eCommerce)': printFloat(orderItem['total']), \
        'Totals Equal?': printYesNo(arePricesEqual), \
        'Tax Details': orderItem['tax_details'], \
        'Item Cost': printFloat(itemCost), \
        'Total Cost': printFloat(itemCost * itemQuantity), \
    })

def writeItemsSold(orders, stock):
    ITEM_FIELDS = ["Time", "Name", "Department", "Price (Stock)", "Quantity", "Total Expected", "Total Reported (eCommerce)", "Totals Equal?", "Tax Details", "Item Cost", "Total Cost"]
    with open(getPath(ITEM_SALES_FILE), "w", newline='') as itemSalesFile:
        itemSalesWriter = csv.DictWriter(itemSalesFile, fieldnames = ITEM_FIELDS)
        itemSalesWriter.writeheader()
        for orderItem in orders:
            writeItemSold(orderItem, stock, itemSalesWriter)

def writeOrder(order, orderSalesWriter):
    expectedTotal = toFloat(order['order_subtotal']) + toFloat(order['order_shipping']) - toFloat(order['discount']) + toFloat(order['order_tax'])
    areTotalsEqual = math.isclose(expectedTotal, toFloat(order['order_total']), abs_tol=0.001)
    orderSalesWriter.writerow({ \
        'Order Number': order['order_number'], \
        'Time': order['timestamp'], \
        'Email': order['email'], \
        'Subtotal': printFloat(order['order_subtotal']), \
        'Delivery Fee': printFloat(order['order_shipping']), \
        'Discount': printFloat("-"+order['discount']), \
        'Tax': printFloat(order['order_tax']), \
        'Expected Total': printFloat(expectedTotal), \
        'Reported Total': printFloat(order['order_total']), \
        'Totals Equal?': printYesNo(areTotalsEqual), \
    })

def writeOrders(orders, stock):
    ORDER_FIELDS = ["Order Number", "Time", "Email", "Subtotal", "Delivery Fee", "Discount", "Tax", "Expected Total", "Reported Total", "Totals Equal?"]
    with open(getPath(ORDER_SALES_FILE), "w", newline='') as orderSalesFile:
        orderSalesWriter = csv.DictWriter(orderSalesFile, fieldnames = ORDER_FIELDS)
        orderSalesWriter.writeheader()
        previousOrderNumber = -1
        for order in orders:
            if order['order_number'] != previousOrderNumber: #Skip orders already accounted for
                writeOrder(order, orderSalesWriter) 
            previousOrderNumber = order['order_number']

def getSaleData(sale):
    quantity = toFloat(sale['Quantity Sold'])
    return { \
        'Name': sale['Item Description'], \
        'Department': sale['Department'], \
        'Category': sale['Category'], \
        'Register Quantity Sold': quantity, \
        'eCommerce Quantity Sold': 0, \
        'Total Quantity Sold': quantity, \
        'Quantity on Hand': sale['Quantity on Hand'], \
        'Supplier': sale['Supplier'], \
    }

def getOrderData(order, stock):
    quantity = toFloat(order['quantity'])
    orderSku = order['sku'].strip()
    orderName = order['name'].strip()
    try:
        department = getStockEntry('Department', orderSku, orderName, stock)
        category = getStockEntry('Category', orderSku, orderName, stock)
        onHand = getStockEntry('Quantity', orderSku, orderName, stock)
        supplier = getStockEntry('Supplier', orderSku, orderName, stock)
    except Exception as e:
        print(e)
        department = "NOT_AVAILABLE"
        category = "NOT_AVAILABLE"
        onHand = "NOT_AVAILABLE"
        supplier = "NOT_AVAILABLE"
    return { \
        'Name': orderName, \
        'Department': department, \
        'Category': category, \
        'Register Quantity Sold': 0, \
        'eCommerce Quantity Sold': quantity, \
        'Total Quantity Sold': quantity, \
        'Quantity on Hand': onHand, \
        'Supplier': supplier, \
    }

def addOrAppendOrder(order, stock, totalItemsSold):
    for item in totalItemsSold:
        if order['name'].strip() == item['Name'].strip():
            quantity = toFloat(order['quantity'])
            item['eCommerce Quantity Sold'] += quantity
            item['Total Quantity Sold'] += quantity
            return
    data = getOrderData(order, stock)
    totalItemsSold.append(data)

def addOrAppendSale(sale, totalItemsSold):
    for item in totalItemsSold:
        if sale['Item Description'].strip() == item['Name'].strip():
            quantity = toFloat(sale['Quantity Sold'])
            item['Register Quantity Sold'] += quantity
            item['Total Quantity Sold'] += quantity
            return
    data = getSaleData(sale)
    totalItemsSold.append(data)

def writeTotalItemsSold(sales, orders, stock):
    totalItemsSold = []
    for sale in sales:
        addOrAppendSale(sale, totalItemsSold)
    for order in orders:
        addOrAppendOrder(order, stock, totalItemsSold)
    FIELDS = ["Name", "Department", "Category", "Register Quantity Sold", "eCommerce Quantity Sold", "Total Quantity Sold", "Quantity on Hand", "Supplier"]
    with open(getPath(TOTAL_SALES_FILE), "w", newline='') as totalSalesFile:
        totalSalesWriter = csv.DictWriter(totalSalesFile, fieldnames = FIELDS)
        totalSalesWriter.writeheader()
        for item in totalItemsSold:
            totalSalesWriter.writerow(item)

def generateAccounting():
    try:
        print("Reading " + ORDERS_FOLDER + " folder...")
        orders = readFromFolder(ORDERS_FOLDER)
        print("Reading " + STOCK_FOLDER + " folder...")
        stock = readFromFolder(STOCK_FOLDER)
        print("Writing " + ORDER_SALES_FILE + "...")
        writeOrders(orders, stock)
        print("Writing " + ITEM_SALES_FILE + "...")
        writeItemsSold(orders, stock)
        if os.path.exists(getPath(SALES_BY_ITEM_FOLDER)):
            print("Reading " + SALES_BY_ITEM_FOLDER + " folder...")
            sales = readFromFolder(SALES_BY_ITEM_FOLDER)
            print("Writing " + TOTAL_SALES_FILE + "...")
            writeTotalItemsSold(sales, orders, stock)
        else:
            print("Skipping " + TOTAL_SALES_FILE + "...")
        print("All files written successfully!")
    except Exception as e:
        print("Error: " + e)
    input("Press Enter to exit...")

generateAccounting()
