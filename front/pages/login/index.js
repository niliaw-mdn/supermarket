import React, { useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import { useRouter } from "next/router";

function Index() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const loginHandler = async () => {
    const response = await fetch("http://localhost:5000/login", {
  
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      const token = data.jwt_token;

      localStorage.setItem("jwt_token", token);

      toast.success("با موفقیت وارد شدید.");
      router.push("./mainPage");
    } else {
      toast.error("لطفا اطلاعات را درست وارد کنید.");
    }
  };

  return (
    <>
      <Toaster />
      <div className="flex justify-center items-center h-screen">
        <div className="border-2 shadow-slate-700 shadow-md px-20 pb-10">
          <div className="flex flex-col space-y-4">
            <div className="flex flex-col -space-y-20">
              <img src="./pic/Grocery.png" width={250} />
              <h2 className="font-extrabold text-4xl">ورود</h2>
            </div>
            <div className="relative w-64">
              <input
                type="email"
                id="floating-input"
                className="block w-full h-10 px-2.5 pt-5 pb-2 text-sm text-gray-900 bg-transparent border border-gray-300 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 peer"
                placeholder=" "
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <label
                htmlFor="floating-input"
                className="absolute text-sm text-gray-500 bg-white px-1 duration-300 transform top-[-10px] left-2 peer-placeholder-shown:top-2.5 peer-placeholder-shown:text-gray-400 peer-placeholder-shown:bg-transparent peer-focus:top-[-10px] peer-focus:text-blue-600 peer-focus:bg-white"
              >
                Email
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
                className="bg-green-600 w-[100%] rounded-md h-10 text-white font-bold text-lg"
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
