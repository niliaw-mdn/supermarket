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
  const [filters, setFilters] = useState({
    minPrice: 0,
    maxPrice: 0,
    selectedBrands: [],
    selectedCategory: "",
    isCategoryOpen: false,
    isPriceOpen: false,
    isBrandOpen: false,
  });
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [productDetails, setProductDetails] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState(null);

  // Fetch initial data (minPrice, maxPrice, categories)
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [minPriceRes, maxPriceRes, categoriesRes] = await Promise.all([
          axios.get("http://localhost:5000/min_price"),
          axios.get("http://localhost:5000/max_price"),
          axios.get("http://localhost:5000/getcategory"),
        ]);
        setFilters((prev) => ({
          ...prev,
          minPrice: minPriceRes.data[0] || 0,
          maxPrice: maxPriceRes.data[0] || 0,
        }));
        setCategories(categoriesRes.data);
      } catch (error) {
        console.error("Error fetching initial data:", error);
        toast.error("Failed to load initial data.");
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const { data } = await axios.get(
          "http://localhost:5000/getProductspn",
          {
            params: {
              page,
              limit,
              minPrice: filters.minPrice ?? undefined, // Default to undefined if not set
              maxPrice: filters.maxPrice ?? undefined,
              category_id: filters.selectedCategory ?? undefined,
              search: searchQuery ?? undefined,
              sort: filters.sortField ?? "name",
              order: filters.sortOrder ?? "asc",
            },
          }
        );
        setProducts(data.products);
        setTotalPages(data.total_pages);
      } catch (error) {
        console.error(
          "Error fetching products:",
          error?.response?.data || error
        );
        toast.error("Failed to load products.");
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [page, filters, searchQuery]);

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1); // Reset to first page when filters change
  };

  // Delete product
  const deleteProduct = async (productId) => {
    if (!window.confirm("Are you sure you want to delete this product?"))
      return;
    setLoading(true);
    try {
      await axios.post("http://localhost:5000/deleteProduct", {
        product_id: productId,
      });
      toast.success("Product deleted successfully!");
      setProducts((prev) => prev.filter((p) => p.product_id !== productId));
    } catch (error) {
      console.error("Error deleting product:", error);
      toast.error("Failed to delete product.");
    } finally {
      setLoading(false);
    }
  };

  // Open product details modal
  const openModal = async (productId) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/getProduct/${productId}`
      );
      setProductDetails(response.data);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error fetching product details:", error);
      toast.error("Failed to load product details.");
    }
  };

  // Close modals
  const closeModal = () => {
    setIsModalOpen(false);
    setProductDetails(null);
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedProductId(null);
  };

  return (
    <>
      <Toaster />
      <div className="mb-[550px] mx-5">
        <h2 className="p-7 font-bold">محصولات موجود</h2>
        <div className="relative w-full">
          {/* Filters Section */}
          <div className="border-2 bg-white border-l-gray-500 shadow-md shadow-black w-[320px] inline-block align-top">
            {/* Category Filter */}
            <div className="relative w-full">
              <button
                onClick={() =>
                  handleFilterChange("isCategoryOpen", !filters.isCategoryOpen)
                }
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
              {filters.isCategoryOpen && (
                <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5">
                  <ul className="py-1 text-md divide-y-2 text-gray-700 text-center">
                    {categories.map((category) => (
                      <li key={category.category_id}>
                        <button
                          onClick={() =>
                            handleFilterChange(
                              "selectedCategory",
                              category.category_name
                            )
                          }
                          className="block px-4 py-2 hover:bg-gray-100 w-full"
                        >
                          {category.category_name}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Price Filter */}
            <div className="relative w-full mt-4">
              <button
                onClick={() =>
                  handleFilterChange("isPriceOpen", !filters.isPriceOpen)
                }
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
              {filters.isPriceOpen && (
                <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5 p-4">
                  <div className="flex flex-col items-center">
                    <div className="flex justify-between w-full mb-4">
                      <label className="text-sm text-gray-600">
                        حداقل قیمت:
                        <input
                          type="number"
                          min="0"
                          className="ml-2 border rounded-lg p-1 w-28"
                          value={filters.minPrice}
                          onChange={(e) =>
                            handleFilterChange(
                              "minPrice",
                              Number(e.target.value)
                            )
                          }
                        />
                      </label>
                      <label className="text-sm text-gray-600">
                        حداکثر قیمت:
                        <input
                          type="number"
                          min="0"
                          className="ml-2 border rounded-lg p-1 w-28"
                          value={filters.maxPrice}
                          onChange={(e) =>
                            handleFilterChange(
                              "maxPrice",
                              Number(e.target.value)
                            )
                          }
                        />
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Brand Filter */}
            <div className="relative w-full mt-4">
              <button
                onClick={() =>
                  handleFilterChange("isBrandOpen", !filters.isBrandOpen)
                }
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
              {filters.isBrandOpen && (
                <div className="w-full bg-white shadow-lg ring-1 ring-black ring-opacity-5 p-4">
                  <div className="flex flex-col items-center">
                    <ul className="py-1 text-md divide-y-2 text-gray-700 text-center">
                      {["brand1", "brand2", "brand3", "brand4"].map((brand) => (
                        <li key={brand}>
                          <input
                            type="checkbox"
                            checked={filters.selectedBrands.includes(brand)}
                            onChange={() =>
                              handleFilterChange(
                                "selectedBrands",
                                filters.selectedBrands.includes(brand)
                                  ? filters.selectedBrands.filter(
                                      (b) => b !== brand
                                    )
                                  : [...filters.selectedBrands, brand]
                              )
                            }
                            className="ml-2 border rounded-lg p-1 w-28"
                          />
                          {brand}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Products Table */}
          <div className="border-2 bg-white border-l-gray-500 shadow-md shadow-black w-[calc(100%-350px)] mr-5 inline-block align-top">
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
                {products.map((post) => (
                  <tr
                    key={post.product_id}
                    className="odd:bg-white even:bg-gray-100"
                  >
                    <td className="border border-gray-300 px-4 py-2">
                      {post.name}
                    </td>
                    <td className="border border-gray-300">
                      <div className="flex justify-center">
                        <img
                          src={`http://localhost:5000/uploads/${encodeURIComponent(
                            post.image_address
                          )}`}
                          alt={`Product ${post.product_id}`}
                          className="h-16 w-16 object-cover"
                        />
                      </div>
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {post.price_per_unit} تومان
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {post.available_quantity}
                    </td>
                    <td className="flex justify-around border border-gray-300 px-4 py-[25px]">
                      <button
                        onClick={() => {
                          setSelectedProductId(post.product_id); // Set the product ID
                          setIsEditModalOpen(true); // Open the edit modal
                        }}
                      >
                        <FaEdit className="text-lg text-green-400" size={30} />
                      </button>

                      <button onClick={() => openModal(post.product_id)}>
                        <IoEyeSharp
                          className="text-lg text-blue-400"
                          size={30}
                        />
                      </button>
                      <button onClick={() => deleteProduct(post.product_id)}>
                        <RiDeleteBin5Fill
                          className="text-lg text-red-400"
                          size={30}
                        />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <nav
              aria-label="Page navigation example"
              className="py-8 flex justify-center"
            >
              <ul className="flex items-center -space-x-px h-8 text-sm">
                <li>
                  <button
                    onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                    className={`flex items-center justify-center px-3 h-14 w-14 leading-tight text-gray-500 bg-white border border-gray-300 rounded-s-lg hover:bg-gray-100 hover:text-gray-700 ${
                      page === 1
                        ? "opacity-50 cursor-not-allowed pointer-events-none"
                        : ""
                    }`}
                    disabled={page === 1}
                  >
                    <span className="sr-only">Previous</span>
                    <svg
                      className="w-3 h-3 rtl:rotate-180"
                      aria-hidden="true"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 6 10"
                    >
                      <path
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M5 1 1 5l4 4"
                      />
                    </svg>
                  </button>
                </li>
                {Array.from({ length: totalPages }).map((_, index) => (
                  <li key={index}>
                    <button
                      onClick={() => setPage(index + 1)}
                      className={`flex items-center justify-center px-3 h-14 w-14 leading-tight ${
                        page === index + 1
                          ? "text-blue-600 bg-blue-50 border border-blue-300"
                          : "text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700"
                      }`}
                    >
                      {index + 1}
                    </button>
                  </li>
                ))}
                <li>
                  <button
                    onClick={() =>
                      setPage((prev) => Math.min(prev + 1, totalPages))
                    }
                    className={`flex items-center justify-center px-3 h-14 w-14 leading-tight text-gray-500 bg-white border border-gray-300 rounded-e-lg hover:bg-gray-100 hover:text-gray-700 ${
                      page === totalPages
                        ? "opacity-50 cursor-not-allowed pointer-events-none"
                        : ""
                    }`}
                    disabled={page === totalPages}
                  >
                    <span className="sr-only">Next</span>
                    <svg
                      className="w-3 h-3 rtl:rotate-180"
                      aria-hidden="true"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 6 10"
                    >
                      <path
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="m1 9 4-4-4-4"
                      />
                    </svg>
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>

      {/* Product Details Modal */}
      {isModalOpen && productDetails && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-md shadow-lg w-1/2">
            <h4 className="p-3 font-medium">
              جزئیات محصول {productDetails.name}
            </h4>
            <table className="w-full text-sm text-left rtl:text-right text-gray-500">
              <tbody>
                <tr className="border-b-8 border-white">
                  <th
                    scope="row"
                    className="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    دسته بندی:
                  </th>
                  <td className="px-6 py-4 bg-zinc-200">
                    {productDetails.category_name}
                  </td>
                </tr>
                <tr className="border-b-8 border-white">
                  <th
                    scope="row"
                    className="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    قیمت:
                  </th>
                  <td className="px-6 py-4 bg-zinc-200">
                    {productDetails.price_per_unit} تومان
                  </td>
                </tr>
                <tr className="border-b-8 border-white">
                  <th
                    scope="row"
                    className="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    برند:
                  </th>
                  <td className="px-6 py-4 bg-zinc-200">
                    {productDetails.manufacturer_name}
                  </td>
                </tr>
                <tr className="border-b-8 border-white">
                  <th
                    scope="row"
                    className="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    موجودی
                  </th>
                  <td className="px-6 py-4 bg-zinc-200">
                    {productDetails.available_quantity}
                  </td>
                </tr>
                <tr className="border-b-8 border-white">
                  <th
                    scope="row"
                    className="px-6 py-4 font-medium text-white whitespace-nowrap bg-zinc-500"
                  >
                    ارزش غذایی:
                  </th>
                  <td className="px-6 py-4 bg-zinc-200">
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

      {/* Edit Product Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex justify-center items-center z-50">
          <div className="rounded-md shadow-lg">
            <EditProduct editId={selectedProductId} onClose={closeEditModal} />
          </div>
        </div>
      )}
    </>
  );
}

export default Allproduct;
