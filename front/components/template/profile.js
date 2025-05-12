import React from "react";

function Profile() {
  return (
    <div className="grid mt-36 grid-cols-[58%,30%] gap-32 mx-10">
      <div className="flex flex-col bg-white rounded-md border border-slate-300 shadow-md">
        <div className="flex flex-row">
          <div className="flex flex-col p-8">
            <p className=" text-gray-800  font-normal">
              نام
              <input
                type="text"
                className="border-b-2 border-gray-400  w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              شماره تماس
              <input
                type="text"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              تاریخ تولد
              <input
                type="date"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              تاریخ ورود
              <input
                type="date"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
          </div>
          <div className="flex flex-col p-8">
            <p className=" text-gray-800  font-normal">
              نام خانوادگی
              <input
                type="text"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              آدرس ایمیل
              <input
                type="email"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              سابقه کاری
              <input
                type="number"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
            <p className="pt-6 text-gray-800  font-normal">
              کشور
              <input
                type="text"
                className="border-b-2 border-gray-400 w-96 h-9"
              />
            </p>
          </div>
        </div>
        <div className="flex flex-row">
          <button className="bg-violet-600 hover:bg-violet-300 p-2 text-white w-28 rounded-md m-5">
            save
          </button>
          <button className="bg-gray-200 hover:bg-gray-100 p-2 border  w-28 rounded-md m-5">
            cancel
          </button>
        </div>
      </div>
      <div className="flex flex-col">
        <div className="bg-white rounded-md border border-slate-300 shadow-md flex flex-col items-center py-10">
          <img src="pic/avatar.png" width={150} />
          <p className="pt-5">Niloofar Madani</p>
          <p className="text-gray-400 text-base font-normal">Front deeloper</p>
        </div>
        <div className="bg-white mt-6 rounded-md border border-slate-300 shadow-md flex flex-col  p-7">
          <h2>مهارت ها</h2>
          <div className="flex flex-wrap">
          <p className="p-2 bg-gray-200 text-gray-600 text-sm rounded-xl">Word</p>
          <p className="p-2 mx-5 bg-gray-200 text-gray-600 text-sm rounded-xl">Excel</p>
          <p className="p-2 bg-gray-200 text-gray-600 text-sm rounded-xl">PowerPoint </p>
          <p className="p-2 mx-5 bg-gray-200 text-gray-600 text-sm rounded-xl">Point of Sale</p>
          <p className="p-2  mt-3 bg-gray-200 text-gray-600 text-sm rounded-xl">QuickBooks</p>

          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
