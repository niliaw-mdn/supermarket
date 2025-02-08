import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";

import Chart from "./chart";

import { MdFastfood } from "react-icons/md";
import { GiTeapotLeaves } from "react-icons/gi";
import { GiClothes } from "react-icons/gi";


function Performance() {
  const router = useRouter();
  const [counters, setCounters] = useState({
    food: { count: 1, end: 100 },
    dishes: { count: 1, end: 250 },
    clothes: { count: 1, end: 300 },
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setCounters((prevCounters) => {
        const updatedCounters = { ...prevCounters };
        
        Object.keys(updatedCounters).forEach((key) => {
          if (updatedCounters[key].count < updatedCounters[key].end) {
            updatedCounters[key].count += 1;
          }
        });

        
        if (Object.values(updatedCounters).every((section) => section.count === section.end)) {
          clearInterval(interval);
        }

        return updatedCounters;
      });
    }, 50);

    return () => clearInterval(interval); 
  }, []);
  const backHandler = () => {
    router.back();
  };

  const dailyData = {
    title: "Daily Users",
    categories: ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "جهارشنبه", "پنج‌شنبه", "جمعه"],
    data: [120, 200, 150, 300, 280, 320, 400],
    color: "#1A56DB",
  };

  const monthlyData = {
    title: "Monthly Users",
    categories: [
      "فروردین",
      "اردیبهشت",
      "خرداد",
      "تیر",
      "مرداد",
      "شهریور",
      "مهر",
      "آبان",
      "آذر",
      "دی",
      "بهمن",
      "اسفند",
    ],
    data: [2000, 3000, 2500, 3200, 4000, 4500, 5000, 4800, 4200, 5200, 6000, 7000],
    color: "#FF5733",
  };

  const yearlyData = {
    title: "Yearly Users",
    categories: ["1399", "1400", "1401", "1402", "1403"],
    data: [24000, 30000, 28000, 32000, 35000],
    color: "#28A745",
  };



 

  return (
    <>
      <div className=" flex flex-wrap mb-20 mt-32 justify-evenly">
      <div className="relative bg-white rounded-md w-96 h-28">
        <div className="absolute bg-[#1ec0d5] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
          <MdFastfood className="text-white " size={60}/>
        </div>
        <div className="absolute left-16 top-3 text-gray-500 font-normal">خوراکی‌ها و مواد غذایی<div className="font-bold p-4 text-2xl">
        {counters.food.count}</div></div>

        </div>

        <div className="relative bg-white rounded-md w-96 h-28">
        <div className="absolute bg-[#fea11f] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
          <GiTeapotLeaves className="text-white " size={60}/>
        </div>
        <div className="absolute left-16 top-3 text-gray-500 font-normal">لوازم خانگی و آشپزخانه<div className="font-bold p-4 text-2xl">
        {counters.dishes.count}</div></div>

        </div>

        <div className="relative bg-white rounded-md w-96 h-28">
        <div className="absolute bg-[#5db461] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
          <GiClothes className="text-white " size={60}/>
        </div>
        <div className="absolute left-[140px] top-3 text-gray-500 font-normal"> پوشاک و لباس<div className="font-bold p-4 text-2xl">
        {counters.clothes.count}</div></div>

        </div>

      </div>
      <div className=" mt-16 flex justify-center">
        <div className="w-[78%] flex flex-row flex-wrap justify-start">
          <div className="flex flex-col bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20"><p className="w-full border-b-2 h-14 p-3">کارکرد هفتگی</p>
          <Chart {...dailyData} />
          </div>

          <div className="flex flex-col mr-10 bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20"><p className="w-full border-b-2 h-14 p-3">کارکرد ماهیانه</p>
          <Chart {...monthlyData} />
          </div>
          
          <div className="flex flex-col bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20"><p className="w-full border-b-2 h-14 p-3">کارکرد کلی</p>
          <Chart {...yearlyData} />
          </div>
        </div>
      </div>
    </>
  );
}

export default Performance;
