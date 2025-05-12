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
import Expired from "@/components/template/Expired";
import InserCostumer from "@/components/template/insertCostumer";
import PopularProduct from "@/components/template/popularproduct";

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
    { label: "محصولات پر فروش", link: "/popularProduct" },
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
        { label: "محصولات پر فروش", link: "/popularProduct" },
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
        { label: "خروج", link: "/logout" },
      ]);
    } else if (icon === "charts") {
      setSelectedOption([
        { label: "چارت ها" },
        { label: " برآورد کارکرد ها", link: "/charts" },
        { label: "محصولات منقضی", link: "/expired" },
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
        { label: "افزودن مشتری جدید", link: "/inserCostumer" },
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
    } else if (link === "/expired") {
      setActiveContent(<Expired />);
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
    } else if (link === "/inserCostumer") {
      setActiveContent(<InserCostumer />);
    } else if (link === "/info") {
      setActiveContent(<Profile />);
    } else if (link === "/logout") {
      router.push("./login");
    } else if (link === "/calender") {
      setActiveContent(<Calendar />);
    } else if (link === "/sales") {
      setActiveContent(<TotalSale />);
    } else if (link === "/admin") {
      setActiveContent(<Admin />);
    }else if (link === "/popularProduct") {
      setActiveContent(<PopularProduct/>);
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
      <div className="min-h-screen sticky top-0 z-50 pt-5 shadow-md bg-purple-50 grid grid-cols-[30%,70%]">
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
      <div className="grid grid-cols-1">
        <div className="fixed top-0 bg-purple-50 shadow h-20 w-full z-30">
          <div className="flex">
            <div className="absolute w-[250px] h-[40px] right-10 top-5">
              <input
                type="text"
                value={searchValue}
                onChange={handleSearchChange}
                placeholder="جستجو..."
                className={`hidden sm:block form-input bg-gray-100 placeholder:tracking-widest ltr:pl-9 ltr:pr-9 rtl:pl-9 rtl:pr-11 py-2 rounded-md border sm:bg-transparent ltr:sm:pr-4 rtl:sm:pl-4 w-full focus:outline-none focus:border-purple-500`}
              />
              <IoSearch size={30} className="hidden sm:block absolute top-1/2 ltr:left-3 rtl:right-3 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>

            <IoPersonCircle
              size={50}
              className="absolute left-80 top-4 text-gray-500/40"
            />
          </div>
        </div>
        <div>
          <div className="text-xl m-5 mt-20 font-bold">{activeContent}</div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
