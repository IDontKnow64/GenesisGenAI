"use client";

import * as React from "react";
import { useState } from "react";
import * as lu from "react-icons/lu";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TooltipProvider } from "@/components/ui/tooltip";
import { MailDisplay } from "@/components/mail-display";
import { MailList } from "@/components/mail-list";
import { Nav } from "@/components/nav";
import { type Mail } from "@/test/data";
import { type LucideIcon, Search } from "lucide-react";
import { useMail } from "@/test/use-mail";
import { Button } from "@/components/ui/button";

interface MailProps {
  accounts: {
    label: string;
    email: string;
    icon: React.ReactNode;
  }[];
  mails: Mail[];
  defaultLayout: number[] | undefined;
  defaultCollapsed?: boolean;
  navCollapsedSize: number;
}

export function Mail({
  accounts,
  mails,
  defaultLayout = [20, 32, 48],
  defaultCollapsed = false,
  navCollapsedSize,
}: MailProps) {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);
  const [mail] = useMail();
  const [folders, setFolders] = useState([
    {
      title: "Inbox",
      label: "128",
      icon: lu.LuInbox as LucideIcon,
      category: "Work",
      variant: "default",
    },
    {
      title: "Junk",
      label: "23",
      icon: lu.LuArchiveX as LucideIcon,
      category: "All",
      variant: "ghost",
    },
    {
      title: "Trash",
      label: "",
      icon: lu.LuTrash2 as LucideIcon,
      category: "All",
      variant: "ghost",
    },
  ]);
  const [categories, setCategories] = useState([
    "All",
    "Work",
  ]);

  const moveUp = (category: string) => {
    const currentIndex = categories.findIndex((cat) => cat === category);
    if (currentIndex > 0) {
      const temp = categories[currentIndex];
      categories[currentIndex] = categories[currentIndex - 1];
      categories[currentIndex - 1] = temp;
      setFolders([...folders]);
    }
  };
  const moveDown = (category: string) => {
    const currentIndex = categories.findIndex((cat) => cat === category);
    if (currentIndex < categories.length - 1) {
      const temp = categories[currentIndex];
      categories[currentIndex] = categories[currentIndex + 1];
      categories[currentIndex + 1] = temp;
      setFolders([...folders]);
    }
  };

  const addFolder = () => {
    const newFolder = {
      title: "New Folder",
      label: "",
      icon: lu.LuFolderOpen as LucideIcon,
      category: "All",
      variant: "ghost",
    };
    setFolders([...folders, newFolder]);
  };

  const addCategory = () => {
    const newCategory = "Other";
    setCategories([...categories, newCategory]);
  };

  return (
    <TooltipProvider delayDuration={0}>
      <ResizablePanelGroup
        direction="horizontal"
        onLayout={(sizes: number[]) => {
          document.cookie = `react-resizable-panels:layout:mail=${JSON.stringify(
            sizes
          )}`;
        }}
        className="h-screen"
      >
        <ResizablePanel
          defaultSize={defaultLayout[0]}
          collapsedSize={navCollapsedSize}
          collapsible={true}
          minSize={15}
          maxSize={20}
          onCollapse={() => {
            setIsCollapsed(true);
            document.cookie = `react-resizable-panels:collapsed=${JSON.stringify(
              true
            )}`;
          }}
          onResize={() => {
            setIsCollapsed(false);
            document.cookie = `react-resizable-panels:collapsed=${JSON.stringify(
              false
            )}`;
          }}
          className={cn(
            "flex flex-col justify-between h-screen min-w-[50px] transition-all duration-300 ease-in-out"
          )}
        >
          <div>
          <div className="pt-[28px]"/>
          {categories.map((category) => (
            <div className="category-item">
              <span className="pr-3 flex justify-between">
                <text className="pl-5 category-title">{isCollapsed ? "" : category}</text>
                <span className="flex gap-0">
                {!isCollapsed && (
                  <div>
                    <Button onClick={() => moveDown(category)} className="size-1 bg-white shadow-none hover:bg-gray-100">
                      <lu.LuArrowDown color="black"/>
                    </Button>
                    <Button onClick={() => moveUp(category)} className="size-1 bg-white shadow-none hover:bg-gray-100">
                      <lu.LuArrowUp color="black"/>
                    </Button>
                  </div>
                )}
                </span>
              </span>
              <Separator />
              
              <Nav
                isCollapsed={isCollapsed}
                links={folders.map((folder) => ({
                  title: folder.title,
                  label: folder.label,
                  icon: folder.icon,
                  variant: folder.variant as "default" | "ghost",
                  category: folder.category,
                })).filter((folder) => folder.category === category)}
              />

            </div>
          ))}
          </div>
          <div className="flex flex-col gap-2 px-2 pb-2 sticky bottom-0 bg-background ">
            <Button onClick={addCategory} variant={"secondary"} className= {`text-black shadow-none hover:bg-gray-200 bottom-10 ${isCollapsed ? "size-9" : "w-full"}`}>{!isCollapsed ? "add category" : <lu.LuListPlus/>}</Button>
            <Button onClick={addFolder} variant={"secondary"} className= {`text-black shadow-none hover:bg-gray-200 bottom-10 ${isCollapsed ? "size-9" : "w-full"}`}>{!isCollapsed ? "add folder" : <lu.LuBookPlus/>}</Button>
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel 
          defaultSize={defaultLayout[1]} 
          minSize={30}
          className="flex flex-col overflow-hidden" // Added overflow control
        >
          <Tabs defaultValue="all" className="h-full flex flex-col">
            <div className="flex items-center px-4 py-2">
              <h1 className="text-xl font-bold">Inbox</h1>
              <TabsList className="ml-auto">
                <TabsTrigger
                  value="all"
                  className="text-zinc-600 dark:text-zinc-200"
                >
                  All mail
                </TabsTrigger>
                <TabsTrigger
                  value="unread"
                  className="text-zinc-600 dark:text-zinc-200"
                >
                  Unread
                </TabsTrigger>
              </TabsList>
            </div>
            <Separator />
            <div className="flex-1 overflow-y-auto">
              <div className="bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                  <form>
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="Search" className="pl-8" />
                    </div>
                  </form>
                </div>
              </div>
              <TabsContent value="all" className="m-0 h-full">
                <MailList items={mails} />
              </TabsContent>
              <TabsContent value="unread" className="m-0 h-full">
                <MailList items={mails.filter((item) => !item.read)} />
              </TabsContent>
            </div>
          </Tabs>
        </ResizablePanel>
        
        <ResizableHandle withHandle />

        <ResizablePanel 
          defaultSize={defaultLayout[2]} 
          minSize={30}
          className="flex flex-col overflow-hidden" // Added overflow control
        >
          <MailDisplay
            mail={mails.find((item) => item.id === mail.selected) || null}
          />
        </ResizablePanel>
      </ResizablePanelGroup>
    </TooltipProvider>
  );
}
