import { format } from "date-fns/format"
import {
  ArchiveX,
  Trash2,
} from "lucide-react"

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Mail } from "@/test/data"
import CircleChart from "@/components/CircleChart"
import { useEffect, useState } from "react"
import { emailService } from "@/services/api"
interface MailDisplayProps {
  mail: Mail | null
}

export function MailDisplay({ mail }: MailDisplayProps) {
  const [summaryText, setSummaryText] = useState("")
  const [scoreText, setScore] = useState("")
  const [reasonsList, setReasons] = useState([""])
  const [typeText, setType] = useState("")
  const today = new Date()

  const summarizeCurrent = async (message_id: string | undefined) => {
    if (message_id) {
      try {
        const result = await emailService.summarizeEmail(message_id);
        console.log('Email:', result.email);
        console.log('Summary:', result.summary);
        setSummaryText(result.summary);
      } catch (error) {
        console.log("Error summarizing")
      }
    }
  }
  const measureScam = async (message_id: string) => {
    try {
      const result = await emailService.scanEmail(message_id);
      console.log('Email:', result.email);
      console.log('Type:', result.type);
      console.log('Email:', result.reasons);
      console.log('Score:', result.score);
      setScore(result.score)
      setReasons(result.reasons)
      setType(result.type)
    } catch (error) {
      console.log("Error Scanning")
      console.log(error)
    }
  }

  useEffect(() => {
    setSummaryText("")
  }, [mail])

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center p-2">
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" disabled={!mail}>
                <ArchiveX className="h-4 w-4" />
                <span className="sr-only">Move to junk</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Move to junk</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" disabled={!mail}>
                <Trash2 className="h-4 w-4" />
                <span className="sr-only">Move to trash</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Move to trash</TooltipContent>
          </Tooltip>
          <Separator orientation="vertical" className="mx-1 h-6" />
        </div>
        <div>
        <div className="flex items-center gap-2">

        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              onClick={() => summarizeCurrent(mail?.id)} 
              variant="outline" 
              disabled={!mail}>
              Summarize!
            </Button>
          </TooltipTrigger>
          <TooltipContent>Summarize</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              onClick={() => mail?.id && measureScam(mail.id)} 
              variant="outline"
              disabled={!mail}>
              Scan!
            </Button>
          </TooltipTrigger>
          <TooltipContent>Scan!</TooltipContent>
        </Tooltip>
        </div>

        </div>
        <div className="ml-auto flex items-center gap-2"/>
        <Separator orientation="vertical" className="mx-2 h-6" />
      </div>
      <Separator />
      {mail ? (
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
          <div className="flex items-start p-4">
            <div className="flex items-start gap-4 text-sm">
              <Avatar>
                <AvatarImage alt={mail.name} />
                <AvatarFallback>
                  {mail.name
                    .split(" ")
                    .map((chunk) => chunk[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div className="grid gap-1">
                <div className="font-semibold">{mail.name}</div>
                <div className="line-clamp-1 text-xs">{mail.subject}</div>
                <div className="line-clamp-1 text-xs">
                  <span className="font-medium">Reply-To:</span> {mail.email}
                </div>
              </div>
            </div>
            {mail.date && (
              <div className="ml-auto text-xs text-muted-foreground">
                {format(new Date(mail.date), "PPpp")}
              </div>
            )}
          </div>
          <Separator />
          <CircleChart msg_id={mail.id} description={summaryText} score={scoreText} reasons={reasonsList} type={typeText}/>
          <div className="whitespace-pre-wrap p-4 text-sm">
            {mail.text}
          </div>
          <Separator className="mt-auto" />

          </div>
        </div>
      ) : (
        <div className="p-8 text-center text-muted-foreground">
          No message selected
        </div>
      )}
    </div>
  )
}
