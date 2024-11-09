class Product:
    def __init__(self, name, manufacturer, weight, salePrice, purchasePrice,discountPercentage, imageData, voluminosity, combinations,
                nutritionalInformation, expirationDate, storageConditions, availableQuantity, numberSold, dateAddedToStock, totalProfitOnSales):
        self.name = name
        self.manufacturer = manufacturer
        self.weight = weight
        self.salePrice = salePrice
        self.purchasePrice = purchasePrice
        self.discountPercentage = discountPercentage
        self.imageData = imageData
        self.voluminosity = voluminosity
        self.combinations = combinations
        self.nutritionalInformation = nutritionalInformation
        self.expirationDate = expirationDate
        self.storageConditions = storageConditions
        self.availableQuantity = availableQuantity
        self.numberSold = numberSold
        self.dateAddedToStock = dateAddedToStock
        self.totalProfitOnSales = totalProfitOnSales

    #this function is for add new products to data base
    def insertProduct():
        pass
        
    #this function made for returning sale price by adding the discount to it
    def returningSalePrice(self):
        return self.salePrice - (self.salePrice * (self.discountPercentage / 100))
        
    #this function making updates to any product we want to 
    def updateProperteis():
        pass
    
    #this is for sending Allert ti admin if any product is going to be expierd
    def expirationDateAllert():
        pass
    
    # this function making taking photos easier for admin 
    def addImagesForDataset():
        pass
    # this is returning all available quantity for product
    def inventory(self):
        return self.availableQuantity
    
    
    
    