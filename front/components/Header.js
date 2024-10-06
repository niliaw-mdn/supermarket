import handler from "@/pages/api/hello";
import React from "react";
import { IoPersonCircleSharp } from "react-icons/io5";
import { useRouter } from "next/router";

function Header() {

  const router = useRouter();

  const clickHandler = ()=>{
     router.push("/profile")
  }
  return (
    <div className="flex justify-center">
      <div className="w-[95%] h-[119px] relative ">
        <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
        <div className="w-[131px] h-[50px] left-[150px] top-6 absolute text-white text-[25px] font-semibold">
          Total
        </div>
        <IoPersonCircleSharp className="w-[60px] h-[60px] right-[15px] top-[16px] absolute text-white cursor-pointer" onClick={clickHandler} />
        <div className="w-[131px] h-[50px] left-[230px] top-6 absolute text-white text-[25px] font-semibold">
          Reset
        </div>
        <img
          className="w-[100px] h-[80px] left-[9px] top-1  absolute"
          src="pic/logo.png"
        />
      </div>
    </div>
  );
}

export default Header;
