import cv2
import os
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
    def addImagesForDataset(self):
        # Number of cameras
        cap = cv2.VideoCapture(0)

        # Send error if camera is unavaileble
        if not cap.isOpened():
            print("Unable to read camera feed!")

        output_dir = '\getting images'
        # os.makedirs(output_dir, exist_ok=True)
        image_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Webcam', frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:
                print("Escape hit, closing...") #break poin of while
                break
            elif k % 256 == ord('s'):   # wait for 's' key to save and exit
                img_name = os.path.join(output_dir, f"opencv_frame_{image_counter}.png")
                cv2.imwrite(img_name, frame)
                print(f"{img_name}written!")
                image_counter += 1

        cap.release()
        cv2.destroyAllWindows()
    # this is returning all available quantity for product
    def inventory(self):
        return self.availableQuantity
    
    
    
    