import React from "react";
import { useRouter } from "next/router";
import { IoArrowBackOutline, IoSearch } from "react-icons/io5";

function Index() {
  const router = useRouter();

  const backHandler = () => {
    router.push("./");
  };

  const addItemHandler = () => {
    router.push("./addItems");
  }

  return (
    <div className="flex justify-center">
      <div className="w-[95%] h-[119px] relative">
        <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
        <div className="absolute right-24 top-8 font-semibold text-lg text-white">
          <a style={{cursor:"pointer"}} onClick={addItemHandler}>اضافه کردن کالا جدید</a>
        </div>


        <div className="relative w-[200px] h-[40px] left-[150px] top-6">
          <IoSearch className="absolute  text-gray-700 text-[20px] top-1/2 left-3 transform -translate-y-1/2" />
          <input
            className="pl-10 w-full h-full  border-none rounded-lg  outline-none text-gray-700 text-[18px]"
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
  );
}

export default Index;
