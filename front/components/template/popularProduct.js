import axios from "axios";
import React, { useEffect, useState } from "react";

export default function PopularProduct() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetching each API endpoint sequentially
        const topProductsResponse = await axios.get("http://localhost:5000/stats/top_products");
        const popularCategoriesResponse = await axios.get("http://localhost:5000/stats/most_popular_categories");
        const peakHourResponse = await axios.get("http://localhost:5000/stats/peak_order_hour");
        const monthlyGrowthResponse = await axios.get("http://localhost:5000/stats/monthly_sales_growth");

        // Setting data from responses
        setData({
          topProducts: topProductsResponse.data,
          popularCategories: popularCategoriesResponse.data,
          peakHour: peakHourResponse.data,
          monthlyGrowth: monthlyGrowthResponse.data,
        });
      } catch (err) {
        console.error("Error loading stats:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Loading state or if data is not yet fetched
  if (loading || !data) return <p className="text-center py-10">در حال بارگذاری...</p>;

  // Destructure data
  const { topProducts, popularCategories, peakHour, monthlyGrowth } = data;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-10 text-right" dir="rtl">
      <h1 className="text-3xl font-bold text-center mb-6">گزارش‌های آماری فروشگاه</h1>

      <section className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📦 پرفروش‌ترین محصولات</h2>
        <ul className="space-y-2">
          {topProducts.map((item) => (
            <li key={item.product_id} className="flex justify-between">
              <span>{item.name}</span>
              <span>{item.total_quantity} عدد</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📁 محبوب‌ترین دسته‌بندی‌ها</h2>
        <ul className="space-y-2">
          {popularCategories.map((cat) => (
            <li key={cat.category_id} className="flex justify-between">
              <span>{cat.category_name}</span>
              <span>{cat.order_count} سفارش</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold mb-4">⏰ ساعت اوج سفارش</h2>
        <p>
          بیشترین سفارش در ساعت <strong>{peakHour.hour}:00</strong> با{" "}
          <strong>{peakHour.order_count}</strong> سفارش ثبت شده است.
        </p>
      </section>

      <section className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📊 رشد فروش ماهانه</h2>
        <p>
          فروش این ماه:{" "}
          <strong>{monthlyGrowth.current_sales.toLocaleString()} تومان</strong>
        </p>
        <p>
          فروش ماه گذشته:{" "}
          <strong>{monthlyGrowth.previous_sales.toLocaleString()} تومان</strong>
        </p>
        <p>
          نرخ رشد:{" "}
          <strong
            className={
              monthlyGrowth.growth_rate_percentage !== null &&
              monthlyGrowth.growth_rate_percentage >= 0
                ? "text-green-600"
                : "text-red-600"
            }
          >
            {monthlyGrowth.growth_rate_percentage !== null
              ? `${monthlyGrowth.growth_rate_percentage.toFixed(2)}%`
              : "ندارد"}
          </strong>
        </p>
      </section>
    </div>
  );
}
