import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { FaEdit } from "react-icons/fa";
import { RiDeleteBin5Fill } from "react-icons/ri";
import { IoEyeSharp } from "react-icons/io5";
import EditProduct from "@/pages/editproduct/[editId]";
import toast, { Toaster } from "react-hot-toast";

function Allproduct({ searchQuery = "" }) {
  const router = useRouter();
  const [fetchdata, setFetchdata] = useState([]);
  const [openSection, setOpenSection] = useState(null);
  const [minValue, setMinValue] = useState(1000);
  const [maxValue, setMaxValue] = useState(9000000000);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const [isPriceOpen, setIsPriceOpen] = useState(false);
  const [isBrandOpen, setIsBrandOpen] = useState(false);
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [productDetails, setProductDetails] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [loading, setLoading] = useState(true);

  const backHandler = () => router.back();
  const addItemHandler = () => router.push("./addItems");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const categoryResponse = await axios.get(
          "http://localhost:5000/getcategory"
        );
        setCategories(categoryResponse.data);
      } catch (error) {
        console.error("Error fetching categories: ", error);
      }

      try {
        const productResponse = await axios.get(
          "http://localhost:5000/getProducts"
        );
        setFetchdata(productResponse.data);
      } catch (error) {
        console.error("Error fetching products: ", error);
      }
    };

    fetchData();
  }, []);

  const handleCategoryChange = (categoryName) => {
    setSelectedCategory(categoryName);
  };

  const toggleBrandSelection = (brand) => {
    setSelectedBrands((prev) =>
      prev.includes(brand) ? prev.filter((b) => b !== brand) : [...prev, brand]
    );
  };

  const filteredData = fetchdata.filter((item) => {
    const matchesSearch = item.name
      ? item.name.toLowerCase().includes(searchQuery.toLowerCase())
      : false;

    const matchesPrice =
      item.price_per_unit >= minValue && item.price_per_unit <= maxValue;

    const matchesBrand =
      selectedBrands.length === 0 || selectedBrands.includes(item.brand);

    const selectedCategoryId = categories.find(
      (cat) => cat.category_name === selectedCategory
    )?.category_id;

    const matchesCategory =
      !selectedCategory || item.category_id === selectedCategoryId;

    return matchesSearch && matchesPrice && matchesBrand && matchesCategory;
  });

  const toggleSection = (section) => {
    setOpenSection(openSection === section ? null : section);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest(".accordion")) {
        setOpenSection(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);


  const deleteProduct = async (productId) => {
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/deleteProduct', {
        product_id: productId,
      });

      if (response.status === 200) {
        toast.success("محصول با موفقیت حذف شد!");
      }
    } catch (error) {
      console.error("Error deleting product:", error);
      alert("There was an error deleting the product.");
    } finally {
      setLoading(false);
    }
  };

  const edit = (productId) => {
    setSelectedProductId(productId);
    setIsEditModalOpen(true);
  };

  const openModal = async (productId) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/getProduct/${productId}`
      );
      setProductDetails(response.data);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error fetching product details: ", error);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setProductDetails(null);
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedProductId(null);
  };

  const categoryMapping = {
    Snacks: "تنقلات",
    Dairy: "لبنیات",
    "Canned and Ready Meals": "کنسرو و غذای آماده",
    "Fruits and Vegetables": "میوه و سبزیجات",
    "Protein Ingredients": "مواد پروتئینی",
    Beverages: "نوشیدنی ها",
  };

  return (
    <>
    <Toaster/>
      <div className=" mb-[550px]  mx-5 ">
        <h2 className="p-7 font-bold">محصولات موجود</h2>
        <div className="relative w-full">
          <div
            className="border-2 bg-white border-l-gray-500 shadow-md  shadow-black w-[320px] inline-block align-top"
            style={{ verticalAlign: "top" }}
          >
            <div className="flex justify-between p-3">
              <p className="font-bold text-xl text-slate-800">فیلترها</p>
              <span>
                <a href="#" className="text-teal-600">
                  حذف فیلترها
                </a>
              </span>
            </div>
            <div className="w-full">
              <div className="relative  w-full">
                <button
                  onClick={() => setIsCategoryOpen(!isCategoryOpen)}
                  className="w-full inline-flex rounded-md bg-white px-7 pt-5 pb-3 font-medium text-gray-700 border-b-2"
                >
                  دسته بندی
                  <svg
                    className="w-5 h-5 ml-2 text-gray-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {isCategoryOpen && (
                  <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5">
                    <ul className="py-1 text-md divide-y-2 text-gray-700 text-center">
                      {categories.map((category) => (
                        <li key={category.category_id}>
                          <a
                            href="#"
                            className="block px-4 py-2 hover:bg-gray-100"
                            onClick={() =>
                              handleCategoryChange(category.category_name)
                            }
                          >
                            {categoryMapping[category.category_name] ||
                              category.category_name}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="relative w-full mt-4">
                <button
                  onClick={() => setIsPriceOpen(!isPriceOpen)}
                  className="w-full inline-flex rounded-md bg-white px-7 pt-5 pb-3 font-medium text-gray-700 border-b-2"
                >
                  محدوده قیمت
                  <svg
                    className="w-5 h-5 ml-2 text-gray-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {isPriceOpen && (
                  <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5 p-4">
                    <div className="flex flex-col items-center">
                      <div className="flex justify-between w-full mb-4">
                        <label className="text-sm text-gray-600">
                          حداقل قیمت:
                          <input
                            type="number"
                            min="1000"
                            className="ml-2 border rounded-lg p-1 w-28"
                            value={minValue}
                            onChange={(e) =>
                              setMinValue(Number(e.target.value))
                            }
                          />
                        </label>
                        <label className="text-sm text-gray-600">
                          حداکثر قیمت:
                          <input
                            type="number"
                            max="9000000000"
                            className="ml-2 border rounded-lg p-1 w-28"
                            value={maxValue}
                            onChange={(e) =>
                              setMaxValue(Number(e.target.value))
                            }
                          />
                        </label>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="relative w-full mt-4">
                <button
                  onClick={() => setIsBrandOpen(!isBrandOpen)}
                  className="w-full inline-flex rounded-md bg-white px-7 pt-5 pb-3 font-medium text-gray-700 border-b-2"
                >
                  برند
                  <svg
                    className="w-5 h-5 ml-2 text-gray-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {isBrandOpen && (
                  <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5 p-4">
                    <div className="flex flex-col items-center">
                      <div className="flex justify-center w-full mb-4">
                        <ul className="py-1 text-md divide-y-2 text-gray-700 text-center">
                          {["brand1", "brand2", "brand3", "brand4"].map(
                            (option) => (
                              <li key={option}>
                                <input
                                  type="checkbox"
                                  checked={selectedBrands.includes(option)}
                                  onChange={() => toggleBrandSelection(option)}
                                  className="ml-2 border rounded-lg p-1 w-28"
                                />
                                {option}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                      <button
                        className="bg-green-500 text-white px-4 py-2 rounded-lg"
                        onClick={() => setIsBrandOpen(false)}
                      >
                        اعمال فیلتر
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div
            className="border-2 bg-white border-l-gray-500 shadow-md shadow-black w-[calc(100%-350px)] mr-5 inline-block align-top"
            style={{ verticalAlign: "top" }}
          >
            <table className="table-auto border-collapse border border-gray-300 w-full text-center h-full">
              <thead className="bg-gray-200">
                <tr>
                  <th className="border border-gray-300 px-4 py-2">
                    نام محصول
                  </th>
                  <th className="border border-gray-300 px-4 py-2">تصویر</th>
                  <th className="border border-gray-300 px-4 py-2">قیمت</th>
                  <th className="border border-gray-300 px-4 py-2">موجودی</th>
                  <th className="border border-gray-300 px-4 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((post) => (
                  <tr
                    key={post.product_id}
                    className="odd:bg-white even:bg-gray-100"
                  >
                    <td className="border border-gray-300 px-4 py-2">
                      {post.name}
                    </td>

                    <td className="border border-gray-300 px-4 py-2">
                      <img
                        src={`http://localhost:5000/productimages/${post.image_address.replace(
                          "uploads/",
                          ""
                        )}`}
                        alt={`Product ${post.product_id}`}
                        className="h-16 w-16 object-cover"
                      />
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {post.price_per_unit}تومان
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {post.available_quantity}
                    </td>
                    <td className="flex  justify-around border border-gray-300 px-4 py-[25px]">
                      <div className="relative group">
                        <FaEdit
                          className="text-lg text-green-400"
                          size={30}
                          onClick={() => edit(post.product_id)}
                        />
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-zinc-600 text-white text-sm rounded-md px-2 py-1">
                          ویرایش
                        </span>
                      </div>
                      <div className="relative group">
                        <IoEyeSharp
                          className="text-lg text-blue-400"
                          size={30}
                          onClick={() => openModal(post.product_id)}
                        />
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-zinc-600 text-white text-sm rounded-md px-2 py-1">
                          جزئیات
                        </span>
                      </div>
                      <div className="relative group ml-4">
                        <RiDeleteBin5Fill
                          className="text-lg text-red-400"
                          size={30}
                          onClick={() => {
                            if (
                              window.confirm(
                                "از پاک کردن این محصول مطمئن هستید؟"
                              )
                            ) {
                              deleteProduct(post.product_id);
                            }
                          }}
                        />
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-zinc-600 text-white text-sm rounded-md px-2 py-1">
                          حذف
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      {isModalOpen && productDetails && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-md shadow-lg w-1/2">
            <h4 className="p-3 font-medium">
              جزئیات محصول {productDetails.name}
            </h4>
            <table class="w-full text-sm text-left rtl:text-right text-gray-500">
              <tbody>
                <tr class="border-b-8 border-white">
                  <th
                    scope="row"
                    class="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    دسته بندی:
                  </th>
                  <td class="px-6 py-4 bg-zinc-200">
                    {productDetails.category_name}
                  </td>
                </tr>
                <tr class="border-b-8 border-white">
                  <th
                    scope="row"
                    class="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    قیمت:
                  </th>
                  <td class="px-6 py-4 bg-zinc-200">
                    {productDetails.price_per_unit} تومان
                  </td>
                </tr>
                <tr class="border-b-8 border-white">
                  <th
                    scope="row"
                    class="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    برند:
                  </th>
                  <td class="px-6 py-4 bg-zinc-200">
                    {productDetails.manufacturer_name}
                  </td>
                </tr>
                <tr class="border-b-8 border-white">
                  <th
                    scope="row"
                    class="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    موجودی
                  </th>
                  <td class="px-6 py-4 bg-zinc-200">
                    {productDetails.available_quantity}
                  </td>
                </tr>
                <tr class="border-b-8 border-white">
                  <th
                    scope="row"
                    class="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    ارزش غذایی:
                  </th>
                  <td class="px-6 py-4 bg-zinc-200">
                    {productDetails.nutritional_information}
                  </td>
                </tr>
              </tbody>
            </table>

            <button
              className="mt-4 px-4 py-2 bg-red-500 text-white rounded-md"
              onClick={closeModal}
            >
              بستن
            </button>
          </div>
        </div>
      )}

      {isEditModalOpen && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex justify-center items-center z-50">
          <div className="rounded-md shadow-lg ">
            <EditProduct editId={selectedProductId} onClose={closeEditModal} />
          </div>
        </div>
      )}
    </>
  );
}

export default Allproduct;
