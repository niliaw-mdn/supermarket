import React, { useState } from "react";
import dynamic from "next/dynamic";

const ApexCharts = dynamic(() => import("react-apexcharts"), { ssr: false });

const Chart = ({ title, categories, data, color }) => {
  const [chartOptions, setChartOptions] = useState({
    chart: {
      height: "100%",
      type: "area",
      fontFamily: "Inter, sans-serif",
      toolbar: {
        show: false,
      },
    },
    tooltip: {
      enabled: true,
    },
    fill: {
      type: "gradient",
      gradient: {
        opacityFrom: 0.55,
        opacityTo: 0,
        gradientToColors: [color],
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 2,
    },
    grid: {
      show: false,
    },
    xaxis: {
      categories: categories,
    },
    yaxis: {
      show: false,
    },
  });

  const [chartSeries, setChartSeries] = useState([
    {
      name: title,
      data: data,
      color: color,
    },
  ]);

  return (
    <div className="w-full">
      <ApexCharts
        options={chartOptions}
        series={chartSeries}
        type="area"
        height="300"
      />
    </div>
  );
};

export default Chart;
