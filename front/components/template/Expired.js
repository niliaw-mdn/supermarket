// components/template/CombinedExpiredExpiring.js
import { useEffect, useState } from "react";
import axios from "axios";
import ReactPaginate from "react-paginate";

function Expired() {
  const [expiredProducts, setExpiredProducts] = useState([]);
  const [expiringProducts, setExpiringProducts] = useState([]);
  const [expiredPageCount, setExpiredPageCount] = useState(0);
  const [expiringPageCount, setExpiringPageCount] = useState(0);
  const [expiredCurrentPage, setExpiredCurrentPage] = useState(0);
  const [expiringCurrentPage, setExpiringCurrentPage] = useState(0);
  const itemsPerPage = 10;


  const fetchExpiredProducts = async (page) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/expired_productspn?page=${
          page + 1
        }&limit=${itemsPerPage}`
      );
      const data = response.data;
      setExpiredProducts(data.products);
      setExpiredPageCount(data.total_pages);
    } catch (error) {
      console.error("Error fetching expired products:", error);
    }
  };


  const fetchExpiringProducts = async (page) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/expiring_productspn?page=${
          page + 1
        }&limit=${itemsPerPage}`
      );
      const data = response.data;
      setExpiringProducts(data.products);
      setExpiringPageCount(data.total_pages);
    } catch (error) {
      console.error("Error fetching expiring products:", error);
    }
  };


  const handleExpiredPageClick = (selectedPage) => {
    setExpiredCurrentPage(selectedPage.selected);
    fetchExpiredProducts(selectedPage.selected);
  };


  const handleExpiringPageClick = (selectedPage) => {
    setExpiringCurrentPage(selectedPage.selected);
    fetchExpiringProducts(selectedPage.selected);
  };

  
  useEffect(() => {
    fetchExpiredProducts(expiredCurrentPage);
    fetchExpiringProducts(expiringCurrentPage);
  }, []);

  return (
    <div dir="rtl" className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        مدیریت محصولات منقضی و در حال انقضا
      </h1>

   
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          محصولات منقضی شده
        </h2>
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-4 py-2 text-right">نام محصول</th>
                <th className="px-4 py-2 text-right">قیمت</th>
                <th className="px-4 py-2 text-right">تعداد موجود</th>
                <th className="px-4 py-2 text-right">تاریخ انقضا</th>
              </tr>
            </thead>
            <tbody>
              {expiredProducts.map((product) => (
                <tr key={product.product_id} className="border-b">
                  <td className="px-4 py-2 text-right">{product.name}</td>
                  <td className="px-4 py-2 text-right">
                    {product.price_per_unit} تومان
                  </td>
                  <td className="px-4 py-2 text-right">
                    {product.available_quantity}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {product.expiration_date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-center">
          <ReactPaginate
            previousLabel={"قبلی"}
            nextLabel={"بعدی"}
            breakLabel={"..."}
            pageCount={expiredPageCount}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={handleExpiredPageClick}
            containerClassName={"flex gap-2 items-center"}
            activeClassName={"bg-blue-500 text-white px-3 py-1 rounded"}
            pageClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            previousClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            nextClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            disabledClassName={"opacity-50 cursor-not-allowed"}
          />
        </div>
      </div>

      
      <div>
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          محصولات در حال انقضا
        </h2>
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-4 py-2 text-right">نام محصول</th>
                <th className="px-4 py-2 text-right">قیمت</th>
                <th className="px-4 py-2 text-right">تعداد موجود</th>
                <th className="px-4 py-2 text-right">تاریخ انقضا</th>
              </tr>
            </thead>
            <tbody>
              {expiringProducts.map((product) => (
                <tr key={product.product_id} className="border-b">
                  <td className="px-4 py-2 text-right">{product.name}</td>
                  <td className="px-4 py-2 text-right">
                    {product.price_per_unit} تومان
                  </td>
                  <td className="px-4 py-2 text-right">
                    {product.available_quantity}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {product.expiration_date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-center">
          <ReactPaginate
            previousLabel={"قبلی"}
            nextLabel={"بعدی"}
            breakLabel={"..."}
            pageCount={expiringPageCount}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={handleExpiringPageClick}
            containerClassName={"flex gap-2 items-center"}
            activeClassName={"bg-blue-500 text-white px-3 py-1 rounded"}
            pageClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            previousClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            nextClassName={"px-3 py-1 border rounded hover:bg-gray-200"}
            disabledClassName={"opacity-50 cursor-not-allowed"}
          />
        </div>
      </div>
    </div>
  );
}

export default Expired;
