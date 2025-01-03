import React, { useState } from "react";
import { useRouter } from "next/router";
import { IoArrowBackOutline } from "react-icons/io5";
import toast, { Toaster } from "react-hot-toast";

function Index() {
  const router = useRouter();

  const backHandler = () => {
    router.push("./products");
  };

  const [unit, setUnit] = useState("kg");
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [file, setFile] = useState(null);

  
  const unitToUomId = {
    kg: 3, 
    number: 1, 
    liter: 7, 
    meter: 4, 
  };

  const handleUnitChange = (e) => {
    setUnit(e.target.value);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("price_per_unit", price);
    formData.append("available_quantity", quantity);
    formData.append("uom_id", unitToUomId[unit]);  
    formData.append("file", file); 

    
    try {
      const response = await fetch("http://localhost:5000/insertProduct", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (result.error) {
        toast.error(`Error: ${result.error}`);
      } else {
        toast.success("محصول با موفقیت درج شد.");
        
        setName("");
        setPrice("");
        setQuantity("");
        setFile(null);
      }
    } catch (error) {
      console.error("Error during product submission:", error);
      toast.error("An error occurred while submitting the product.");
    }
  };

  return (
    <>
     <Toaster/>
      <div className="flex justify-center">
        <div className="w-[95%] h-[119px] relative">
          <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
          <div className="absolute right-24 top-8 font-semibold text-lg text-white"></div>

          <img
            className="w-[100px] h-[80px] left-[9px] top-1 absolute"
            src="pic/logo.png"
            alt="Logo"
          />

          <IoArrowBackOutline
            className="absolute left-[-35px] top-7 text-gray-400 cursor-pointer"
            size={30}
            onClick={backHandler}
          />
        </div>
      </div>

      <div className="flex flex-col justify-center items-center">
        <div className="bg-gray-300 border-gray-500 shadow-lg h-auto w-[500px] rounded-lg px-12 ">
          <div className="mb-4 font-semibold pt-5 pl-56">
            مشخصات محصول را وارد کنید:
          </div>
          <form onSubmit={handleSubmit} className="w-full">
            <ul className="list-none">
              <li className="py-5">
                <input
                  className="h-8 w-72 rounded-md p-3"
                  placeholder="اسم محصول"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </li>
              <li className="py-5">
                <input
                  className="h-8 w-72 rounded-md p-3"
                  placeholder="قیمت"
                  type="text"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                />
              </li>
              <li className="py-5 flex items-center space-x-2 rtl:space-x-reverse">
                <input
                  className="h-8 w-40 rounded-md p-3 border border-gray-300"
                  placeholder="مقدار"
                  type="number"
                  step={unit === "kg" ? "0.1" : "1"}
                  min="0"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  required
                />
                <select
                  className="h-10 w-32 rounded-md p-2 border border-gray-300 bg-white"
                  value={unit}
                  onChange={handleUnitChange}
                >
                  <option value="kg">کیلوگرم</option>
                  <option value="number">عدد</option>
                  <option value="liter">لیتر</option>
                  <option value="meter">متر</option>
                </select>
              </li>
              <li>
                <label
                  className="block mb-2 text-sm font-medium text-gray-900"
                  htmlFor="file_input"
                >
                  عکس محصول:
                </label>
                <input
                  className="block w-full text-sm text-gray-900 border border-gray-500 rounded-lg cursor-pointer bg-gray-400 placeholder-gray-400"
                  id="file_input"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  required
                />
              </li>
              <li className="m-10 ml-10 bg-[#0f8515] text-center pt-1 rounded-md h-10">
                <button type="submit" className="text-white font-bold text-lg">
                  تایید
                </button>
              </li>
            </ul>
          </form>
        </div>
      </div>
    </>
  );
}

export default Index;
