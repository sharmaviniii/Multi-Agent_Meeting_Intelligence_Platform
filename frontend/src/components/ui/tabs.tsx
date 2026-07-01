import {
  createContext,
  type HTMLAttributes,
  type KeyboardEvent,
  type ReactNode,
  useContext,
} from "react";

import { cn } from "@/lib/utils";

type TabsContextValue = {
  activeValue: string;
  onValueChange: (value: string) => void;
  values: string[];
};

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext() {
  const context = useContext(TabsContext);

  if (!context) {
    throw new Error("Tabs components must be rendered inside Tabs.");
  }

  return context;
}

type TabsProps = HTMLAttributes<HTMLDivElement> & {
  value: string;
  onValueChange: (value: string) => void;
  values: string[];
};

export function Tabs({ children, className, onValueChange, value, values, ...props }: TabsProps) {
  return (
    <TabsContext.Provider value={{ activeValue: value, onValueChange, values }}>
      <div className={cn("flex min-h-0 flex-1 flex-col", className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex gap-1 overflow-x-auto border-b border-border px-4 md:px-6",
        className,
      )}
      role="tablist"
      {...props}
    />
  );
}

type TabsTriggerProps = {
  children: ReactNode;
  controls: string;
  value: string;
};

export function TabsTrigger({ children, controls, value }: TabsTriggerProps) {
  const { activeValue, onValueChange, values } = useTabsContext();
  const isActive = value === activeValue;
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
      return;
    }

    event.preventDefault();
    const currentIndex = values.indexOf(activeValue);
    const lastIndex = values.length - 1;
    const nextIndex =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? lastIndex
          : event.key === "ArrowRight"
            ? (currentIndex + 1) % values.length
            : (currentIndex - 1 + values.length) % values.length;
    const nextValue = values[nextIndex];

    if (nextValue) {
      onValueChange(nextValue);
      window.requestAnimationFrame(() => {
        document.getElementById(`${nextValue}-tab`)?.focus();
      });
    }
  };

  return (
    <button
      aria-controls={controls}
      aria-selected={isActive}
      className={cn(
        "min-h-11 whitespace-nowrap border-b-2 border-transparent px-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        isActive && "border-primary text-foreground",
      )}
      id={`${value}-tab`}
      onKeyDown={handleKeyDown}
      onClick={() => onValueChange(value)}
      role="tab"
      tabIndex={isActive ? 0 : -1}
      type="button"
    >
      {children}
    </button>
  );
}

type TabsContentProps = HTMLAttributes<HTMLElement> & {
  labelledBy: string;
  value: string;
};

export function TabsContent({ children, className, labelledBy, value, ...props }: TabsContentProps) {
  const { activeValue } = useTabsContext();
  const isActive = value === activeValue;

  return (
    <section
      aria-labelledby={labelledBy}
      className={cn("min-h-0 flex-1", !isActive && "hidden", className)}
      hidden={!isActive}
      id={`${value}-panel`}
      role="tabpanel"
      tabIndex={0}
      {...props}
    >
      {children}
    </section>
  );
}
