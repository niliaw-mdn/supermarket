import { useState, useEffect } from "react";

export default function AddItem() {
  const [formData, setFormData] = useState({
    name: "",
    uom_id: "",
    price_per_unit: "",
    available_quantity: "",
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
    file: null,
  });
  const fieldLabels = {
    name: "نام محصول",
    uom_id: "واحد اندازه‌گیری",
    price_per_unit: "قیمت هر واحد",
    available_quantity: "مقدار موجود",
    manufacturer_name: "نام تولیدکننده",
    weight: "وزن",
    purchase_price: "قیمت خرید",
    discount_percentage: "درصد تخفیف",
    voluminosity: "حجم",
    combinations: "ترکیبات",
    nutritional_information: "اطلاعات تغذیه‌ای",
    expiration_date: "تاریخ انقضا",
    storage_conditions: "شرایط نگهداری",
    number_sold: "تعداد فروش‌رفته",
    date_added_to_stock: "تاریخ اضافه‌شده به انبار",
    total_profit_on_sales: "سود کل فروش",
    error_rate_in_weight: "نرخ خطا در وزن",
    category_id: "دسته‌بندی",
    file: "تصویر محصول",
  };

  const [categories, setCategories] = useState([]);
  const [uoms, setUoms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      const categoryData = [
        { category_id: 1, category_name: "Snacks" },
        { category_id: 2, category_name: "Dairy" },
        { category_id: 3, category_name: "Canned and Ready Meals" },
        { category_id: 4, category_name: "Fruits and Vegetables" },
        { category_id: 5, category_name: "Protein Ingredients" },
        { category_id: 6, category_name: "Beverages" },
      ];
      setCategories(categoryData);
    };

    const fetchUOMs = async () => {
      const uomData = [
        { uom_id: 1, uom_name: "each" },
        { uom_id: 2, uom_name: "kg" },
        { uom_id: 3, uom_name: "g" },
        { uom_id: 4, uom_name: "m" },
        { uom_id: 5, uom_name: "m²" },
        { uom_id: 6, uom_name: "m³" },
        { uom_id: 7, uom_name: "litr" },
      ];
      setUoms(uomData);
    };

    fetchCategories();
    fetchUOMs();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: [
        "price_per_unit",
        "weight",
        "purchase_price",
        "discount_percentage",
        "voluminosity",
        "total_profit_on_sales",
        "error_rate_in_weight",
      ].includes(name)
        ? value === ""
          ? ""
          : parseFloat(value)
        : [
            "available_quantity",
            "number_sold",
            "category_id",
            "uom_id",
          ].includes(name)
        ? value === ""
          ? ""
          : parseInt(value)
        : value,
    }));
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFormData((prev) => ({
        ...prev,
        file: e.target.files[0],
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.file) {
      alert("Please select a file before submitting.");
      return;
    }

    setIsLoading(true);

    const formDataToSend = new FormData();
    Object.keys(formData).forEach((key) => {
      if (key === "file" && formData[key] === null) return;
      formDataToSend.append(key, formData[key]);
    });

    try {
      const res = await fetch("http://localhost:5000/insertProduct", {
        method: "POST",
        body: formDataToSend,
      });

      const data = await res.json();
      setIsLoading(false);

      if (res.ok) {
        alert(`✅ محصول شما با موفقیت ثبت شد`);
        setFormData({
          name: "",
          uom_id: "",
          price_per_unit: "",
          available_quantity: "",
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
          file: null,
        });
      } else {
        alert(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setIsLoading(false);
      alert("❌ Something went wrong!");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white shadow-lg rounded-lg">
      <h1 className="text-2xl font-semibold mb-6">مشخصات محصول</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {Object.keys(formData).map((key) => {
          if (key === "file") {
            return (
              <div key={key} className="flex flex-col">
                <label className="mb-2 text-sm font-medium">عکس محصول</label>
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="dropzone-file"
                    className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    {formData.file ? (
                      <img
                        src={URL.createObjectURL(formData.file)}
                        alt="Uploaded Preview"
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <svg
                          className="w-8 h-8 mb-4 text-gray-500"
                          fill="none"
                          viewBox="0 0 20 16"
                        >
                          <path
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                          />
                        </svg>
                        <p className="mb-2 text-sm text-gray-500">
                          <span className="font-semibold">Click to upload</span>{" "}
                          or drag and drop
                        </p>
                        <p className="text-xs text-gray-500">
                          SVG, PNG, JPG or GIF (MAX. 800x400px)
                        </p>
                      </div>
                    )}
                    <input
                      id="dropzone-file"
                      type="file"
                      name={key}
                      accept="image/*"
                      className="hidden"
                      onChange={handleFileChange}
                      required
                    />
                  </label>
                </div>
              </div>
            );
          }

          if (key === "category_id") {
            return (
              <div key={key} className="flex flex-col">
                <label className="mb-2 text-sm font-medium">
                  {fieldLabels.category_id}
                </label>
                <select
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  className="border px-4 py-2 rounded-md"
                  required
                >
                  <option value=""></option>
                  {categories.map((category) => (
                    <option
                      key={category.category_id}
                      value={category.category_id}
                    >
                      {category.category_name}
                    </option>
                  ))}
                </select>
              </div>
            );
          }

          if (key === "uom_id") {
            return (
              <div key={key} className="flex flex-col">
                <label className="mb-2 text-sm font-medium">
                  {fieldLabels.uom_id}
                </label>
                <select
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  className="border px-4 py-2 rounded-md"
                  required
                >
                  <option value=""></option>
                  {uoms.map((uom) => (
                    <option key={uom.uom_id} value={uom.uom_id}>
                      {uom.uom_name}
                    </option>
                  ))}
                </select>
              </div>
            );
          }

          return (
            <div key={key} className="flex flex-col">
              <label className="mb-2 text-sm font-medium">
                {fieldLabels[key] || key}
              </label>

              <input
                type={
                  key.includes("date")
                    ? "date"
                    : key === "error_rate_in_weight"
                    ? "number"
                    : "text"
                }
                name={key}
                value={formData[key]}
                onChange={handleChange}
                className="border px-4 py-2 rounded-md"
                required
              />
            </div>
          );
        })}

        <button
          type="submit"
          className="w-full py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 flex justify-center items-center"
          disabled={isLoading}
        >
          {isLoading ? "Submitting..." : "Insert Product"}
        </button>
      </form>
    </div>
  );
}
