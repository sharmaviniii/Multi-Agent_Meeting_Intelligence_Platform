import { RouterProvider } from "react-router";

import { QueryProvider } from "@/app/query-provider";
import { router } from "@/routes/router";

export function App() {
  return (
    <QueryProvider>
      <RouterProvider router={router} />
    </QueryProvider>
  );
}
