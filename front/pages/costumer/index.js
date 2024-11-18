import React from 'react'

export default function () {
  return (
    <div className='flex justify-center'> <div className="w-[95%] h-[119px] relative">
    <div className="w-full h-[80px] left-0 top-[6px] absolute bg-[#3b6e28] rounded-[20px]"></div>
    <div className="absolute right-24 top-8 font-semibold text-lg text-white">
      <a style={{ cursor: "pointer" }}>
        اضافه کردن کالا جدید
      </a>
    </div>

    <img
      className="w-[100px] h-[80px] left-[9px] top-1 absolute"
      src="pic/logo.png"
      alt="Logo"
    />

  </div></div>
  )
}

