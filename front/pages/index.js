import Image from "next/image";
import localFont from "next/font/local";
import Header from "@/components/Header";
import Product from "@/components/template/Product";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export default function Home() {
  return <>
  <Header/>
  <Product/>
</>;
}