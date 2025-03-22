import { useState, useEffect } from "react";

import { Mail } from "@/components/mail";
import { accounts, mails } from "@/test/data";

export default function MailPage() {
  const [defaultLayout, setDefaultLayout] = useState();
  const [defaultCollapsed, setDefaultCollapsed] = useState();

  useEffect(() => {
    const layout = localStorage.getItem("react-resizable-panels:layout:mail");
    const collapsed = localStorage.getItem("react-resizable-panels:collapsed");
    
    if (layout) setDefaultLayout(JSON.parse(layout));
    if (collapsed) setDefaultCollapsed(JSON.parse(collapsed));
  }, []);

  return (
    <>
      <div className="md:hidden">
        <img
          src="/examples/mail-dark.png"
          width={1280}
          height={727}
          alt="Mail"
          className="hidden dark:block"
        />
        <img
          src="/examples/mail-light.png"
          width={1280}
          height={727}
          alt="Mail"
          className="block dark:hidden"
        />
      </div>
      <div className="hidden flex-col md:flex">
        <Mail
          accounts={accounts}
          mails={mails}
          defaultLayout={defaultLayout}
          defaultCollapsed={defaultCollapsed}
          navCollapsedSize={4}
        />
      </div>
    </>
  );
}
