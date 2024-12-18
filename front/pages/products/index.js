import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { IoArrowBackOutline, IoSearch } from "react-icons/io5";
import axios from "axios";

function Index() {
  const router = useRouter();
  const [fetchdata, setFetchdata] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [openSection, setOpenSection] = useState(null);
  const [minValue, setMinValue] = useState(1000); 
  const [maxValue, setMaxValue] = useState(50000);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false); 
  const [isPriceOpen, setIsPriceOpen] = useState(false); 
  const [isBrandOpen, setIsBrandOpen] = useState(false);
  const [selectedBrands, setSelectedBrands] = useState([]); 

  const backHandler = () => router.back();
  const addItemHandler = () => router.push("./addItems");

  useEffect(() => {
    axios
      .get(`http://localhost:5000/getProducts`) 
      .then((res) => {
        setFetchdata(res.data);
      })
      .catch((err) => {
        console.error("Error fetching data: ", err);
      });
  }, []);

  const toggleBrandSelection = (brand) => {
    setSelectedBrands((prev) =>
      prev.includes(brand) ? prev.filter((b) => b !== brand) : [...prev, brand]
    );
  };

  const filteredData = fetchdata.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  return (
    <>
      <div className="flex justify-center">
        <div className="w-[95%] h-[119px] relative">
          <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
          <div className="absolute right-24 top-8 font-semibold text-lg text-white">
            <a style={{ cursor: "pointer" }} onClick={addItemHandler}>
              اضافه کردن کالا جدید
            </a>
          </div>

          <div className="relative w-[250px] h-[40px] right-80 top-6">
            <IoSearch className="absolute text-gray-700 text-[20px] top-1/2 left-3 transform -translate-y-1/2" />
            <input
              className="pl-10 w-full h-full border-none rounded-lg outline-none text-gray-700 text-[18px]"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <img
            className="w-[100px] h-[80px] left-[9px] top-1 absolute"
            src="pic/logo.png"
            alt="Logo"
          />

          <IoArrowBackOutline
            className="absolute left-[-35px] top-7 text-gray-400 cursor-pointer"
            size={30}
            onClick={backHandler}
          />
        </div>
      </div>
      <div className="flex mx-5 mt-4 justify-between items-start">
        <div className="border-2 border-l-gray-500 shadow-md shadow-black w-80 overflow-hidden h-auto">
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
                    {[
                      "تنقلات",
                      "لبنیات",
                      "کنسرو و غذای آماده",
                      "میوه و سبزیجات",
                      "مواد پروتئینی",
                      "نوشیدنی ها",
                    ].map((option) => (
                      <li key={option}>
                        <a
                          href="#"
                          className="block px-4 py-2 hover:bg-gray-100"
                        >
                          {option}
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
                          onChange={(e) => setMinValue(Number(e.target.value))}
                        />
                      </label>
                      <label className="text-sm text-gray-600">
                        حداکثر قیمت:
                        <input
                          type="number"
                          max="50000"
                          className="ml-2 border rounded-lg p-1 w-28"
                          value={maxValue}
                          onChange={(e) => setMaxValue(Number(e.target.value))}
                        />
                      </label>
                    </div>
                    <button
                      className="bg-green-500 text-white px-4 py-2 rounded-lg"
                      onClick={() => setIsPriceOpen(false)}
                    >
                      اعمال فیلتر
                    </button>
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
                        {["brand1", "brand2", "brand3", "brand4"].map((option) => (
                          <li key={option}>
                            <input
                              type="checkbox"
                              checked={selectedBrands.includes(option)}
                              onChange={() => toggleBrandSelection(option)}
                              className="ml-2 border rounded-lg p-1 w-28"
                            />
                            {option}
                          </li>
                        ))}
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

        <table className="table-auto border-collapse border border-gray-300 w-[80%] text-center">
          <thead className="bg-gray-200">
            <tr>
              <th className="border border-gray-300 px-4 py-2">Image</th>
              <th className="border border-gray-300 px-4 py-2">Title</th>
              <th className="border border-gray-300 px-4 py-2">Price</th>
              <th className="border border-gray-300 px-4 py-2">Category</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((post) => (
              <tr key={post.id} className="odd:bg-white even:bg-gray-100">
                <td className="border border-gray-300 px-4 py-2">
                  <img
                    className="h-16 w-16 object-contain mx-auto"
                    src={post.image}
                    alt={post.title}
                  />
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {post.name}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  ${post.price}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {post.category}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Index;
