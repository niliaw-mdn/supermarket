import React, { useState, useEffect } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";

function EditProduct({ editId, onClose }) {
  const [productData, setProductData] = useState({
    name: "",
    price_per_unit: "",
    available_quantity: "",
    uom_id: "",
    manufacturer_name: "",
    weight: "",
    purchase_price: "",
    discount_percentage: "",
    voluminosity: "",
    combinations: "",
    nutritional_information: "",
    expiration_date: "",
    storage_conditions: "",
    number_sold: "",
    date_added_to_stock: "",
    total_profit_on_sales: "",
    error_rate_in_weight: "",
    category_id: "",
    image_address: "",
    image: null, // Add image state for file input
  });
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [uomOptions, setUomOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch the product data for editing
        if (editId) {
          const productRes = await axios.get(
            `http://localhost:5000/getProduct/${editId}`
          );
          setProductData(productRes.data);
        }

        // Fetch UOM options
        const uomRes = await axios.get("http://localhost:5000/getUOM");
        setUomOptions(uomRes.data);

        // Fetch category options
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
    Object.keys(productData).forEach((key) => {
      if (key !== "image" && productData[key]) {  // Exclude 'image' field from being appended as a string
        formData.append(key, productData[key]);
      }
    });

    // Include image if it exists
    if (productData.image) {
      formData.append("file", productData.image);
    }

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProductData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProductData((prevData) => ({
        ...prevData,
        image: file,
      }));
    }
  };

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
                        name={field.key}
                        value={productData[field.key] || ""}
                        onChange={handleInputChange}
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
                        name={field.key}
                        value={productData[field.key] || ""}
                        onChange={handleInputChange}
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
                        name={field.key}
                        value={productData[field.key] || ""}
                        onChange={handleInputChange}
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
                        name={field.key}
                        value={productData[field.key] || ""}
                        onChange={handleInputChange}
                        required
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Image upload field */}
            <div className="flex flex-col pb-5">
              <label>تصویر محصول:</label>
              <input
                type="file"
                className="border-2 border-slate-300 rounded-md m-3 p-2"
                onChange={handleImageChange}
              />
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
