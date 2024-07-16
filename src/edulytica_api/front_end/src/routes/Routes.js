import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { useAuth } from "../provider/authProvider";
import { ProtectedRoute } from "./ProtectedRoute";
import LoginForm from "../components/LoginForm";
import Logout from "../components/Logout";
import LLMForm from "../components/LLMForms"
import Results from "../components/Results"
import Layout from "../components/Layout";
import DetailResult from "../components/DetailResult"
const Routes = () => {
    const { token } = useAuth();
  
    // Define public routes accessible to all users
    const routesForPublic = [
      {
        path: "/contact",
        element:<p>Contact</p>,
      },
      {
        path: "/about",
        element:<p>About</p>,
      },
    ];
  
    // Define routes accessible only to authenticated users
    const routesForAuthenticatedOnly = [
      {
        path: "/",
        element: <ProtectedRoute />, // Wrap the component in ProtectedRoute
        children: [
          {
            path: "/",
            element:<p>UserHome</p>,
          },
          {
            path: "/results",
            element: <Results url='http://localhost:8000/llm/results'/>,
          },
          {
            path: "/result",
            element: <DetailResult url='http://localhost:8000/llm/result'/>,
          },
          {
            path: "/purpose",
            element:<LLMForm url='http://localhost:8000/llm/purpose'/>,
          },
          {
            path: "/summarize",
            element:<LLMForm url='http://localhost:8000/llm/summary'/>,
          },
          {
            path: "/profile",
            element:<p>Profile</p>,
          },
          {
            path: "/logout",
            element:<Logout url='http://localhost:8000/logout'/>,
          },
        ],
      },
    ];
  
    // Define routes accessible only to non-authenticated users
    const routesForNotAuthenticatedOnly = [
      {
        path: "/",
        element:<p>HomePage</p>,
      },
      {
        path: "/login",
        element:<LoginForm url='http://localhost:8000/login'/>,
      },
    ];
  
    // Combine and conditionally include routes based on authentication status
    const router = createBrowserRouter([
      {
        element: <Layout />,
        children: [
          ...routesForPublic,
          ...(!token ? routesForNotAuthenticatedOnly : []),
          ...routesForAuthenticatedOnly,
        ]
      }
    ]
    );
  
    // Provide the router configuration using RouterProvider
    return <RouterProvider router={router}/>;
  };
  
  export default Routes;