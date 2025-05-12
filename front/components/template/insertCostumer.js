import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/router";
import DatePicker from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import toast, { Toaster } from "react-hot-toast";
import { CiCalendar } from "react-icons/ci";


export default function InserCostumer() {
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [membershipDate, setMembershipDate] = useState("");
  const [numberOfPurchases, setNumberOfPurchases] = useState("");
  const [total, setTotal] = useState("");
  const [file, setFile] = useState(null);

  const router = useRouter();

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file) {
      toast.error("لطفا یک تصویر انتخاب کنید");
      return;
    }

    const formData = new FormData();
    formData.append("customer_name", customerName);
    formData.append("customer_phone", customerPhone);
    formData.append("membership_date", membershipDate);
    formData.append("number_of_purchases", numberOfPurchases);
    formData.append("total", total);
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://localhost:5000/insertCustomer",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (response.status === 201) {
        toast.success("با موفقیت ثبت شد");
        router.push("./login");
      } else {
        toast.error("ثبت‌نام انجام نشد");
      }
    } catch (error) {
      console.error(error);
      toast.error("خطا هنگام ثبت‌نام");
    }
  };

  return (
    <>
      <Toaster />
      <div className="flex h-screen">
        <div className="px-20 pb-10">
          <div className="flex flex-col -space-y-20 pb-20">
            <img src="./pic/Grocery.png" width={250} />
            <h2 className="font-extrabold text-4xl">ثبت نام مشتری</h2>
          </div>
          <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
            <input
              type="text"
              placeholder="نام"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              className="border p-2 rounded"
              required
            />
            <input
              type="text"
              placeholder="شماره تماس"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              className="border p-2 rounded"
              required
            />
            <div className="relative">
              <DatePicker
                calendar={persian}
                locale={persian_fa}
                value={membershipDate}
                onChange={(date) =>
                  setMembershipDate(date?.format("YYYY-MM-DD"))
                }
                containerClassName="w-full"
                inputClass="w-full border p-2 rounded pr-10"
                format="YYYY/MM/DD"
                placeholder="تاریخ عضویت"
              />
              <CiCalendar  className="absolute right-2 top-2.5 w-5 h-5 text-gray-500 pointer-events-none" />
            </div>

            <input
              type="number"
              placeholder="تعداد خریدها"
              value={numberOfPurchases}
              onChange={(e) => setNumberOfPurchases(e.target.value)}
              className="border p-2 rounded"
            />
            <input
              type="number"
              placeholder="مجموع پرداختی"
              value={total}
              onChange={(e) => setTotal(e.target.value)}
              className="border p-2 rounded"
            />
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
              className="border p-2 rounded"
              required
            />
            <button
              type="submit"
              className="bg-green-600 rounded-md h-10 text-white font-bold text-lg"
            >
              ثبت نام
            </button>
            <a href="./login" className="text-center text-green-500">
              قبلا ثبت نام کرده‌اید؟
            </a>
          </form>
        </div>
      </div>
    </>
  );
}
