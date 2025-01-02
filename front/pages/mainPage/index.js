import React from "react";
import Link from "next/link";
import Image from "next/image";
import Product from "@/components/template/Product";

function Index() {
  return (
    <div className="grid grid-cols-[15%_auto]">
      <div className="bg-gray-50">
        <div className="fixed bg-white text-gray shadow-lg rounded-lg w-64 h-[1000px] right-[-2px] top-0">
          <div className="flex flex-row gap-40 p-3">
            <div>
              <Link href="/">
                <Image
                  src="/pic/logo.png"
                  alt="logo"
                  width={29}
                  height={33}
                  className="w-[35px] h-[40px]"
                />
              </Link>
            </div>
          </div>

          <nav>
            <ul className="w-[90%] divide-y divide-gray-300 pr-10">
              <li className="p-6">
                <a href="./">صفحه اصلی</a>
              </li>
              <li className="p-6">
                <a href="./login">پروفایل</a>
              </li>
              <li className="p-6">
                <a href="/products">محصولات</a>
              </li>
              <li className="p-6">
                <a href="/staff">کارکنان</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
      <div className="relative">
        <div className="w-[97%] h-[80px] right-5 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
        <div className="w-[131px] h-[50px] left-[150px] top-6 absolute text-white text-[25px] font-semibold">
          Total
        </div>

        <div className="w-[131px] h-[50px] left-[230px] top-6 absolute text-white text-[25px] font-semibold">
          Reset
        </div>
        <img
          className="w-[100px] h-[80px] left-[25px] top-1 absolute"
          src="pic/logo.png"
        />
        <div className="mt-32">
        <Product />
        </div>
      </div>
    </div>
  );
}

export default Index;
