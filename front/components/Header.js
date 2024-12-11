import React from "react";
import Link from "next/link";
import Image from "next/image";
import { useState , useRef , useEffect } from "react";
import Product from "./template/Product";

import { TbMenuDeep } from "react-icons/tb";
import { IoPersonCircleSharp } from "react-icons/io5";
import { IoCloseSharp } from "react-icons/io5";

function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);


  const transitionMenu = (open) => {
    const menu = menuRef.current;
    let opacity = open ? 0 : 1;
    let transform = open ? 100 : 0;
    const duration = 500;
    const start = performance.now();

    const animate = (time) => {
      const elapsed = time - start;
      const progress = Math.min(elapsed / duration, 1);

      opacity = open ? progress : 1 - progress;
      transform = open ? 100 - progress * 100 : progress * 100;

      menu.style.opacity = opacity;
      menu.style.transform = `translateX(${transform}%)`;

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        if (!open) menu.style.display = "none"; 
      }
    };

    if (open) {
      menu.style.display = "block";
    }

    requestAnimationFrame(animate);
  };

  useEffect(() => {
    if (isOpen) {
      transitionMenu(true);
    } else {
      transitionMenu(false);
    }
  }, [isOpen]);


  const getDrawerPosition = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      return {
        top: rect.top + window.scrollY, 
        left: rect.left + window.scrollX, 
      };
    }
    return { top: 0, left: 0 };
  };


  return (
    <div className="flex justify-center flex-col">
      <div className="w-[95%] h-[119px] relative ">
        <div className="w-full h-[80px] right-10 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
        <div className="w-[131px] h-[50px] left-[150px] top-6 absolute text-white text-[25px] font-semibold">
          Total
        </div>
        
        <div className="w-[131px] h-[50px] left-[230px] top-6 absolute text-white text-[25px] font-semibold">
          Reset
        </div>
        <img
          className="w-[100px] h-[80px] left-[9px] top-1  absolute"
          src="pic/logo.png"
        />
        <div className="relative z-50 right-10">
          {!isOpen && (
            <TbMenuDeep onClick={() => setIsOpen(true)} className="h-14 w-20 mt-[17px] text-white cursor-pointer" />
          )}

          <div
            ref={menuRef}
            className="fixed bg-white text-gray shadow-lg rounded-lg w-64 h-[1000px] right-[-2px] top-0"
            style={{
              transform: "translateX(100%)",
              opacity: 0,
              display: "none",
            }}
          >
            <div className="flex flex-row gap-40 p-3">
              <div>
                <Link href="/">
                  <Image
                    src="/pic/logo.png"
                    alt="logo"
                    width={29}
                    height={33}
                    className="w-[35px] h-[40px]"
                  />
                </Link>
              </div>

              <div>
                <IoCloseSharp
                  onClick={() => setIsOpen(false)}
                  className="h-10 w-8 pb-2 text-gray-500"
                />
              </div>
            </div>

            <nav>
              <ul className="w-[90%] divide-y divide-gray-300 pr-10">
                <li className="p-6">
                  <a href="./">صفحه اصلی</a>
                </li>
                <li className="p-6">
                  <a href="./profile">پروفایل</a>
                </li>
                <li className="p-6">
                  <a href="/products">محصولات</a>
                </li>
                <li className="p-6">
                  <a href="/staff">کارکنان</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
      <Product/>
    </div>
  );
}

export default Header;
