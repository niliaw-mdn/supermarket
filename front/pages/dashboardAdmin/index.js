import React, { useState, useEffect } from "react";
import { MdDashboard } from "react-icons/md";
import { FaChartPie } from "react-icons/fa";
import { IoIosApps } from "react-icons/io";
import { HiShoppingBag } from "react-icons/hi2";
import { IoPeople } from "react-icons/io5";
import { IoPersonCircle } from "react-icons/io5";
import { LuFileSliders } from "react-icons/lu";
import Allproduct from "@/components/template/Allproduct";
import AddItem from "@/components/template/addItem";
import Performance from "@/components/template/performance";
import { IoSearch } from "react-icons/io5";
import { useRouter } from "next/router";
import Calendar from "@/components/template/calender";
import TotalSale from "@/components/template/totalsale";
import Profile from "@/components/template/profile";
import Admin from "@/components/template/admin";

function Sidebar() {
  const router = useRouter();
  const [searchValue, setSearchValue] = useState("");
  const [activeIcons, setActiveIcons] = useState({
    dashboard: true,
    application: false,
    charts: false,
    product: false,
    costumer: false,
    profile: false,
    pages: false,
  });

  const handleSearchChange = (e) => {
    setSearchValue(e.target.value);
  };

  const [selectedOption, setSelectedOption] = useState([
    { label: "داشبورد" },
    { label: "فروش کل", link: "/sales" },
    { label: "محصولات پر فروش", link: "/categories" },
  ]);

  const [activeContent, setActiveContent] = useState(<Performance />);

  const menuHandler = (icon) => {
    setActiveIcons((prevState) => ({
      ...prevState,
      dashboard: false,
      application: false,
      charts: false,
      product: false,
      costumer: false,
      pages: false,
      profile: false,
      [icon]: !prevState[icon],
    }));

    if (icon === "dashboard") {
      setSelectedOption([
        { label: "داشبورد" },
        { label: "فروش کل", link: "/sales" },
        { label: "محصولات پر فروش", link: "/categories" },
      ]);
    } else if (icon === "application") {
      setSelectedOption([
        { label: "برنامه های کاربردی" },
        { label: "تقویم", link: "/calender" },
      ]);
    } else if (icon === "profile") {
      setSelectedOption([
        { label: "پروفایل شما" },
        { label: "اطلاعات فردی", link: "/info" },
        { label: "کارکرد شما", link: "/admin" },
        { label: "خروج" , link: "/logout"},
      ]);
    } else if (icon === "charts") {
      setSelectedOption([
        { label: "چارت ها" },
        { label: " برآورد کارکرد ها", link: "/charts" },
      ]);
    } else if (icon === "product") {
      setSelectedOption([
        { label: "محصولات" },
        { label: "موجودی ها", link: "/supply" },
        { label: "اضافه کردن کالا جدید", link: "/additem" },
      ]);
    } else if (icon === "costumer") {
      setSelectedOption([
        { label: "مشتریان" },
        { label: "اطلاعات مشتریان", link: "/costumer" },
      ]);
    } else if (icon === "pages") {
      setSelectedOption([
        { label: "صفحات" },
        { label: "صفحه اصلی", link: "/mainpage" },
        { label: "صفحه عضویت", link: "/register" },
        { label: "صفحه ورود", link: "/login" },
        { label: "داشبورد ادمین", link: "/dashboard" },
        { label: "خروج", link: "/logout" },
      ]);
    }
  };
  useEffect(() => {
    const isProductInventoryActive = selectedOption.some(
      (option) => option.label === "موجودی ها" && option.link === "/supply"
    );

    if (isProductInventoryActive) {
      setActiveContent(
        <Allproduct key={searchValue} searchQuery={searchValue} />
      );
    }
  }, [selectedOption, searchValue]);

  const clickHandler = (link) => {
    if (link === "/dashboard") {
      setActiveContent(<Product />);
    } else if (link === "/charts") {
      setActiveContent(<Performance />);
    } else if (link === "/supply") {
      setActiveIcons((prevState) => ({
        ...prevState,
        product: true,
      }));
      setActiveContent(<Allproduct searchQuery={searchValue} />);
    } else if (link === "/additem") {
      setActiveContent(<AddItem />);
    } else if (link === "/mainpage") {
      setActiveContent(<Product />);
    } else if (link === "/info") {
      setActiveContent(<Profile/>);
    } else if (link === "/logout") {
      router.push("./login");
    } else if (link === "/calender") {
      setActiveContent(<Calendar />);
    } else if (link === "/sales") {
      setActiveContent(<TotalSale />);
    } else if (link === "/admin") {
      setActiveContent(<Admin />);
    } else if (link === "/register") {
      router.push("./login");
    } else if (link === "/login") {
      router.push("./register");
    } else if (link === "/dashboard") {
      router.push("./dashboardAdmin");
    } else if (link === "/logout") {
      router.push("./");
    } else {
      setActiveContent("Content Not Found");
    }
  };

  return (
    <div className="grid grid-cols-[16%,84%]">
      <div
        className="bg-[#57c4f5]"
        style={{
            backgroundImage: `
      linear-gradient(to bottom, rgba(241, 245, 249, 0), rgba(255,255,255,1)90%),
      linear-gradient(to right, rgba(87,196,245,1), rgba(87,196,245,1))
    `,
          }}
      >
        <div className="h-screen sticky -top-3 mt-10 rounded-se-2xl bg-purple-50 grid grid-cols-[30%,70%]">
          <div className="flex flex-col pt-5 items-center space-y-8 border-l-2 border-dashed">
            <img src="./pic/logo.png" width={50} alt="Logo" />

            <div className="relative group">
              <MdDashboard
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.dashboard
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("dashboard")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                داشبورد
              </span>
            </div>

            <div className="relative group">
              <HiShoppingBag
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.product
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("product")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                محصولات
              </span>
            </div>

            <div className="relative group">
              <IoPersonCircle
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.profile
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("profile")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                پروفایل‌من
              </span>
            </div>

            <div className="relative group">
              <IoIosApps
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.application
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("application")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                برنامه‌ها
              </span>
            </div>

            <div className="relative group">
              <FaChartPie
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.charts
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("charts")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                چارت‌ها
              </span>
            </div>

            <div className="relative group">
              <IoPeople
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.costumer
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("costumer")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                مشتریان
              </span>
            </div>

            <div className="relative group">
              <LuFileSliders
                size={40}
                className={`text-gray-400 p-1 transition-all duration-200 ${
                  activeIcons.pages
                    ? "bg-purple-200 scale-110 rounded-md text-violet-500"
                    : "hover:bg-purple-200 hover:scale-110 rounded-md hover:text-[#846cf9]"
                }`}
                onClick={() => menuHandler("pages")}
              />
              <span className="absolute top-1 right-3 -translate-x-1/2 mb-1 hidden group-hover:block bg-[#846cf9] text-white text-sm rounded-md px-2 py-1">
                صفحات
              </span>
            </div>
          </div>

          <div className="flex flex-col items-start  font-semibold text-gray-400  space-y-4 pr-5">
            {selectedOption.map((option, index) => (
              <div
                key={index}
                tabIndex={index !== 0 ? 0 : -1}
                className={`cursor-pointer ${
                  index === 0
                    ? "text-black font-bold text-2xl pt-5 pointer-events-none"
                    : "text-gray-400 focus:bg-violet-500 p-1 text-lg  rounded-md w-[90%] focus:text-white transition-all duration-200"
                }`}
                onClick={() => {
                  if (index !== 0) clickHandler(option.link);
                }}
              >
                {option.label}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1">
        <div
          className="h-44 w-full"
          style={{
            backgroundImage: `
      linear-gradient(to bottom, rgba(241, 245, 249, 0), rgba(226,232,240,1)90%),
      linear-gradient(to right, rgba(37, 33, 158, 1), rgba(56,189,248,1))
    `,
          }}
        >
          <div className="relative w-[250px] h-[40px] right-24 top-3">
            <IoSearch
              className="absolute text-gray-500 text-[20px] bg-white h-full rounded-ss-xl rounded-es-xl pr-3 top-1/2 left-[250px] transform -translate-y-1/2"
              size={40}
            />
            <input
              className="pr-3 w-full h-full bg-white border-none rounded-ee-xl rounded-se-xl outline-none text-gray-500 text-[18px]"
              placeholder="جستجو"
              value={searchValue}
              onChange={handleSearchChange}
            />
          </div>

          <div className="flex justify-end p-5 mt-[-53px]">
            <IoPersonCircle size={50} className="text-white" />
          </div>
        </div>
        <div>
          <div className="text-xl font-bold">{activeContent}</div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
