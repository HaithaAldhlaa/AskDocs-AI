
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const navigationItems = [
    {
      label: "Chat",
      href: "/",
      icon: "\u2726",
    },
    {
      label: "RAG Documents",
      href: "/documents",
      icon: "\u25A4",
    },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">{"\u2726"}</div>
        <span>AskDocs AI</span>
      </div>

      <div className="sidebar-divider" />

      <nav className="sidebar-nav">
        <p className="sidebar-label">WORKSPACE</p>

        {navigationItems.map((item) => {
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${isActive ? "active" : ""}`}
              aria-current={isActive ? "page" : undefined}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span className="status-dot" />
        <span>AskDocsAI Workspace</span>
      </div>
    </aside>
  );
}
