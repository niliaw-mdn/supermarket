import React, { useEffect, useState } from "react";
import Header from "@/components/Header";

function Index() {
  const [showHeader, setShowHeader] = useState(false);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === "Enter") {
        setShowHeader(true); 
      }
    };

    document.addEventListener("keydown", handleKeyPress);

    return () => {
      document.removeEventListener("keydown", handleKeyPress);
    };
  }, []);

  if (showHeader) {
    return <Header />;
  }

  return (
    <div
    className="flex justify-center items-center h-screen bg-cover bg-center"
    style={{
      backgroundImage: "url('./pic/bgmain.gif')",
    }}
  >
    <div className="text-center">
      <img src="./pic/main.png" width={600} alt="Main" />
      <h1 className="text-7xl mt-8 text-white font-bold">
        به فروشگاه ما خوش آمدید
      </h1>
    </div>
  </div>
  
  );
}

export default Index;