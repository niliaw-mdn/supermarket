import React, { useState, useEffect } from "react";
import axios from "axios";

import { PiChartLineUpBold } from "react-icons/pi";
import { PiChartLineDownBold } from "react-icons/pi";

const ProductsTable = () => {
  const [statistics, setStatistics] = useState({
    totalProfit: 0,
    averageDiscount: 0,
    profitAbove1000: 0,
    maxProfit: 0,
    minProfit: 0,
    negativeProfitProducts: 0,
    totalUnitsSold: 0,
    maxUnitsSold: 0,
    minUnitsSold: 0,
  });

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const [
          totalProfit,
          averageDiscount,
          profitAbove1000,
          maxProfit,
          minProfit,
          negativeProfitProducts,
          totalUnitsSold,
          maxUnitsSold,
          minUnitsSold,
        ] = await Promise.all([
          axios.get("http://localhost:5000/total_profit"),
          axios.get("http://localhost:5000/average_discount"),
          axios.get("http://localhost:5000/profit_above_1000"),
          axios.get("http://localhost:5000/max_profit"),
          axios.get("http://localhost:5000/min_profit"),
          axios.get("http://localhost:5000/negative_profit_products"),
          axios.get("http://localhost:5000/total_units_sold"),
          axios.get("http://localhost:5000/max_units_sold"),
          axios.get("http://localhost:5000/min_units_sold"),
        ]);

        setStatistics({
          totalProfit: totalProfit.data[0] || 0,
          averageDiscount: averageDiscount.data[0] || 0,
          profitAbove1000: profitAbove1000.data[0] || 0,
          maxProfit: maxProfit.data[0] || 0,
          minProfit: minProfit.data[0] || 0,
          negativeProfitProducts: negativeProfitProducts.data[0] || 0,
          totalUnitsSold: totalUnitsSold.data[0] || 0,
          maxUnitsSold: maxUnitsSold.data[0] || 0,
          minUnitsSold: minUnitsSold.data[0] || 0,
        });
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    };

    fetchStatistics();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <table className="table-auto w-full border-collapse border border-gray-200">
        <thead>
          <tr>
            <th className="border border-gray-200 px-4 py-2">آمار</th>
            <th className="border border-gray-200 px-4 py-2">مقدار</th>
            <th className="border border-gray-200 px-4 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-gray-200 px-4 py-2">سود کل</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.totalProfit}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">میانگین تخفیف</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.averageDiscount}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-red-700">+<PiChartLineDownBold className="text-red-700" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">تعداد محصولات با سود بیشتر از1000 تومان</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.profitAbove1000}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">حداکثر سود</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.maxProfit}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">حداقل سود</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.minProfit}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">تعداد محصولات با سود منفی</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.negativeProfitProducts}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-red-700">+<PiChartLineDownBold className="text-red-700" size={30}/></td>
          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">تعداد کل واحدهای فروخته شده</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.totalUnitsSold}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>

          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">بیشترین تعداد واحد فروخته شده</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.maxUnitsSold}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-green-600">+<PiChartLineUpBold className="text-green-600" size={30}/></td>

          </tr>
          <tr>
            <td className="border border-gray-200 px-4 py-2">کمترین تعداد واحد فروخته شده</td>
            <td className="border border-gray-200 px-4 py-2">{statistics.minUnitsSold}</td>
            <td className="border border-gray-200 px-4 py-2 flex flex-row text-red-700">+<PiChartLineDownBold className="text-red-700" size={30}/></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default ProductsTable;
