import { useState, useEffect } from "react";

import { Mail } from "@/components/mail";
import { MobileMail } from "@/components/MobileMail";
import { accounts, mails } from "@/test/data";
import { emailService } from "@/services/api";

const MailPage = () => {
  const [defaultLayout, setDefaultLayout] = useState();
  const [defaultCollapsed, setDefaultCollapsed] = useState();
  const [loading, setLoading] = useState(true);
  const [newMails, setMails] = useState([]);

  useEffect(() => {
    const fetchInitialState = async () => {
      try {
        // Load layout settings first
        const layout = localStorage.getItem("react-resizable-panels:layout:mail");
        const collapsed = localStorage.getItem("react-resizable-panels:collapsed");
        
        setDefaultLayout(layout ? JSON.parse(layout) : undefined);
        setDefaultCollapsed(collapsed ? JSON.parse(collapsed) : undefined);

        // Then fetch emails
        const response = await emailService.getRawEmails();
        // setMails(response);
        console.log(response);
        setMails(response);
      } catch (error) {
        console.error("Initialization error:", error);
      } finally {
        setLoading(false);
      }
    };
    
    setMails(newMails);
    fetchInitialState();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <>
      <div className="hidden flex-col md:flex">
        <Mail
          accounts={accounts}
          mails={newMails}
          defaultLayout={defaultLayout}
          defaultCollapsed={defaultCollapsed}
          navCollapsedSize={4}
        />
      </div>
      <div className="flex flex-col md:hidden">
        <MobileMail
          accounts={accounts}
          mails={newMails}
          defaultLayout={defaultLayout}
          defaultCollapsed={defaultCollapsed}
          navCollapsedSize={4}
        />
      </div>
    </>
  );
}

export default MailPage;