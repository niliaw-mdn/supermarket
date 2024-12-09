import React from "react";

export default function () {
  return (
    <div className="flex flex-col">
      <div className="flex justify-center">
      <div className="w-[95%] h-[119px] relative">
        <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
        <div className="absolute right-24 top-8 font-semibold text-lg text-white">
          <a style={{ cursor: "pointer" }}>اضافه کردن کاربر</a>
        </div>

        <img
          className="w-[100px] h-[80px] left-[9px] top-1 absolute"
          src="pic/logo.png"
          alt="Logo"
        />
      </div>
      </div>
      <div className="flex justify-center">
        <table className="table-auto w-[90%] border  ">
          <thead>
            <tr>
              <th>نام و نام خانوادگی</th>
              <th>کدملی</th>
              <th>شماره تماس</th>
              <th>عکس</th>
              <th>شماره کارکنی</th>
              <th>تاریخ ورود</th>
              <th>مدرک تحصیلی</th>
              <th>وضعیت نظام وظیفه</th>
              <th>تاریخ آخرین قرارداد</th>
              <th>تاریخ پایان آخرین قرارداد</th>
              <th>قرارداد های کارکن</th>
            </tr>
          </thead>
          <tbody>
            <tr className="bg-white border-b border-t  hover:bg-gray-50 ">
              <td>The Sliding Mr. Bones (Next Stop, Pottersville)</td>
              <td>Malcolm Lockyer</td>
              <td>1961</td>
              <td>The Sliding Mr. Bones (Next Stop, Pottersville)</td>
              <td>Malcolm Lockyer</td>
              <td>The Sliding Mr. Bones (Next Stop, Pottersville)</td>
              <td>Malcolm Lockyer</td>
              <td>The Sliding Mr. Bones (Next Stop, Pottersville)</td>
              <td>Malcolm Lockyer</td>
              <td>The Sliding Mr. Bones (Next Stop, Pottersville)</td>
              <td>Malcolm Lockyer</td>
            </tr>
            <tr className="bg-white border-b  hover:bg-gray-50">
              <td>Witchy Woman</td>
              <td>The Eagles</td>
              <td>1972</td>
            </tr>

          </tbody>
        </table>
      </div>
    </div>
  );
}
