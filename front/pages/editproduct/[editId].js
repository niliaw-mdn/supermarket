import React, { useState, useEffect } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";

function EditProduct({ editId, onClose }) {
  const [productData, setProductData] = useState({});
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [uomOptions, setUomOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [originalProductData, setOriginalProductData] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (editId) {
          const productRes = await axios.get(
            `http://localhost:5000/getProduct/${editId}`
          );
          setProductData(productRes.data);
          setOriginalProductData(productRes.data); 
        }

        const uomRes = await axios.get("http://localhost:5000/getUOM");
        setUomOptions(uomRes.data);

        const categoryRes = await axios.get(
          "http://localhost:5000/getcategory"
        );
        setCategoryOptions(categoryRes.data);

        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setLoading(false);
      }
    };

    fetchData();
  }, [editId]);

  const handleUpdate = async (e) => {
    e.preventDefault();

    const formData = new FormData();


    if (productData.name) formData.append("name", productData.name);
    if (productData.price_per_unit)
      formData.append("price_per_unit", parseFloat(productData.price_per_unit));
    if (productData.available_quantity)
      formData.append(
        "available_quantity",
        parseInt(productData.available_quantity)
      );
    if (productData.uom_id)
      formData.append("uom_id", parseInt(productData.uom_id));
    if (productData.manufacturer_name)
      formData.append("manufacturer_name", productData.manufacturer_name);
    if (productData.weight)
      formData.append("weight", parseFloat(productData.weight));
    if (productData.purchase_price)
      formData.append("purchase_price", parseFloat(productData.purchase_price));
    if (productData.discount_percentage)
      formData.append(
        "discount_percentage",
        parseInt(productData.discount_percentage)
      );
    if (productData.voluminosity)
      formData.append("voluminosity", parseFloat(productData.voluminosity));
    if (productData.category_id)
      formData.append("category_id", parseInt(productData.category_id));

  
    if (
      productData.expiration_date &&
      productData.expiration_date !== originalProductData.expiration_date
    ) {
      formData.append("expiration_date", productData.expiration_date);
    }

    if (productData.image) {
      formData.append("image", productData.image);
    }

    try {
      const response = await axios.put(
        `http://localhost:5000/updateProduct/${editId}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      toast.success("محصول با موفقیت بروزرسانی شد.");
      onClose();

      
      setProductData((prev) => ({
        ...prev,
        image_address: response.data.image_address,
      }));
    } catch (err) {
      console.error("Error updating product:", err);
      toast.error("بروزرسانی محصول به مشکل برخورد، دوباره تلاش کنید.");
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <>
      <Toaster />
      <div className="flex bg-slate-50 justify-center items-center">
        <div className="border-2 w-96 relative">
          <button
            className="absolute top-3 left-3 text-zinc-500 hover:text-zinc-900"
            onClick={onClose}
          >
            ✖
          </button>

          <h2 className="text-center font-bold py-5">بروزرسانی محصول</h2>
          <form onSubmit={handleUpdate} className="p-4 flex flex-col h-full">
            <div className="grid grid-cols-2 gap-x-8">
              <div>
                {[
                  { label: "نام محصول", key: "name", type: "text" },
                  {
                    label: "واحد اندازه گیری",
                    key: "uom_id",
                    type: "select",
                    options: uomOptions,
                  },
                  { label: "برند", key: "manufacturer_name", type: "text" },
                  { label: "قیمت فروش", key: "purchase_price", type: "number" },
                ].map((field) => (
                  <div className="flex flex-col pb-5" key={field.key}>
                    <label>{field.label}:</label>
                    {field.type === "select" ? (
                      <select
                        className="border-2 border-slate-300 rounded-md m-3 p-2"
                        value={productData[field.key] || ""}
                        onChange={(e) =>
                          setProductData({
                            ...productData,
                            [field.key]: e.target.value,
                          })
                        }
                        required
                      >
                        <option value="">انتخاب {field.label}</option>
                        {field.options.map((option) => (
                          <option
                            key={option.uom_id || option.category_id}
                            value={option.uom_id || option.category_id}
                          >
                            {option.uom_name || option.category_name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        className="border-2 border-slate-300 rounded-md m-3 p-2"
                        type={field.type}
                        value={productData[field.key] || ""}
                        onChange={(e) =>
                          setProductData({
                            ...productData,
                            [field.key]: e.target.value,
                          })
                        }
                        required
                      />
                    )}
                  </div>
                ))}
              </div>

              <div>
                {[
                  { label: "وزن", key: "weight", type: "number" },
                  {
                    label: "دسته بندی",
                    key: "category_id",
                    type: "select",
                    options: categoryOptions,
                  },
                  { label: "قیمت", key: "price_per_unit", type: "number" },
                  {
                    label: "موجودی",
                    key: "available_quantity",
                    type: "number",
                  },
                ].map((field) => (
                  <div className="flex flex-col pb-5" key={field.key}>
                    <label>{field.label}:</label>
                    {field.type === "select" ? (
                      <select
                        className="border-2 border-slate-300 rounded-md m-3 p-2"
                        value={productData[field.key] || ""}
                        onChange={(e) =>
                          setProductData({
                            ...productData,
                            [field.key]: e.target.value,
                          })
                        }
                        required
                      >
                        <option value="">انتخاب {field.label}</option>
                        {field.options.map((option) => (
                          <option
                            key={option.uom_id || option.category_id}
                            value={option.uom_id || option.category_id}
                          >
                            {option.uom_name || option.category_name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        className="border-2 border-slate-300 rounded-md m-3 p-2"
                        type={field.type}
                        value={productData[field.key] || ""}
                        onChange={(e) =>
                          setProductData({
                            ...productData,
                            [field.key]: e.target.value,
                          })
                        }
                        required
                      />
                    )}
                  </div>
                ))}
              </div>

              {/* Image Upload */}
              <div className="flex flex-col pb-5">
                <label>تصویر محصول:</label>
                <input
                  className="border-2 border-slate-300 rounded-md m-3 p-2"
                  type="file"
                  accept="image/*"
                  onChange={(e) =>
                    setProductData({ ...productData, image: e.target.files[0] })
                  }
                />
              </div>

              <div className="flex flex-col pb-5">
                <label>تاریخ انقضا:</label>
                <input
                  className="border-2 border-slate-300 rounded-md m-3 p-2"
                  type="date"
                  value={productData.expiration_date || ""}
                  onChange={(e) =>
                    setProductData({
                      ...productData,
                      expiration_date: e.target.value,
                    })
                  }
                />
              </div>
            </div>

            <div className="flex justify-center p-4 mt-auto bg-white">
              <button
                type="submit"
                className="bg-blue-500 text-white p-2 rounded w-full"
              >
                بروزرسانی
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default EditProduct;
