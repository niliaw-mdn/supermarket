import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import ProductsTable from "./ProductsTable";

import Chart from "./chart";

import { MdFastfood } from "react-icons/md";
import { GiTeapotLeaves } from "react-icons/gi";
import { GiClothes } from "react-icons/gi";
import { FaChartLine } from "react-icons/fa";

function Performance() {
  const router = useRouter();

  const [counters, setCounters] = useState({
    food: { count: 1, end: 100 },
    dishes: { count: 1, end: 250 },
    clothes: { count: 1, end: 300 },
    totalProduct: { count: 1, end: 0 },
  });

  useEffect(() => {
    const fetchTotalProducts = async () => {
      try {
        const response = await fetch("http://localhost:5000/total_products");
        const data = await response.json();

        setCounters((prev) => ({
          ...prev,
          totalProduct: { count: 1, end: data || 0 },
        }));
      } catch (error) {
        console.error("Error fetching total products:", error);
      }
    };

    fetchTotalProducts();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCounters((prevCounters) => {
        let allCompleted = true;
        const newCounters = Object.keys(prevCounters).reduce((acc, key) => {
          if (prevCounters[key].count < prevCounters[key].end) {
            acc[key] = {
              ...prevCounters[key],
              count: prevCounters[key].count + 1,
            };
            allCompleted = false;
          } else {
            acc[key] = prevCounters[key];
          }
          return acc;
        }, {});

        if (allCompleted) clearInterval(interval);

        return newCounters;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [counters.totalProduct.end]);

  const backHandler = () => {
    router.back();
  };

  const dailyData = {
    title: "Daily Users",
    categories: [
      "شنبه",
      "یکشنبه",
      "دوشنبه",
      "سه‌شنبه",
      "جهارشنبه",
      "پنج‌شنبه",
      "جمعه",
    ],
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
    data: [
      2000, 3000, 2500, 3200, 4000, 4500, 5000, 4800, 4200, 5200, 6000, 7000,
    ],
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
          <div className="absolute bg-[#af24f0] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
            <FaChartLine className="text-white " size={60} />
          </div>
          <div className="absolute left-16 top-3 text-gray-500 font-normal">
            تعداد کل محصولات:
            <div className="font-bold p-4 text-2xl">
              {counters.totalProduct.count}
            </div>
          </div>
        </div>
        <div className="relative bg-white rounded-md w-96 h-28">
          <div className="absolute bg-[#1ec0d5] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
            <MdFastfood className="text-white " size={60} />
          </div>
          <div className="absolute left-16 top-3 text-gray-500 font-normal">
            خوراکی‌ها و مواد غذایی
            <div className="font-bold p-4 text-2xl">{counters.food.count}</div>
          </div>
        </div>

        <div className="relative bg-white rounded-md w-96 h-28">
          <div className="absolute bg-[#fea11f] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
            <GiTeapotLeaves className="text-white " size={60} />
          </div>
          <div className="absolute left-16 top-3 text-gray-500 font-normal">
            لوازم خانگی و آشپزخانه
            <div className="font-bold p-4 text-2xl">
              {counters.dishes.count}
            </div>
          </div>
        </div>

        <div className="relative bg-white rounded-md w-96 h-28">
          <div className="absolute bg-[#5db461] bottom-8 rounded-md right-3 flex justify-center items-center w-24 h-24">
            <GiClothes className="text-white " size={60} />
          </div>
          <div className="absolute left-[140px] top-3 text-gray-500 font-normal">
            {" "}
            پوشاک و لباس
            <div className="font-bold p-4 text-2xl">
              {counters.clothes.count}
            </div>
          </div>
        </div>
      </div>
      <div className=" mt-16 flex justify-center">
        <div className="w-[90%] flex flex-row flex-wrap justify-start">
          <div className="flex flex-col bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20">
            <p className="w-full border-b-2 h-14 p-3">کارکرد هفتگی</p>
            <Chart {...dailyData} />
          </div>

          <div className="flex flex-col mr-10 bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20">
            <p className="w-full border-b-2 h-14 p-3">کارکرد ماهیانه</p>
            <Chart {...monthlyData} />
          </div>

          <div className="flex flex-col bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20">
            <p className="w-full border-b-2 h-14 p-3">کارکرد کلی</p>
            <Chart {...yearlyData} />
          </div>
          <div className="flex flex-col mr-10 bg-white border-2 border-zinc-300 rounded-md shadow-md mt-20">
            <ProductsTable/>
          </div>
        </div>
      </div>
    </>
  );
}

export default Performance;
