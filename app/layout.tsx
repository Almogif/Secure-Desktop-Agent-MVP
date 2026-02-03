import "../styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Flow",
  description: "Quiet writing with inline AI suggestions"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="min-h-screen px-6 py-16">{children}</main>
      </body>
    </html>
  );
}
