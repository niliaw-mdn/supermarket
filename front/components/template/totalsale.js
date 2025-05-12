import React, { useState, useEffect } from "react";
import axios from "axios";
import dynamic from "next/dynamic";
import Chart from "./chart";

const ApexCharts = dynamic(() => import("react-apexcharts"), { ssr: false });

function TotalSale() {
  const [dailySalesData, setDailySalesData] = useState([]);
  const [paymentMethodSales, setPaymentMethodSales] = useState([]);
  const [pieChartOptions, setPieChartOptions] = useState(null);
  const [showLegend, setShowLegend] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const salesResponse = await axios.get(
          `http://localhost:5000/stats/sales_by_date`
        );
        const paymentMethodResponse = await axios.get(
          `http://localhost:5000/stats/sales_by_payment_method`
        );

        const dailySales = salesResponse.data;
        const paymentMethods = paymentMethodResponse.data;

        // Process and format the date data
        const categories = dailySales.map((record) => {
          const date = new Date(record[0]);
          return date.toLocaleDateString("fa-IR", {
            year: "numeric",
            month: "short",
            day: "numeric",
          });
        });

        const dailyData = dailySales.map((record) => record[1]); // sales data

        const pieData = paymentMethods.map((record) => record.total_sales);
        const labels = paymentMethods.map((record) => record.payment_method);

        setDailySalesData(dailySales);
        setPaymentMethodSales(paymentMethods);

        setPieChartOptions({
          dailyData: {
            title: "Daily Sales",
            categories: categories,
            data: dailyData,
            color: "#FF5733",
          },
          pieData: {
            series: pieData,
            options: {
              chart: { type: "pie" },
              labels: labels,
              legend: { show: false, position: "bottom" },
              colors: ["#FF5733", "#33FF57", "#5733FF", "#FFC300", "#DAF7A6"],
              responsive: [
                {
                  breakpoint: 480,
                  options: {
                    chart: { width: 300 },
                    legend: { position: "bottom" },
                  },
                },
              ],
            },
          },
        });
      } catch (err) {
        console.error("Error fetching data: ", err);
      }
    };

    fetchData();
  }, []);

  // Calculate total sales and total transactions
  const totalSales = dailySalesData.reduce(
    (acc, record) => acc + record.daily_sales,
    0
  );
  const totalTransactions = dailySalesData.length;
  const avgTransactionValue = totalTransactions
    ? totalSales / totalTransactions
    : 0;

  const toggleLegend = () => {
    setPieChartOptions((prevOptions) => ({
      ...prevOptions,
      pieData: {
        ...prevOptions.pieData,
        options: {
          ...prevOptions.pieData.options,
          legend: { ...prevOptions.pieData.options.legend, show: !showLegend },
        },
      },
    }));
    setShowLegend(!showLegend);
  };

  return (
    <div>
      <div className="flex justify-center">
        <table className="table-auto border-collapse border border-gray-300 my-10 w-[90%]">
          <thead className="bg-slate-600 text-white">
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
          <tbody>
            {dailySalesData.map((record, index) => (
              <tr key={index} className="odd:bg-white even:bg-gray-200">
                <td className="border border-gray-300 px-4 py-2">
                  {new Date(record[0]).toLocaleDateString("fa-IR", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {record[1]}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {totalTransactions}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {avgTransactionValue}
                </td>
                <td className="border border-gray-300 px-4 py-2">0</td>
                <td className="border border-gray-300 px-4 py-2">
                  Not Available
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  Not Available
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-row justify-evenly mb-5">
        <div className="bg-white border border-slate-300 shadow-md flex items-center rounded-md p-2">
          {pieChartOptions?.dailyData && (
            <Chart {...pieChartOptions.dailyData} />
          )}
        </div>
        <div className="flex flex-col bg-white p-10 border border-slate-300 shadow-md items-center rounded-md">
          {pieChartOptions?.pieData && (
            <ApexCharts
              options={pieChartOptions.pieData.options}
              series={pieChartOptions.pieData.series}
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
