import React, { useRef } from "react";
import Webcam from "react-webcam";
import Image from "next/image";

function Product() {
  const webcamRef = useRef(null);

  return (
    <>
      <div className="w-full flex justify-center mt-10">
        <div className="w-[90%] h-[1100px] bg-[#c6d0c4] rounded-[10px] flex  justify-between relative">
          <div>
            <div className="w-[264px] h-[41px] text-white text-[32px] font-semibold flex flex-col absolute top-10 right-3">
              محصول مورد نظر:
            </div>
            <Webcam
              audio={false}
              ref={webcamRef}
              className="w-[800px] h-[700px] object-cover rounded-md absolute top-28 right-10"
            />
          </div>

          <div className="relative m-28">
            <table className="w-full text-sm text-left  text-gray-500">
              <thead className="text-xs text-white uppercase bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3">
                    اسم محصول
                  </th>
                  <th scope="col" className="px-6 py-3">
                    تعداد
                  </th>
                  <th scope="col" className="px-6 py-3">
                    قیمت
                  </th>
                  <th scope="col" className="px-6 py-3">
                    تصویر
                  </th>
                  <th scope="col" className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-white border-b  hover:bg-gray-50 ">
                  <td className="px-10 py-4 font-semibold text-gray-900 ">
                    سیب
                  </td>
                  <td className="px-5 py-4">
                    <input
                      type="number"
                      className="bg-gray-50 w-14 border border-gray-300 text-gray-900 text-sm rounded-lg block px-2.5 py-1"
                      placeholder="1"
                      required
                    />
                  </td>
                  <td className="px-5 py-4 font-semibold text-gray-900 ">
                    100تومان
                  </td>
                  <td className="py-4 px-1">
                    <Image src="/pic/apple-93.png" width={70} height={70} />
                  </td>
                  <td className="px-6 py-4">
                    <a
                      href="#"
                      className="font-medium text-red-600 dark:text-red-500 hover:underline"
                    >
                      حذف
                    </a>
                  </td>
                </tr>
                <tr className="bg-white border-b  hover:bg-gray-50 ">
                  <td className="px-3 py-4">
                    <a className="font-semibold text-gray-900 border-2 border-black p-2">
                      live total
                    </a>
                  </td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>

          <Image
            src="/pic/bg.png"
            width={1000}
            height={150}
            className="bottom-0 left-0 absolute"
          />
        </div>
      </div>
    </>
  );
}

export default Product;
