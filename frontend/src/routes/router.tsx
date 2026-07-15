//import { createBrowserRouter } from "react-router";

//export const router = createBrowserRouter([
 // {
  //  path: "/",
    //lazy: () => import("@/routes/root-route"),
  //},
//]);
import { createBrowserRouter } from "react-router";
import LandingPage from "@/LandingPage";
import NotFound from "./NotFound";
import { MeetingShell } from "@/app/meeting-shell";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/app",
    element: <MeetingShell />,
  },
  {
    path: "*",
    element: <NotFound />,
}
]);