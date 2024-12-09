import React, { useState } from "react";
import { useRouter } from "next/router";

import Chart from "../../components/template/chart";

import { IoPersonCircleSharp, IoArrowBackOutline } from "react-icons/io5";


function index() {
  const router = useRouter();

  const backHandler = () => {
    router.back();
  };

  const dailyData = {
    title: "Daily Users",
    categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    data: [120, 200, 150, 300, 280, 320, 400],
    color: "#1A56DB",
  };

  const monthlyData = {
    title: "Monthly Users",
    categories: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ],
    data: [2000, 3000, 2500, 3200, 4000, 4500, 5000, 4800, 4200, 5200, 6000, 7000],
    color: "#FF5733",
  };

  const yearlyData = {
    title: "Yearly Users",
    categories: ["2020", "2021", "2022", "2023", "2024"],
    data: [24000, 30000, 28000, 32000, 35000],
    color: "#28A745",
  };

  return (
    <>
      <div className="flex justify-center">
        <div className="w-[95%] h-[119px] relative">
          <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
          <div className="absolute right-24 top-8 font-semibold text-lg text-white">
            <p>.نیلوفر معدنی خوش آمدید</p>
          </div>
          <div className="w-[131px] h-[50px] left-[150px] top-6 absolute text-white text-[25px] font-semibold">
            Edit
          </div>
          <IoPersonCircleSharp className="w-[60px] h-[60px] right-[15px] top-[16px] absolute text-white cursor-pointer" />
          <img
            className="w-[100px] h-[80px] left-[9px] top-1 absolute"
            src="pic/logo.png"
          />
          <IoArrowBackOutline
            className="absolute left-[-35px] top-7 text-gray-400"
            size={30}
            onClick={backHandler}
          />
        </div>
      </div>

      <div className="flex justify-center">
        <div className="w-[95%] flex flex-row justify-evenly">
          <div className="flex flex-col">کارکرد امروز
          <Chart {...dailyData} />
          </div>

          <div className="border-l border-gray-300 h-screen mx-4"></div>
          <div className="flex flex-col">کارکرد ماهیانه
          <Chart {...monthlyData} />
          </div>
          <div className="border-l border-gray-300 h-screen mx-4"></div>
          <div className="flex flex-col">کارکرد کلی
          <Chart {...yearlyData} />
          </div>
        </div>
      </div>
    </>
  );
}

export default index;
