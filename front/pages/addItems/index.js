import React from "react";
import { useRouter } from "next/router";
import { IoArrowBackOutline } from "react-icons/io5";

function Index() {
  const router = useRouter();

  const backHandler = () => {
    router.push("./dashboardAdmin");
  };

  return (
    <>
      <div className="flex justify-center">
        <div className="w-[95%] h-[119px] relative">
          <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
          <div className="absolute right-24 top-8 font-semibold text-lg text-white"></div>

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

      <div className="flex flex-col justify-center items-center">
        <div className="bg-gray-300 h-auto w-[500px] rounded-lg flex flex-col justify-center items-center">
          <div className="mb-4 font-semibold pt-5 pl-56">
            :مشخصات محصول را وارد کنید
          </div>
          <ul className="list-none">
            <li className="py-5">
              <input
                className="h-8 w-72 rounded-md p-3"
                placeholder="اسم محصول"
                type="text"
              />
            </li>
            <li className="py-5">
              <input
                className="h-8 w-72 rounded-md p-3"
                placeholder="قیمت"
                type="text"
              />
            </li>
            <li className="py-5">
              <input
                className="h-8 w-72 rounded-md p-3"
                placeholder="مقدار"
                type="text"
              />
            </li>
            <li className="py-5">
              <input
                className="h-8 w-72 rounded-md p-3"
                placeholder="مجموع"
                type="text"
              />
            </li>
            <li>
              <label
                className="block mb-2 text-sm font-medium text-gray-900"
                htmlFor="file_input"
              >
                عکس محصول:
              </label>
              <input
                className="block w-full text-sm text-gray-900 border border-gray-500 rounded-lg cursor-pointer bg-gray-400 placeholder-gray-400"
                id="file_input"
                type="file"
                accept="image/*"
              />
            </li>
            <li className="m-10 ml-10 bg-[#0f8515] text-center pt-1 rounded-md h-10">
              <button className="text-white font-bold text-lg">تایید</button>
            </li>
          </ul>
        </div>
      </div>
    </>
  );
}

export default Index;
