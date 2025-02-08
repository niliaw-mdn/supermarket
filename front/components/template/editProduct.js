import React, { useState, useEffect } from "react";
import axios from "axios";

function EditProduct({ productId, onClose }) {
  const [productData, setProductData] = useState({
    name: "",
    price_per_unit: 0,
    available_quantity: 0,
    description: "",
    category: "",
    brand: "",
    image_address: "",
  });

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/getProduct/${productId}`);
        setProductData(response.data);
      } catch (error) {
        console.error("Error fetching product data: ", error);
      }
    };

    fetchProductData();
  }, [productId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`http://localhost:5000/updateProduct/${productId}`, productData);
      alert("Product updated successfully!");
      onClose(); // Close modal after saving
    } catch (error) {
      console.error("Error updating product: ", error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-5 rounded-lg w-[400px]">
        <h3>ویرایش محصول</h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label>نام محصول</label>
            <input
              type="text"
              value={productData.name}
              onChange={(e) => setProductData({ ...productData, name: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>قیمت</label>
            <input
              type="number"
              value={productData.price_per_unit}
              onChange={(e) => setProductData({ ...productData, price_per_unit: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>موجودی</label>
            <input
              type="number"
              value={productData.available_quantity}
              onChange={(e) => setProductData({ ...productData, available_quantity: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>توضیحات</label>
            <textarea
              value={productData.description}
              onChange={(e) => setProductData({ ...productData, description: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>دسته‌بندی</label>
            <input
              type="text"
              value={productData.category}
              onChange={(e) => setProductData({ ...productData, category: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>برند</label>
            <input
              type="text"
              value={productData.brand}
              onChange={(e) => setProductData({ ...productData, brand: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="mb-4">
            <label>تصویر</label>
            <input
              type="text"
              value={productData.image_address}
              onChange={(e) => setProductData({ ...productData, image_address: e.target.value })}
              className="w-full p-2 mt-1"
            />
          </div>
          <div className="flex justify-between">
            <button type="button" onClick={onClose} className="bg-gray-500 text-white py-2 px-4 rounded">
              بستن
            </button>
            <button type="submit" className="bg-blue-500 text-white py-2 px-4 rounded">
              ذخیره تغییرات
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditProduct;
