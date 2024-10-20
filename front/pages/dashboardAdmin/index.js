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

          <div className="relative w-[200px] h-[40px] left-[150px] top-6">
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
      <div className="flex justify-center">
      <div className="flex flex-wrap justify-start w-[90%]">
        {fetchdata.map((post) => (
          <div key={post.id} className="m-2">

            <div className="h-52 w-48 py-5 flex flex-col items-center bg-gray-100 rounded-lg shadow-md">
              <img
                className="h-24 w-24 object-contain"
                src={post.image}
                alt={post.title}
              />
              <div className="text-center mt-2 text-sm line-clamp-3">{post.title}</div>
            </div>
          </div>
        ))}
      </div>
      </div>
    </>
  );
}

export default Index;
