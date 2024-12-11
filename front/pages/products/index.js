import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { IoArrowBackOutline, IoSearch } from "react-icons/io5";
import axios from "axios";

function Index() {
  const router = useRouter();
  const [fetchdata, setFetchdata] = useState([]);

  const backHandler = () => {
    router.back();
  };

  const addItemHandler = () => {
    router.push("./addItems");
  };

  useEffect(() => {
    axios.get(`https://fakestoreapi.com/products`).then((res) => {
      setFetchdata(res.data);
    });
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
      <div className="flex justify-center mt-4">
        <table className="table-auto border-collapse border border-gray-300 w-[90%] text-center">
          <thead className="bg-gray-200">
            <tr>
              <th className="border border-gray-300 px-4 py-2">Image</th>
              <th className="border border-gray-300 px-4 py-2">Title</th>
              <th className="border border-gray-300 px-4 py-2">Price</th>
              <th className="border border-gray-300 px-4 py-2">Category</th>
            </tr>
          </thead>
          <tbody>
            {fetchdata.map((post) => (
              <tr key={post.id} className="odd:bg-white even:bg-gray-100">
                <td className="border border-gray-300 px-4 py-2">
                  <img
                    className="h-16 w-16 object-contain mx-auto"
                    src={post.image}
                    alt={post.title}
                  />
                </td>
                <td className="border border-gray-300 px-4 py-2">{post.title}</td>
                <td className="border border-gray-300 px-4 py-2">${post.price}</td>
                <td className="border border-gray-300 px-4 py-2">{post.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Index;