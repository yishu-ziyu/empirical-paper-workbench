import { KeyboardEvent, useEffect, useLayoutEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "../lib/cn";

export interface StageTab {
  id: string;
  label: string;
  hint: string;
  disabled?: boolean;
}

const DEFAULT_TABS: StageTab[] = [
  { id: "brief", label: "任务书", hint: "确认研究题目和边界" },
  { id: "recursive-search", label: "递归搜索", hint: "题目、变量、数据、文献互相追问" },
  { id: "variables", label: "数据变量", hint: "字段画像和变量角色候选" },
  { id: "design", label: "方法设计", hint: "识别策略和模型设定" },
  { id: "execution", label: "执行实验", hint: "运行、诊断、预检和草案" },
];

const DEFAULT_CURSOR_POSITION = { left: 5, width: 88, opacity: 1 };

interface SlideTabsProps {
  tabs?: StageTab[];
  value?: string;
  onChange?: (id: string) => void;
}

export function SlideTabs({ tabs = DEFAULT_TABS, value, onChange }: SlideTabsProps) {
  const [activeId, setActiveId] = useState(value || tabs[0]?.id || "");
  const [position, setPosition] = useState(DEFAULT_CURSOR_POSITION);
  const tabRefs = useRef<Record<string, HTMLButtonElement | null>>({});
  const active = tabs.find((tab) => tab.id === activeId) || tabs[0];

  useEffect(() => {
    if (value) setActiveId(value);
  }, [value]);

  function setCursorTo(id: string) {
    const node = tabRefs.current[id];
    if (!node) return;
    setPosition({ left: node.offsetLeft, width: node.offsetWidth, opacity: 1 });
  }

  useLayoutEffect(() => {
    setCursorTo(activeId);
    const frame = window.requestAnimationFrame(() => setCursorTo(activeId));
    return () => window.cancelAnimationFrame(frame);
  }, [activeId, tabs]);

  function returnActiveCursor() {
    setCursorTo(activeId);
  }

  function selectTab(id: string) {
    const target = tabs.find((tab) => tab.id === id);
    if (target?.disabled) {
      onChange?.(id);
      returnActiveCursor();
      return;
    }

    setActiveId(id);
    onChange?.(id);
    setCursorTo(id);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const nextIndex = (index + offset + tabs.length) % tabs.length;
    const next = tabs[nextIndex];
    if (next.disabled) {
      onChange?.(next.id);
      returnActiveCursor();
      return;
    }
    selectTab(next.id);
    tabRefs.current[next.id]?.focus();
  }

  return (
    <nav aria-label="研究阶段" className="slide-tabs-wrap">
      <div
        className="slide-tabs"
        onMouseLeave={() => {
          returnActiveCursor();
        }}
        role="tablist"
      >
        {tabs.map((tab, index) => (
          <button
            aria-disabled={tab.disabled ? "true" : undefined}
            aria-selected={tab.id === activeId}
            className={cn(
              "slide-tabs__tab",
              tab.id === activeId && "slide-tabs__tab--active",
              tab.disabled && "slide-tabs__tab--locked",
            )}
            key={tab.id}
            onClick={() => selectTab(tab.id)}
            onFocus={() => selectTab(tab.id)}
            onKeyDown={(event) => handleKeyDown(event, index)}
            onMouseEnter={(event) => {
              if (tab.disabled) return;
              setPosition({
                left: event.currentTarget.offsetLeft,
                width: event.currentTarget.offsetWidth,
                opacity: 1,
              });
            }}
            ref={(node) => {
              tabRefs.current[tab.id] = node;
            }}
            role="tab"
            type="button"
          >
            {tab.label}
          </button>
        ))}
        <motion.span
          animate={position}
          className="slide-tabs__cursor"
          initial={false}
          transition={{ type: "spring", stiffness: 420, damping: 34 }}
        />
      </div>
      <p className="slide-tabs__hint">{active?.hint}</p>
    </nav>
  );
}
