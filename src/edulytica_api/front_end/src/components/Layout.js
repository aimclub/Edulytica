import { Outlet } from "react-router-dom"

import Header from "../components/Header";
// import Header from "./Header"
// import Footer from "./Footer"

export default function Layout() {
    return (
        <>
            <Header />
            <main>                
                <Outlet />
            </main>
            {/* <Footer /> */}
        </>
    )
}