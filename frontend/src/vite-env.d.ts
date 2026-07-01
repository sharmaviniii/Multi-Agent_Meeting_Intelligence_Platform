/// <reference types="vite/client" />

import type { SVGProps } from "react";

declare module "react" {
  interface ReactSVG {
    [elementName: string]: SVGProps<SVGSVGElement>;
  }
}

declare module "*.css";
