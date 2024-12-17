import React, { useState, useEffect } from "react";
import toast, { Toaster } from "react-hot-toast"; 
import { useRouter } from "next/router";

function Index() {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  
  const loginHandler = () => {
    if (password !== "1234" || userName !== "niloofar") {
      toast.error("لطفا اطلاعات را درست وارد کنید.");
    } else {
      toast.success("با موفقیت وارد شدید.");
      router.push("/profile");
    }
  };

  return (
    <>
       <Toaster />
      <div className="flex justify-center items-center h-screen">
        <div className="border-2 shadow-slate-700 shadow-md p-5">
          <div className="flex flex-col space-y-4">
            <p className="p-3 font-semibold">ابتدا وارد حساب کاربری خود شوید.</p>
            <div className="relative w-64">
              <input
                type="text"
                id="floating-input"
                className="block w-full h-10 px-2.5 pt-5 pb-2 text-sm text-gray-900 bg-transparent border border-gray-300 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 peer"
                placeholder=" "
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
              />
              <label
                htmlFor="floating-input"
                className="absolute text-sm text-gray-500 bg-white px-1 duration-300 transform top-[-10px] left-2 peer-placeholder-shown:top-2.5 peer-placeholder-shown:text-gray-400 peer-placeholder-shown:bg-transparent peer-focus:top-[-10px] peer-focus:text-blue-600 peer-focus:bg-white"
              >
                User name
              </label>
            </div>
            <div className="relative w-64">
              <input
                type="password"
                id="floating-input"
                className="block w-full h-10 px-2.5 pt-5 pb-2 text-sm text-gray-900 bg-transparent border border-gray-300 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 peer"
                placeholder=" "
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <label
                htmlFor="floating-input"
                className="absolute text-sm text-gray-500 bg-white px-1 duration-300 transform top-[-10px] left-2 peer-placeholder-shown:top-2.5 peer-placeholder-shown:text-gray-400 peer-placeholder-shown:bg-transparent peer-focus:top-[-10px] peer-focus:text-blue-600 peer-focus:bg-white"
              >
                Password
              </label>
            </div>
            <div className="flex justify-center">
              <button
                className="bg-blue-700 w-[50%] text-white text-lg text-center rounded-md pb-1"
                onClick={loginHandler}
              >
                ورود
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Index;
