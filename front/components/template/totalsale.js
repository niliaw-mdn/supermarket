import React, { useState, useEffect } from "react";
import axios from "axios";
import dynamic from "next/dynamic";
import Chart from "./chart";

const ApexCharts = dynamic(() => import("react-apexcharts"), { ssr: false });

function TotalSale() {
  const [data, setData] = useState([]);
  const [pieChartOptions, setPieChartOptions] = useState(null);
  const [showLegend, setShowLegend] = useState(false);

  useEffect(() => {
    axios
      .get(`server/totalSales.json`)
      .then((res) => {
        setData(res.data);

        const productNames = res.data.map(
          (record) => record["پرفروش‌ترین محصول"]
        );
        const salesPerProduct = res.data.map((record) => record["فروش روزانه"]);

        setPieChartOptions({
          series: salesPerProduct,
          options: {
            chart: {
              type: "pie",
            },
            labels: productNames,
            legend: {
              show: false,
              position: "bottom",
            },
            colors: ["#FF5733", "#33FF57", "#5733FF", "#FFC300", "#DAF7A6"],
            responsive: [
              {
                breakpoint: 480,
                options: {
                  chart: {
                    width: 300,
                  },
                  legend: {
                    position: "bottom",
                  },
                },
              },
            ],
          },
        });
      })
      .catch((err) => {
        console.error("Error fetching data: ", err);
      });
  }, []);

  const totalSales = data.reduce(
    (acc, record) => acc + record["فروش روزانه"],
    0
  );
  const totalTransactions = data.reduce(
    (acc, record) => acc + record["تعداد تراکنش‌ها"],
    0
  );
  const avgTransactionValue = totalTransactions
    ? totalSales / totalTransactions
    : 0;

  const dailyData = {
    title: "Daily Sales",
    categories: data.map((record) => record["تاریخ"]),
    data: data.map((record) => record["فروش روزانه"]),
    color: "#FF5733",
  };

  const toggleLegend = () => {
    setPieChartOptions((prevOptions) => ({
      ...prevOptions,
      options: {
        ...prevOptions.options,
        legend: {
          ...prevOptions.options.legend,
          show: !showLegend,
        },
      },
    }));
    setShowLegend(!showLegend);
  };

  return (
    <div>
      <div className="flex justify-center">
        <table className="table-auto border-collapse border border-gray-300 my-10 w-[90%]">
          <thead className="bg-slate-600 text-white ">
            <tr>
              <th className="px-4 py-5">تاریخ</th>
              <th className="px-4 py-5">فروش روزانه</th>
              <th className="px-4 py-5">تعداد تراکنش‌ها</th>
              <th className="px-4 py-5">میانگین ارزش تراکنش</th>
              <th className="px-4 py-5">تخفیف کل</th>
              <th className="px-4 py-5">پرفروش‌ترین محصول</th>
              <th className="px-4 py-5">روش پرداخت</th>
            </tr>
          </thead>
          <tbody className="">
            {data.map((record, index) => (
              <tr key={index} className="odd:bg-white even:bg-gray-200">
                <td className="border border-gray-300 px-4 py-2">
                  {record["تاریخ"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["فروش روزانه"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["تعداد تراکنش‌ها"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["میانگین ارزش تراکنش"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["تخفیف کل"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["پرفروش‌ترین محصول"]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record["روش پرداخت"]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-row justify-evenly mb-5">
        <div className="bg-white border border-slate-300 shadow-md flex items-center rounded-md p-2">
          {data.length > 0 && <Chart {...dailyData} />}
        </div>
        <div className="flex flex-col bg-white p-10 border border-slate-300 shadow-md  items-center rounded-md">
          {pieChartOptions && (
            <ApexCharts
              options={pieChartOptions.options}
              series={pieChartOptions.series}
              type="pie"
              height="300"
              width="600"
            />
          )}
          <button
            className="mt-5 text-blue-600 font-normal text-right text-base"
            onClick={toggleLegend}
          >
            {showLegend ? "بستن" : "اطلاعات بیشتر..."}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TotalSale;
