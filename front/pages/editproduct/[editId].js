import React, { useState, useEffect } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";

function EditProduct({ editId, onClose }) {
  const [productData, setProductData] = useState({});
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [uomOptions, setUomOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (editId) {
          const productRes = await axios.get(
            `http://localhost:5000/getProduct/${editId}`
          );
          setProductData(productRes.data);
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

    if (!productData.name || productData.name.trim() === "") {
      toast.error("نام محصول الزامی است.");
      return;
    }

    const formData = new FormData();
    formData.append("name", productData.name);
    formData.append(
      "price_per_unit",
      parseFloat(productData.price_per_unit) || 0
    );
    formData.append(
      "available_quantity",
      parseInt(productData.available_quantity) || 0
    );
    formData.append("uom_id", parseInt(productData.uom_id) || 0);
    formData.append("manufacturer_name", productData.manufacturer_name || "");
    formData.append("weight", parseFloat(productData.weight) || 0);
    formData.append(
      "purchase_price",
      parseFloat(productData.purchase_price) || 0
    );
    formData.append(
      "discount_percentage",
      parseInt(productData.discount_percentage) || 0
    );
    formData.append("voluminosity", parseFloat(productData.voluminosity) || 0);
    formData.append("combinations", productData.combinations || "");
    formData.append(
      "nutritional_information",
      productData.nutritional_information || ""
    );
    formData.append(
      "expiration_date",
      productData.expiration_date
        ? new Date(productData.expiration_date).toISOString().split("T")[0]
        : ""
    );
    formData.append("storage_conditions", productData.storage_conditions || "");
    formData.append("number_sold", parseInt(productData.number_sold) || 0);
    formData.append(
      "date_added_to_stock",
      productData.date_added_to_stock
        ? new Date(productData.date_added_to_stock).toISOString().split("T")[0]
        : ""
    );
    formData.append(
      "total_profit_on_sales",
      parseFloat(productData.total_profit_on_sales) || 0
    );
    formData.append(
      "error_rate_in_weight",
      parseFloat(productData.error_rate_in_weight) || 0
    );
    formData.append("category_id", parseInt(productData.category_id) || 0);
    formData.append("image_address", productData.image_address || "");

    try {
      await axios.put(
        `http://localhost:5000/updateProduct/${editId}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      toast.success("محصول با موفقیت بروزرسانی شد.");
      onClose();
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
