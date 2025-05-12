// components/template/CombinedExpiredExpiring.js
import { useEffect, useState } from "react";
import axios from "axios";
import {
  RiArrowLeftSLine,
  RiArrowLeftDoubleFill,
  RiArrowRightSLine,
  RiArrowRightDoubleFill,
} from "react-icons/ri";

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
      const res = await axios.get(
        `http://localhost:5000/expired_productspn?page=${page + 1}&limit=${itemsPerPage}`
      );
      const data = res.data;
      setExpiredProducts(data.products);
      setExpiredPageCount(data.total_pages);
    } catch (err) {
      console.error("Error fetching expired products:", err);
    }
  };

  const fetchExpiringProducts = async (page) => {
    try {
      const res = await axios.get(
        `http://localhost:5000/expiring_productspn?page=${page + 1}&limit=${itemsPerPage}`
      );
      const data = res.data;
      setExpiringProducts(data.products);
      setExpiringPageCount(data.total_pages);
    } catch (err) {
      console.error("Error fetching expiring products:", err);
    }
  };

  const handleExpiredPageChange = (page) => {
    setExpiredCurrentPage(page);
    fetchExpiredProducts(page);
  };

  const handleExpiringPageChange = (page) => {
    setExpiringCurrentPage(page);
    fetchExpiringProducts(page);
  };

  useEffect(() => {
    fetchExpiredProducts(expiredCurrentPage);
    fetchExpiringProducts(expiringCurrentPage);
  }, []);

  const renderPagination = (
    currentPage,
    pageCount,
    onPageChange,
    totalItems
  ) => (
    <div className="flex justify-between font-thin items-center mt-4 text-gray-400">
      <div>
        نمایش{" "}
        {Math.min(currentPage * itemsPerPage + 1, totalItems)} تا{" "}
        {Math.min((currentPage + 1) * itemsPerPage, totalItems)} از {totalItems} ورودی
      </div>
      <div className="flex gap-1 items-center">
        <button
          onClick={() => onPageChange(0)}
          disabled={currentPage === 0}
          className="px-2 py-2 rounded-full hover:bg-blue-600 hover:text-white bg-gray-300"
        >
          <RiArrowRightDoubleFill size={20} />
        </button>
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 0}
          className="px-2 py-2 rounded-full hover:bg-blue-600 hover:text-white bg-gray-300"
        >
          <RiArrowRightSLine size={20} />
        </button>

        {Array.from({ length: pageCount }, (_, i) => (
          <button
            key={i}
            onClick={() => onPageChange(i)}
            className={`px-4 py-2 rounded-full text-sm transition-all duration-200 ${
              currentPage === i
                ? "bg-blue-600 text-white"
                : "bg-gray-300 text-black hover:bg-blue-600 hover:text-white"
            }`}
          >
            {i + 1}
          </button>
        ))}

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === pageCount - 1}
          className="px-2 py-2 rounded-full hover:bg-blue-600 hover:text-white bg-gray-300"
        >
          <RiArrowLeftSLine size={20} />
        </button>
        <button
          onClick={() => onPageChange(pageCount - 1)}
          disabled={currentPage === pageCount - 1}
          className="px-2 py-2 rounded-full hover:bg-blue-600 hover:text-white bg-gray-300"
        >
          <RiArrowLeftDoubleFill size={20} />
        </button>
      </div>
    </div>
  );

  return (
    <div dir="rtl" className="mt-24 p-6 bg-white rounded ">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        مدیریت محصولات منقضی و در حال انقضا
      </h1>

      {/* Expired Products */}
      <section  className="border mb-12 p-5 shadow-md rounded-lg overflow-hidden">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          محصولات منقضی شده
        </h2>
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-red-400 text-white h-12">
              <tr>
                <th className="px-4 py-2 text-right font-thin">نام محصول</th>
                <th className="px-4 py-2 text-right font-thin">قیمت</th>
                <th className="px-4 py-2 text-right font-thin">تعداد موجود</th>
                <th className="px-4 py-2 text-right font-thin">تاریخ انقضا</th>
              </tr>
            </thead>
            <tbody>
              {expiredProducts.map((p) => (
                <tr key={p.product_id} className="border-b font-thin">
                  <td className="px-4 py-5 text-right">{p.name}</td>
                  <td className="px-4 py-5 text-green-600 text-right">
                    {p.price_per_unit} تومان
                  </td>
                  <td className="px-4 py-5 text-right">{p.available_quantity}</td>
                  <td className="px-4 py-5 text-right">{p.expiration_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {renderPagination(
          expiredCurrentPage,
          expiredPageCount,
          handleExpiredPageChange,
          expiredProducts.length
        )}
      </section>

      {/* Expiring Products */}
      <section  className="border p-5 shadow-md rounded-lg overflow-hidden">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          محصولات در حال انقضا
        </h2>
        <div>
          <table className="min-w-full">
            <thead className="bg-orange-400/50 text-white h-12">
              <tr>
                <th className="px-4 py-2 text-right font-thin">نام محصول</th>
                <th className="px-4 py-2 text-right font-thin">قیمت</th>
                <th className="px-4 py-2 text-right font-thin">تعداد موجود</th>
                <th className="px-4 py-2 text-right font-thin">تاریخ انقضا</th>
              </tr>
            </thead>
            <tbody>
              {expiringProducts.map((p) => (
                <tr key={p.product_id} className="border-b font-thin">
                  <td className="px-4 py-5 text-right">{p.name}</td>
                  <td className="px-4 py-5 text-green-600 text-right">
                    {p.price_per_unit} تومان
                  </td>
                  <td className="px-4 py-5 text-right">{p.available_quantity}</td>
                  <td className="px-4 py-5 text-right">{p.expiration_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {renderPagination(
          expiringCurrentPage,
          expiringPageCount,
          handleExpiringPageChange,
          expiringProducts.length
        )}
      </section>
    </div>
  );
}

export default Expired;
