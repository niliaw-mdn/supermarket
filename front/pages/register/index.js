import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/router";
import toast, { Toaster } from "react-hot-toast"; 

export default function Index() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  
  const router = useRouter();

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords don't match");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/register", {
        email,
        password,
        confirm_password: confirmPassword,
      });

      if (response.status === 201) {
        toast.success("با موفقیت ثبت شد");
        router.push("./login");
      } else {
        toast.error("Registration failed");
      }
    } catch (error) {
      console.error(error);
      toast.error("Error during registration");
    }
  };

  return (
    <>
    <Toaster/>
    <div className="flex justify-center items-center h-screen">
      <div className="border-2 shadow-slate-700 shadow-md px-20 pb-10">
        <div className="flex flex-col -space-y-20 pb-20">
        <img src="./pic/Grocery.png" width={250}/>
        <h2 className="font-extrabold text-4xl">ثبت نام </h2>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
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
            <div className="relative w-64">
              <input
                type="password"
                id="floating-input"
                className="block w-full h-10 px-2.5 pt-5 pb-2 text-sm text-gray-900 bg-transparent border border-gray-300 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 peer"
                placeholder=" "
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <label
                htmlFor="floating-input"
                className="absolute text-sm text-gray-500 bg-white px-1 duration-300 transform top-[-10px] left-2 peer-placeholder-shown:top-2.5 peer-placeholder-shown:text-gray-400 peer-placeholder-shown:bg-transparent peer-focus:top-[-10px] peer-focus:text-blue-600 peer-focus:bg-white"
              >
                Confirm Password
              </label>
            </div>
            
          <button type="submit" className="bg-green-600 rounded-md h-10 text-white font-bold text-lg">ثبت نام</button>
          <a href="./login" className="text-center text-green-500">قبلا ثبت نام کرده اید؟</a>
        </form>
      </div>
    </div>
    </>
  );
}
